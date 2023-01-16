#!/bin/bash

cd "$(dirname "$(realpath "$0")")"

# Check for .env
if [ -f .env ]; then
    source .env
fi

if [ -z "$JWDJ_THEME" ]; then
    JWDJ_THEME="flatly"
fi

cat <<EOF > src/theme.scss
\$web-font-path: false;

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
