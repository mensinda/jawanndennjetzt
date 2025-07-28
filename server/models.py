from django.db import models
import datetime

from django.conf import settings
from .limits import *

def _default_valid_until() -> datetime.datetime:
    return datetime.datetime.now() + datetime.timedelta(days=settings.JWDJ_DAYS_TO_KEEP)

class Poll(models.Model):
    id = models.CharField(max_length=16, primary_key=True)
    owner = models.CharField(max_length=SESSION_KEY_LENGTH) # Session key
    name = models.CharField(max_length=TITLE_LENGTH)
    description = models.CharField(max_length=DESCRIPTION_LENGTH)
    allow_not_voted = models.BooleanField()
    created = models.DateTimeField(auto_now=True)
    valid_until = models.DateTimeField(default=_default_valid_until)
    published = models.DateTimeField(default=None, null=True)
    closed = models.DateTimeField(default=None, null=True)
    closed_option_idx = models.SmallIntegerField(default=-1)

    class Meta:
        indexes = [
            models.Index(fields=['valid_until']),
            models.Index(fields=['owner']),
        ]

class PollOption(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    index = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=NAME_LENGTH)

class Ballot(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    name = models.CharField(max_length=NAME_LENGTH)
    note = models.CharField(max_length=DESCRIPTION_LENGTH, null=True)
    owner = models.CharField(max_length=SESSION_KEY_LENGTH) # Session key
    created = models.DateTimeField(auto_now=True)

    # Votes have a length of 1 and valid chars are '-', 'Y', 'N', 'M'
    votes = models.CharField(max_length=MAX_VOTES)

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
        ]

def _default_sesssion_merge_valid_until():
    return datetime.datetime.now() + datetime.timedelta(minutes=5)

class SessionMerge(models.Model):
    otp = models.CharField(max_length=8, primary_key=True)
    owner = models.CharField(max_length=SESSION_KEY_LENGTH, unique=True) # Session key
    valid_until = models.DateTimeField(default=_default_sesssion_merge_valid_until)

    class Meta:
        indexes = [
            models.Index(fields=['valid_until']),
            models.Index(fields=['owner']),
        ]
