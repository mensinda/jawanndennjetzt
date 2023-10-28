#!/bin/bash

cd "$(dirname "$(realpath "$0")")"

# Check for .env
[ -f ../.env ] && source ../.env
[ -f .env    ] && source .env

# Default variables
[ -z "$JWDJ_THEME"     ] && JWDJ_THEME="flatly"
[ -z "$JWDJ_WEB_FONTS" ] && JWDJ_WEB_FONTS=0

[ -e src/theme.scss ] && rm src/theme.scss

if [[ "$JWDJ_WEB_FONTS" == "static" ]]; then
    FONT_CSS="src/assets/fonts/${JWDJ_THEME}-fonts.css"
    if [ -f "$FONT_CSS" ]; then
        echo "\$web-font-path: '/$FONT_CSS';" >> src/theme.scss
    else
        echo "WARNING: Static font for theme '${JWDJ_THEME}' was not found!\n\n\n"
    fi
elif [[ "$JWDJ_WEB_FONTS" == "0" || "$JWDJ_WEB_FONTS" == "false" ]]; then
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

[ -z "$JWDJ_SUBPATH"     ] && JWDJ_SUBPATH="/"
[ -z "$JWDJ_LOGO_WIDTH"  ] && JWDJ_LOGO_WIDTH="30px"
[ -z "$JWDJ_LOGO_HEIGHT" ] && JWDJ_LOGO_HEIGHT="30px"

if [[ "$JWDJ_DARK_DATE_PICKER" == "0" || "$JWDJ_DARK_DATE_PICKER" == "false" ]]; then
    JWDJ_DARK_DATE_PICKER="false"
else
    JWDJ_DARK_DATE_PICKER="true"
fi

case "$JWDJ_DARK_MODE_TOGGLE" in
    fancy)   DARK_MODE_IMPORT="ToggleFancy.vue"   ;;
    minimal) DARK_MODE_IMPORT="ToggleMinimal.vue" ;;
    off)     DARK_MODE_IMPORT="ToggleDummy.vue"   ;;
    *)
        echo "Invalid JWDJ_DARK_MODE_TOGGLE: '$JWDJ_DARK_MODE_TOGGLE'"
        exit 1;
        ;;
esac

cat <<EOF > src/config.ts
const JWDJ_SUBPATH = "${JWDJ_SUBPATH}";
const JWDJ_LOGO = "${JWDJ_LOGO}";
const JWDJ_LOGO_WIDTH = "${JWDJ_LOGO_WIDTH}";
const JWDJ_LOGO_HEIGHT = "${JWDJ_LOGO_HEIGHT}";
const JWDJ_LOGO_VERTICAL_MARGIN = "${JWDJ_LOGO_VERTICAL_MARGIN}";
const JWDJ_DARK_DATE_PICKER = $JWDJ_DARK_DATE_PICKER;

import DarkModeToggle from "@/components/darkmode/$DARK_MODE_IMPORT";

export {
  JWDJ_SUBPATH,
  JWDJ_LOGO,
  JWDJ_LOGO_WIDTH,
  JWDJ_LOGO_HEIGHT,
  JWDJ_LOGO_VERTICAL_MARGIN,
  JWDJ_DARK_DATE_PICKER,
  DarkModeToggle,
};
EOF
