#!/bin/sh

source .env
sed -i "s|@SUB_PATH@|$JWDJ_SUBPATH|g" /etc/nginx/conf.d/nginx.conf

rm /etc/nginx/conf.d/default.conf

if [[ "$JWDJ_SUBPATH" != "/" ]]; then
    mv /static /static.old
    mkdir -p "/static/$JWDJ_SUBPATH"
    mv /static.old/* "/static/$JWDJ_SUBPATH"
    rm -rf /static.old
fi
