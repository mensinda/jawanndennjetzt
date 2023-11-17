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
import json
import base64
import uuid
import traceback
import io

from importlib import import_module
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from .models import Poll, PollOption, Ballot
from .limits import *
from .serializers import NewPollSerializer, SubmitVoteSerializer, UpdatePollSerializer, ClosePollSerializer, AuthLoginSerializer
from .errors import *
from .cleanup import do_poll_cleanup

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
    logout(request)

    return _user_data(request)

@require_GET
@refresh_session
@ensure_csrf_cookie
@handle_exception
def session_setup(request) -> dict[str]:
    return {}

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

        for i in data['options']:
            PollOption.objects.create(
                poll = poll,
                index = i['index'],
                name = i['name'],
            )

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
        created_by_me = Poll.objects.filter(owner=request.session.session_key).order_by('created')
        voted_in = Ballot.objects.filter(owner=request.session.session_key).order_by('created')

        created_ids = set(x.id for x in created_by_me)

        return {
            'created_by_me': [
                {'id': x.id, 'name': x.name} for x in created_by_me
            ],
            'voted_in': [
                {'id': x.poll.id, 'name': x.poll.name } for x in voted_in if x.poll.id not in created_ids
            ]
        }
