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

// Import theme variables
@import "bootswatch/dist/${JWDJ_THEME}/variables";

// This would import ALL of bootstrap, which is a lot
// @import "bootstrap/scss/bootstrap";

// So we just import what we need:

// scss-docs-start import-stack
// Configuration
@import "bootstrap/scss/functions";
@import "bootstrap/scss/variables";
@import "bootstrap/scss/variables-dark";
@import "bootstrap/scss/maps";
@import "bootstrap/scss/mixins";
@import "bootstrap/scss/utilities";

// Layout & components
@import "bootstrap/scss/root";
@import "bootstrap/scss/reboot";
@import "bootstrap/scss/type";
// @import "bootstrap/scss/images";
@import "bootstrap/scss/containers";
@import "bootstrap/scss/grid";
@import "bootstrap/scss/tables";
@import "bootstrap/scss/forms";
@import "bootstrap/scss/buttons";
@import "bootstrap/scss/transitions";
// @import "bootstrap/scss/dropdown";
@import "bootstrap/scss/button-group";
@import "bootstrap/scss/nav";
@import "bootstrap/scss/navbar";
@import "bootstrap/scss/card";
// @import "bootstrap/scss/accordion";
// @import "bootstrap/scss/breadcrumb";
// @import "bootstrap/scss/pagination";
// @import "bootstrap/scss/badge";
// @import "bootstrap/scss/alert";
// @import "bootstrap/scss/progress";
// @import "bootstrap/scss/list-group";
@import "bootstrap/scss/close";
// @import "bootstrap/scss/toasts";
@import "bootstrap/scss/modal";
// @import "bootstrap/scss/tooltip";
// @import "bootstrap/scss/popover";
// @import "bootstrap/scss/carousel";
// @import "bootstrap/scss/spinners";
// @import "bootstrap/scss/offcanvas";
// @import "bootstrap/scss/placeholders";

// Helpers
@import "bootstrap/scss/helpers";

// Utilities
@import "bootstrap/scss/utilities/api";

// Finally, import the rest from the theme:
@import "bootswatch/dist/${JWDJ_THEME}/bootswatch";
EOF

[ -z "$JWDJ_SUBPATH"         ] && JWDJ_SUBPATH="/"
[ -z "$JWDJ_LOGO_WIDTH"      ] && JWDJ_LOGO_WIDTH="30px"
[ -z "$JWDJ_LOGO_HEIGHT"     ] && JWDJ_LOGO_HEIGHT="30px"
[ -z "$JWDJ_PRIMARY_BTN_CLS" ] && JWDJ_PRIMARY_BTN_CLS="btn-success"

if [[ "$JWDJ_DARK_DATE_PICKER" == "0" || "$JWDJ_DARK_DATE_PICKER" == "false" ]]; then
    JWDJ_DARK_DATE_PICKER="false"
else
    JWDJ_DARK_DATE_PICKER="true"
fi

if [[ "$JWDJ_LOGIN_MANAGER" == "0" || "$JWDJ_LOGIN_MANAGER" == "false" || "$JWDJ_LOGIN_MANAGER" == "" ]]; then
    JWDJ_LOGIN_MANAGER="false"
else
    JWDJ_LOGIN_MANAGER="true"
fi

if [[ "$JWDJ_ENABLE_PARTICLES" == "0" || "$JWDJ_ENABLE_PARTICLES" == "false" || "$JWDJ_ENABLE_PARTICLES" == "" ]]; then
    JWDJ_ENABLE_PARTICLES="false"
else
    JWDJ_ENABLE_PARTICLES="true"
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
const JWDJ_LOGIN_MANAGER = $JWDJ_LOGIN_MANAGER;
const JWDJ_LOGIN_SYSTEM_NAME = "$JWDJ_LOGIN_SYSTEM_NAME";
const JWDJ_NAV_BG_CLASS = "$JWDJ_NAV_BG_CLASS";
const JWDJ_NAV_BG_TYPE = "$JWDJ_NAV_BG_TYPE";
const JWDJ_PRIMARY_BTN_CLS = "$JWDJ_PRIMARY_BTN_CLS";
const JWDJ_ENABLE_PARTICLES = ${JWDJ_ENABLE_PARTICLES};

import DarkModeToggle from "@/components/darkmode/$DARK_MODE_IMPORT";

export {
  JWDJ_SUBPATH,
  JWDJ_LOGO,
  JWDJ_LOGO_WIDTH,
  JWDJ_LOGO_HEIGHT,
  JWDJ_LOGO_VERTICAL_MARGIN,
  JWDJ_DARK_DATE_PICKER,
  JWDJ_LOGIN_MANAGER,
  JWDJ_LOGIN_SYSTEM_NAME,
  JWDJ_NAV_BG_CLASS,
  JWDJ_NAV_BG_TYPE,
  JWDJ_PRIMARY_BTN_CLS,
  JWDJ_ENABLE_PARTICLES,
  DarkModeToggle,
};
EOF

if [[ "$JWDJ_ENABLE_PARTICLES" == "true" ]]; then

cat <<EOF > src/particles.ts
import Particles from "./particles/particles-index";
import { loadSlim } from "@tsparticles/slim";
import { App as Application } from "vue";

function doInitParticles(app: Application) {
  app.use(Particles, { init: async (engine) => await loadSlim(engine) });
}

export default doInitParticles;
EOF

else

cat <<EOF > src/particles.ts
import { App as Application } from "vue";
import particles from "./particles/vue-particles-dummy.vue";

function doInitParticles(app: Application) {
  // Particles are disabled via JWDJ_ENABLE_PARTICLES --> load a dummy component
  app.component("vue-particles", particles);
}

export default doInitParticles;
EOF

fi
