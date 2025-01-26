#!/bin/bash

set -e
set -u

[ -e .env                  ] && source .env
[ -e /run/secrets/jwdj.env ] && source /run/secrets/jwdj.env

[[ ! -d /static ]] && mkdir /static
rm -rf /static/*
cp -R /static_raw/* /static

if [[ "$JWDJ_DATABASE_TYPE" == "postgresql" ]]; then
    ./wait-for-it.sh $JWDJ_POSTGRES_HOST:$JWDJ_POSTGRES_PORT
fi

./manage.py migrate

gunicorn server.wsgi:application --bind 0.0.0.0:8000
