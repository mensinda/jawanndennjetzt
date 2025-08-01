# Generated by Django 5.2.4 on 2025-07-22 12:16

import server.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SessionMerge',
            fields=[
                ('otp', models.CharField(max_length=8, primary_key=True, serialize=False)),
                ('owner', models.CharField(max_length=32, unique=True)),
                ('valid_until', models.DateTimeField(default=server.models._default_sesssion_merge_valid_until)),
            ],
            options={
                'indexes': [models.Index(fields=['valid_until'], name='server_sess_valid_u_f846df_idx'), models.Index(fields=['owner'], name='server_sess_owner_1b4ecb_idx')],
            },
        ),
    ]
