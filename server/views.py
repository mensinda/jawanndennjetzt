from functools import wraps

from django.views.decorators.http import require_GET, require_POST
from django.http.response import JsonResponse, HttpResponse
from django.db import transaction
from django.conf import settings
from rest_framework.parsers import JSONParser
from django.views.decorators.csrf import ensure_csrf_cookie
import json
import base64
import uuid
import traceback
import io
import datetime

from importlib import import_module
SessionStore = import_module(settings.SESSION_ENGINE).SessionStore

from .models import Poll, PollOption, Ballot
from .limits import *
from .serializers import NewPollSerializer, SubmitVoteSerializer, UpdatePollSerializer, ClosePollSerializer
from .errors import *
from .cleanup import do_poll_cleanup

def handle_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
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

def refresh_session(f):
    @wraps(f)
    def wrapper(request, *args, **kwargs):
        if not request.session.session_key:
            request.session.save()
        request.session.modified = True
        return f(request, *args, **kwargs)
    return wrapper

@require_GET
@handle_exception
@refresh_session
@ensure_csrf_cookie
def session_setup(request):
    return JsonResponse({'status': 'ok'})

@require_POST
@handle_exception
@refresh_session
def new_poll(request):
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

    return JsonResponse({'status': 'OK', 'id': poll.id})

@require_GET
@handle_exception
@refresh_session
@ensure_csrf_cookie
def get_poll_exists(request, poll_id: str) -> HttpResponse:
    if not poll_id or not isinstance(poll_id, str):
        raise InvalidDataError(f'ID "{poll_id}" is not a string or empty')

    with transaction.atomic():
        n_found = Poll.objects.filter(pk=poll_id).count()
        if n_found == 0:
            return JsonResponse({
                'found': False
            })
        elif n_found == 1:
            return JsonResponse({
                'found': True
            })
        else:
            raise InvalidInternalState(f'Internal Error: Found {n_found} entries for "{poll_id}"')

@require_GET
@handle_exception
@refresh_session
@ensure_csrf_cookie
def get_poll(request, poll_id: str) -> HttpResponse:
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

    return JsonResponse({
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
    })

@require_POST
@handle_exception
@refresh_session
def do_vote(request, poll_id: str) -> HttpResponse:
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

    return JsonResponse({'status': 'OK', 'id': poll.id})

@require_POST
@handle_exception
@refresh_session
def do_update(request, poll_id: str) -> HttpResponse:
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

    return JsonResponse({'status': 'OK', 'id': poll.id})

@require_POST
@handle_exception
@refresh_session
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

        poll.closed = datetime.datetime.now()
        poll.closed_option_idx = data['option_idx']
        poll.save()

    return JsonResponse({'status': 'OK', 'id': poll_id})

@require_POST
@handle_exception
@refresh_session
def do_reopen(request, poll_id: str) -> HttpResponse:
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

    return JsonResponse({'status': 'OK', 'id': poll.id})

@require_POST
@handle_exception
@refresh_session
def do_delete(request, poll_id: str) -> HttpResponse:
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

    return JsonResponse({'status': 'OK', 'id': poll.id})

@require_GET
@handle_exception
@refresh_session
@ensure_csrf_cookie
def my_polls(request) -> HttpResponse:
    with transaction.atomic():
        created_by_me = Poll.objects.filter(owner=request.session.session_key).order_by('created')
        voted_in = Ballot.objects.filter(owner=request.session.session_key).order_by('created')

        created_ids = set(x.id for x in created_by_me)

        return JsonResponse({
            'status': 'OK',
            'created_by_me': [
                {'id': x.id, 'name': x.name} for x in created_by_me
            ],
            'voted_in': [
                {'id': x.poll.id, 'name': x.poll.name } for x in voted_in if x.poll.id not in created_ids
            ]
        })
