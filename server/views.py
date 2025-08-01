from functools import wraps
from datetime import datetime, timedelta

from django.views.decorators.http import require_GET, require_POST
from django.http.response import JsonResponse, HttpResponse
from django.db import transaction
from django.conf import settings
from django.core.management import call_command
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import AbstractUser
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import ensure_csrf_cookie
from datetime import timezone
import json
import base64
import uuid
import traceback
import io
import random

import typing as T

from importlib import import_module

from .models import Poll, PollOption, Ballot, SessionMerge
from .limits import *
from .serializers import NewPollSerializer, SubmitVoteSerializer, UpdatePollSerializer, ClosePollSerializer, AuthLoginSerializer, SessionMergeSerializer
from .errors import *
from .cleanup import do_poll_cleanup
from .session_backend import no_flushing_section

if T.TYPE_CHECKING:
    from .session_backend import SessionStore
else:
    SessionStore = import_module(settings.SESSION_ENGINE).SessionStore


def handle_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            res = f(*args, **kwargs)
            if isinstance(res, dict):
                return JsonResponse({'status': 'OK', **res})
            return res
        except Exception as e:
            code = e.code if isinstance(e, BackendError) else 'UNKNOWN_ERROR'
            extra_data = e.extra_data if isinstance(e, BackendError) else {}
            if not isinstance(e, BackendError):
                traceback.print_exc()
            return JsonResponse({
                'status': 'error',
                'msg': str(e),
                'code': code,
                **extra_data
            }, status=500)

    return wrapper

last_db_clean: datetime | None = None

def refresh_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if settings.JWDJ_SESSION_CLEAN_INTERVAL > 0:
            global last_db_clean
            delta = timedelta(days=settings.JWDJ_SESSION_CLEAN_INTERVAL)
            now = datetime.now()
            if last_db_clean is None or now - last_db_clean > delta:
                call_command('clearsessions')
                last_db_clean = now
        if not request.session.session_key:
            request.session.save()
        request.session.modified = True
        return f(request, *args, **kwargs)
    return wrapper

def _user_data(request) -> dict[str]:
    user: AbstractUser = request.user
    authorised = user.is_authenticated and not user.is_anonymous
    return {
        'authorised': authorised,
        'authorisation_enabled': settings.JWDJ_LOGIN_MANAGER,
        'user': {
            'username': user.get_username(),
            'name': user.get_full_name(),
            'email': user.email,
        } if authorised else None,
    }

@require_GET
@refresh_session
@ensure_csrf_cookie
@handle_exception
def auth_is_authorised(request) -> dict[str]:
    if not settings.JWDJ_LOGIN_MANAGER:
        return _user_data(request)

    return _user_data(request)

@require_POST
@refresh_session
@handle_exception
def auth_login(request) -> dict[str]:
    if not settings.JWDJ_LOGIN_MANAGER:
        return _user_data(request)

    ser = AuthLoginSerializer(data=JSONParser().parse(io.BytesIO(request.body)))
    if not ser.is_valid():
        raise InvalidDataError(json.dumps(ser.errors, indent=2))
    data = ser.validated_data

    user = authenticate(request=request, username=data['username'], password=data['password'])
    if user is None:
        return _user_data(request)

    login(request=request, user=user)

    return _user_data(request)

@require_POST
@refresh_session
@handle_exception
def auth_logout(request) -> dict[str]:
    # Custom / patched logout to keep the session alive
    with no_flushing_section(request.session):
        logout(request)
        request.session.clear()

    return _user_data(request)

@require_GET
@refresh_session
@ensure_csrf_cookie
@handle_exception
def session_setup(request) -> dict[str]:
    return {}

@require_POST
@refresh_session
@ensure_csrf_cookie
@handle_exception
def session_merge_new_otp(request) -> dict[str]:
    do_poll_cleanup()

    session_key: str = request.session.session_key

    with transaction.atomic():
        try:
            existing = SessionMerge.objects.get(owner = session_key)
            existing.delete()
        except SessionMerge.DoesNotExist:
            pass

        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        otp = ''.join(random.choice(chars) for i in range(8))

        new = SessionMerge.objects.create(
            otp = otp,
            owner = session_key,
        )

        return {
            'otp': new.otp,
            'valid_until': new.valid_until.astimezone(timezone.utc).isoformat()
        }

@require_POST
@refresh_session
@ensure_csrf_cookie
@handle_exception
def session_merge_submit_otp(request) -> dict[str]:
    do_poll_cleanup()

    session: SessionStore = request.session
    session_key: str = session.session_key

    ser = SessionMergeSerializer(data=JSONParser().parse(io.BytesIO(request.body)))
    if not ser.is_valid():
        raise InvalidDataError(json.dumps(ser.errors, indent=2))
    data = ser.validated_data
    otp: str = data['otp']

    with transaction.atomic():
        sm: SessionMerge
        try:
            sm = SessionMerge.objects.get(otp = otp)
        except SessionMerge.DoesNotExist:
            raise InvalidDataError(f'OTP not found or expired')

        if sm.owner == session_key:
            raise InvalidDataError(f'Unable to merge into the same session!')

        # Migrate polls
        for poll in Poll.objects.filter(owner=session_key):
            poll.owner = sm.owner
            poll.save()

        # Migrate votes
        #  - first search for primary ballots
        primary_session_polls = set(x.poll.id for x in Ballot.objects.filter(owner=sm.owner))

        #  - migrate ballots now
        for ballot in Ballot.objects.filter(owner=session_key):
            # Delete ballots that would be duplicate
            if ballot.poll.id in primary_session_polls:
                ballot.delete()
                continue

            # Migrate the rest
            ballot.owner = sm.owner
            ballot.save()

        # Session merge tokens are one time use only
        sm.delete()

        # Switch the session
        session.delete()
        session = SessionStore(sm.owner)
        session.load()
        session.modified = True
        session.save()
        request.session = session

    return {
        'status': 'OK'
    }

@require_POST
@refresh_session
@handle_exception
def new_poll(request) -> dict[str]:
    if settings.JWDJ_LOGIN_MANAGER and not request.user.is_authenticated:
        raise PermissionDenied()

    ser = NewPollSerializer(data=JSONParser().parse(io.BytesIO(request.body)))
    if not ser.is_valid():
        raise InvalidDataError(json.dumps(ser.errors, indent=2))
    data = ser.validated_data

    do_poll_cleanup()

    with transaction.atomic():
        if Poll.objects.count() >= settings.JWDJ_MAX_POLL_COUNT:
            raise MaxPollReachedError(f'Reached the maximum number of polls for this instance')

        poll = Poll.objects.create(
            id = base64.urlsafe_b64encode(uuid.uuid4().int.to_bytes(32, 'little')).decode()[:12],
            owner = request.session.session_key,
            name = data['name'],
            allow_not_voted = data['allow_not_voted'],
            description = data['description'],
        )

        index_set: set[int] = set()
        for i in data['options']:
            idx: int = i['index']
            if idx in index_set:
                raise InvalidDataError(f'Duplicate option index: {idx}')
            index_set.add(idx)
            PollOption.objects.create(
                poll = poll,
                index = idx,
                name = i['name'],
            )

        # Validate that the indexes are continous
        sorted_indexes = list(sorted(index_set))
        if sorted_indexes[0] != 0:
            raise InvalidDataError(f'The first option MUST have index 0!')

        last = 0
        for idx in sorted_indexes[1:]:
            if last + 1 != idx:
                raise InvalidDataError(f'Index list not continous!')
            last = idx

    return {'id': poll.id}

@require_GET
@refresh_session
@ensure_csrf_cookie
@handle_exception
def get_poll_exists(request, poll_id: str) -> dict[str]:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    with transaction.atomic():
        n_found = Poll.objects.filter(pk=poll_id).count()
        if n_found == 0:
            return {
                'found': False
            }
        elif n_found == 1:
            return {
                'found': True
            }
        else:
            raise InvalidInternalState(f'Internal Error: Found {n_found} entries for "{poll_id}"')

@require_GET
@refresh_session
@ensure_csrf_cookie
@handle_exception
def get_poll(request, poll_id: str) -> dict[str]:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    with transaction.atomic():
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        if poll.valid_until < datetime.now():
            do_poll_cleanup()
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        options = PollOption.objects.filter(poll=poll).order_by('index')
        ballots = Ballot.objects.filter(poll=poll).order_by('created')

        ballot_data = []
        my_ballot = None
        for ballot in ballots:
            if (len(ballot.votes) != len(options)):
                raise InvalidInternalState(f'Expected {len(options)} for ballot {ballot.name} but got {len(ballot.votes)}')

            if ballot.owner == request.session.session_key:
                my_ballot = {'name': ballot.name, 'votes': ballot.votes, 'note': ballot.note}
            else:
                ballot_data += [{'name': ballot.name, 'votes': ballot.votes, 'note': ballot.note}]

    return {
        'id': poll.id,
        'name': poll.name,
        'description': poll.description,
        'allow_not_voted': poll.allow_not_voted,
        'is_owner': poll.owner == request.session.session_key,
        'created': poll.created,
        'valid_until': poll.valid_until,
        'published': poll.published,
        'closed': poll.closed,
        'closed_option_idx': poll.closed_option_idx,
        'options': [{'id': str(x.id), 'index': x.index, 'name': x.name} for x in options],
        'ballots': ballot_data,
        'my_ballot': my_ballot,
    }

@require_POST
@refresh_session
@handle_exception
def do_vote(request, poll_id: str) -> dict[str]:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    ser = SubmitVoteSerializer(data=JSONParser().parse(io.BytesIO(request.body)))
    if not ser.is_valid():
        raise InvalidDataError(json.dumps(ser.errors, indent=2))
    data = ser.validated_data

    do_poll_cleanup()

    with transaction.atomic():
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        nopts = PollOption.objects.filter(poll=poll).count()
        nballots = Ballot.objects.filter(poll=poll).count()
        if len(data['votes']) != nopts:
            raise InvalidDataError(f'Invalid vote size {len(data["votes"])}. Expected {nopts}')

        try:
            ballot = Ballot.objects.get(poll=poll, owner=request.session.session_key)
        except Ballot.DoesNotExist:
            if nballots >= settings.JWDJ_MAX_BALLOT_COUNT:
                raise MaxBallotReachedError(f'The maximum number of ballots {settings.JWDJ_MAX_BALLOT_COUNT} was reached for this poll.')
            ballot = Ballot(
                poll=poll,
                owner=request.session.session_key,
            )

        ballot.name = data['name']
        ballot.votes = data['votes']
        ballot.note = data['note']
        ballot.save()

    return {'id': poll.id}

@require_POST
@refresh_session
@handle_exception
def do_update(request, poll_id: str) -> dict[str]:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    ser = UpdatePollSerializer(data=JSONParser().parse(io.BytesIO(request.body)))
    if not ser.is_valid():
        raise InvalidDataError(json.dumps(ser.errors, indent=2))
    data = ser.validated_data

    do_poll_cleanup()

    with transaction.atomic():
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        if poll.owner != request.session.session_key:
            raise PermissionDenied('Only the creator can update polls!')

        poll.name = data['name']
        poll.description = data['description']
        poll.allow_not_voted = data['allow_not_voted']
        poll.save()

        existing_options = PollOption.objects.filter(poll=poll)
        opt_map = {x.index: x for x in existing_options}
        to_delete_options = set(opt_map.keys())

        ballot_update_plan: list[
            T.Tuple[
                int,
                T.Callable[[str], str]
            ]
        ] = []

        # Update / create the options themselfs
        # Als create the update plan
        index_set: set[int] = set()
        for option in data['options']:
            idx: int = option['index']
            old_index: int = option['old_index']
            if idx in index_set:
                raise InvalidDataError(f'Duplicate option index: {idx}')
            index_set.add(idx)

            # New option if the old index is < 0
            if old_index < 0:
                PollOption.objects.create(
                    poll = poll,
                    index = idx,
                    name = option['name'],
                )

                # Insert a '-' for new options
                ballot_update_plan += [
                    (idx, lambda x: '-')
                ]
            # Else, update the existing option
            elif old_index in opt_map:
                opt = opt_map[old_index]
                opt.index = idx
                opt.name = option['name']
                opt.save()

                # Extract the old value
                ballot_update_plan += [
                    (
                        idx,
                        # Ensure that the *value* of old_index is captured in the lambda
                        # and not the *name* / stack reference of old_index
                        (lambda i: lambda x: x[i])(old_index)
                    )
                ]

                # Keep the option around
                to_delete_options.remove(old_index)

        # Validate that the indexes are continous
        sorted_indexes = list(sorted(index_set))
        if sorted_indexes[0] != 0:
            raise InvalidDataError(f'The first option MUST have index 0!')

        last = 0
        for idx in sorted_indexes[1:]:
            if last + 1 != idx:
                raise InvalidDataError(f'Index list not continous!')
            last = idx

        # Remove deleted options
        for delete in to_delete_options:
            opt_map[delete].delete()

        # Update all ballots
        ballot_update_plan = sorted(ballot_update_plan)
        ballots = Ballot.objects.filter(poll=poll)

        for ballot in ballots:
            old_votes = ballot.votes
            new_votes = ''

            for up in ballot_update_plan:
                new_votes += up[1](old_votes)

            ballot.votes = new_votes
            ballot.save()

    return {'id': poll.id}

@require_POST
@refresh_session
@handle_exception
def do_close(request, poll_id: str) -> HttpResponse:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    ser = ClosePollSerializer(data=JSONParser().parse(io.BytesIO(request.body)))
    if not ser.is_valid():
        raise InvalidDataError(json.dumps(ser.errors, indent=2))
    data = ser.validated_data

    do_poll_cleanup()

    with transaction.atomic():
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        if poll.owner != request.session.session_key:
            raise PermissionDenied('Only the creator can close polls!')

        poll.closed = datetime.now()
        poll.closed_option_idx = data['option_idx']
        poll.save()

    return {'id': poll_id}

@require_POST
@refresh_session
@handle_exception
def do_reopen(request, poll_id: str) -> dict[str]:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    do_poll_cleanup()

    with transaction.atomic():
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        if poll.owner != request.session.session_key:
            raise PermissionDenied('Only the creator can reopen polls!')

        poll.closed = None
        poll.closed_option_idx = -1
        poll.save()

    return {'id': poll.id}

@require_POST
@refresh_session
@handle_exception
def do_delete(request, poll_id: str) -> dict[str]:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    do_poll_cleanup()

    with transaction.atomic():
        try:
            poll = Poll.objects.get(pk=poll_id)
        except Poll.DoesNotExist:
            raise PollNotFound(poll_id, f'Unable to find poll "{poll_id}"')

        if poll.owner != request.session.session_key:
            raise PermissionDenied('Only the creator can delete polls!')

        poll.delete()

    return {'id': poll.id}

@require_GET
@refresh_session
@ensure_csrf_cookie
@handle_exception
def my_polls(request) -> dict[str]:
    with transaction.atomic():
        created_by_me = Poll.objects.filter(owner=request.session.session_key, valid_until__gt=datetime.now()).order_by('created')
        voted_in = Ballot.objects.filter(owner=request.session.session_key, poll__valid_until__gt=datetime.now()).order_by('created')

        created_ids = set(x.id for x in created_by_me)

        return {
            'created_by_me': [
                {'id': x.id, 'name': x.name} for x in created_by_me
            ],
            'voted_in': [
                {'id': x.poll.id, 'name': x.poll.name } for x in voted_in if x.poll.id not in created_ids
            ]
        }
