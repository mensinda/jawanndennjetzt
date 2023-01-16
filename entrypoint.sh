#!/bin/bash

set -e
set -u

source .env

if [[ "$JWDJ_DATABASE_TYPE" == "postgresql" ]]; then
    ./wait-for-it.sh $JWDJ_POSTGRES_HOST:$JWDJ_POSTGRES_PORT
fi

./manage.py migrate

gunicorn server.wsgi:application --bind 0.0.0.0:8000
