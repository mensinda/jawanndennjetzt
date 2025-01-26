#!/bin/bash

set -e

cd "$(dirname "$0")"

source .env

PREFIX=jwdj
DRIVER=podman

help() {
  cat <<EOF
Usage: $0 [-p|--prefix <PREFIX>] [-h|--help]

Options:
  -h | --help             Show this help message and exit
  -p | --prefix   PREFIX  Use the PREFIX for the image and secret names   [default: jwdj]
  -d | --driver   DRIVER  The driver (podman / docker) to use             [default: podman]
EOF
}

while [[ $# -gt 0 ]]; do
  case $1 in
    -p|--prefix)
      PREFIX="$2"
      shift # past argument
      shift # past value
      ;;
    -d|--driver)
      DRIVER="$2"
      shift # past argument
      shift # past value
      ;;
    -h|--help)
      help
      exit 1
      ;;
    *)
      help
      echo "Unknown option $1"
      exit 1
      ;;
  esac
done

# Create the client build env file
# This file only contains withelisted variables to not expose any secrets
cat <<EOF > .env.client.tmp
DEBUG=$DEBUG
NODE_ENV=$NODE_ENV
JWDJ_HOST=$JWDJ_HOST
JWDJ_SUBPATH=$JWDJ_SUBPATH
JWDJ_THEME=$JWDJ_THEME
JWDJ_NAV_BG_CLASS=$JWDJ_NAV_BG_CLASS
JWDJ_NAV_BG_TYPE=$JWDJ_NAV_BG_TYPE
JWDJ_PRIMARY_BTN_CLS=$JWDJ_PRIMARY_BTN_CLS
JWDJ_ENABLE_PARTICLES=$JWDJ_ENABLE_PARTICLES
JWDJ_DARK_DATE_PICKER=$JWDJ_DARK_DATE_PICKER
JWDJ_WEB_FONTS=$JWDJ_WEB_FONTS
JWDJ_FAVICON=$JWDJ_FAVICON
JWDJ_OPEN_GRAPH_IMAGE=$JWDJ_OPEN_GRAPH_IMAGE
JWDJ_LOGO=$JWDJ_LOGO
JWDJ_LOGO_WIDTH=$JWDJ_LOGO_WIDTH
JWDJ_LOGO_HEIGHT=$JWDJ_LOGO_HEIGHT
JWDJ_LOGO_VERTICAL_MARGIN=$JWDJ_LOGO_VERTICAL_MARGIN
JWDJ_DARK_MODE_TOGGLE=$JWDJ_DARK_MODE_TOGGLE
JWDJ_SESSION_CLEAN_INTERVAL=$JWDJ_SESSION_CLEAN_INTERVAL
JWDJ_DAYS_TO_KEEP=$JWDJ_DAYS_TO_KEEP
JWDJ_MAX_POLL_COUNT=$JWDJ_MAX_POLL_COUNT
JWDJ_MAX_OPTIONS_COUNT=$JWDJ_MAX_OPTIONS_COUNT
JWDJ_MAX_BALLOT_COUNT=$JWDJ_MAX_BALLOT_COUNT
JWDJ_LOGIN_MANAGER=$JWDJ_LOGIN_MANAGER
JWDJ_LOGIN_SYSTEM_NAME=$JWDJ_LOGIN_SYSTEM_NAME
EOF

# Build the immages
$DRIVER build -t $PREFIX-nginx   --target nginx   .
$DRIVER build -t $PREFIX-backend --target backend .

# create the secretes
cat <<EOF > .env.db.tmp
POSTGRES_NAME=$JWDJ_POSTGRES_NAME
POSTGRES_USER=$JWDJ_POSTGRES_USER
POSTGRES_PASSWORD=$JWDJ_POSTGRES_PASSWORD
EOF

$DRIVER secret create --replace $PREFIX-backend-secret .env
$DRIVER secret create --replace $PREFIX-db-secret      .env.db.tmp

# Cleanup
rm .env.db.tmp
