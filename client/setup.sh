#!/bin/bash

cd "$(dirname "$(realpath "$0")")"

# Check for .env
if [ -f ../.env ]; then
    source ../.env
fi

if [ -f .env ]; then
    source .env
fi

if [ -z "$JWDJ_THEME" ]; then
    JWDJ_THEME="flatly"
fi

if [ -z "$JWDJ_WEB_FONTS" ]; then
    JWDJ_WEB_FONTS=0
fi

[ -e src/theme.scss ] && rm src/theme.scss

if [[ "$JWDJ_WEB_FONTS" == "0" || "$JWDJ_WEB_FONTS" == "false" ]]; then
    echo "\$web-font-path: false;" >> src/theme.scss
fi

if [ -f variables.scss ]; then
    cat variables.scss >> src/theme.scss
fi

cat <<EOF >> src/theme.scss

@import "~bootswatch/dist/${JWDJ_THEME}/variables";
@import "~bootstrap/scss/bootstrap";
@import "~bootswatch/dist/${JWDJ_THEME}/bootswatch";
EOF

if [ -z "$JWDJ_SUBPATH" ]; then
    JWDJ_SUBPATH="/"
fi

cat <<EOF > src/config.ts
const JWDJ_SUBPATH = "${JWDJ_SUBPATH}";

export { JWDJ_SUBPATH };
EOF
