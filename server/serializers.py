from rest_framework.serializers import Serializer, CharField, BooleanField, IntegerField, EmailField, ValidationError
from django.conf import settings

from .limits import *

class OptionSerializer(Serializer):
    index = IntegerField(min_value=0)
    name = CharField(max_length=NAME_LENGTH)

class NewPollSerializer(Serializer):
    name = CharField(max_length=TITLE_LENGTH, allow_blank=False)
    description = CharField(max_length=DESCRIPTION_LENGTH, allow_blank=True)
    allow_not_voted = BooleanField()
    options = OptionSerializer(many=True, min_length=1, max_length=settings.JWDJ_MAX_OPTIONS_COUNT)


class SubmitVoteSerializer(Serializer):
    name = CharField(max_length=NAME_LENGTH)
    votes = CharField(max_length=MAX_VOTES)
    note = CharField(max_length=DESCRIPTION_LENGTH, allow_blank=True)

    def validate_votes(self, raw: str):
        for v in raw:
            if v not in ('-', 'Y', 'N', 'M'):
                raise ValidationError(f'Invalid vote char "{v}" in votes (allowed chars are)')

        return raw

class UpdatePollSerializer(Serializer):
    name = CharField(max_length=TITLE_LENGTH, allow_blank=False)
    description = CharField(max_length=DESCRIPTION_LENGTH, allow_blank=True)
    allow_not_voted = BooleanField()

class ClosePollSerializer(Serializer):
    option_idx = IntegerField()
