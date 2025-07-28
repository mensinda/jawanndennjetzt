from .models import Poll, SessionMerge
from django.db import transaction

import datetime

def do_poll_cleanup():
    with transaction.atomic():
        to_clean = Poll.objects.filter(valid_until__lt=datetime.datetime.now())
        for poll in to_clean:
            print(f'CLEANUP: deleting poll {poll.id}')
            poll.delete()

    with transaction.atomic():
        to_clean = SessionMerge.objects.filter(valid_until__lt=datetime.datetime.now())
        for sm in to_clean:
            print(f'CLEANUP: deleting SessionMerge for {sm.owner}')
            sm.delete()
