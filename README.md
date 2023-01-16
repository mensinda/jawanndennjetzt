# JaWannDennJetzt

This project aims to address one of mankinds toughest challenges to date: **Scheduling a date for a group of people.**

Taking inspiration from the similarly named project **_JaWannDenn_** (German for _'So, when is it gonna be?'_), we started from scratch and built **_JaWannDennJetzt_** (German for _'So, when is it **finally** gonna be?!'_).
It provides a useful poll creation tool to help tackle the above problem. Polls can be created and shared within seconds, while users can respond to them just as quickly\*. Should anything come up and a vote needs updating, the user can simply update their vote. Once all votes are in, the final result can be chosen from an easy to read vote overview.
This makes the entire scheduling process simple, quick and as straightforward as possible.

\*_theoretically, if the stars align and they already know their schedule_

## Configuration

```bash
# Important: This option MUST be changed
# ======================================
#
# To generate the key, use `openssl rand -base64 66 | tr -d '\n'` for instance
SECRET_KEY=django-insecure-XXXX

# Production settings
# ==================

# These two variables should never be changed!
DEBUG=0
NODE_ENV=production

# When the endpoint is served at a subpath
# (e.g. nginx with a location that is not "/")
#
# NOTE: All values should start and end with a "/" char
JWDJ_SUBPATH=/

# Theme name from https://bootswatch.com
JWDJ_THEME=flatly

# Poll settings
# =============

JWDJ_DAYS_TO_KEEP=32
JWDJ_MAX_POLL_COUNT=4096
JWDJ_MAX_OPTIONS_COUNT=64
JWDJ_MAX_BALLOT_COUNT=256

# Django
# ======
#
# Age of the session cookie in seconds
#   2419200 == 4 * 7 * 24 * 60 * 60  (== 4 weeks)
SESSION_COOKIE_AGE=2419200

# Add "127.0.0.1:1337" to this list for running the provided docker compose config locally
ALLOWED_HOSTS=127.0.0.1,localhost,127.0.0.1:1337


# Database
# ========

# - sqlite3      -- use this config if you run the sqlite docker compose config
#JWDJ_DATABASE_TYPE=sqlite3
#JWDJ_SQLITE_FILE=/db/db.sqlite3

# - postgresql   -- use this config if you run the postgresql docker compose config
JWDJ_DATABASE_TYPE=postgresql
JWDJ_POSTGRES_NAME=jwdj
JWDJ_POSTGRES_USER=jwdj
JWDJ_POSTGRES_PASSWORD=insecure-pw-pls-change
JWDJ_POSTGRES_HOST=postgres
JWDJ_POSTGRES_PORT=5432


# Static files
# ============

# Enable this if you want to use django for serving the static
# client html / js / css files. This is NOT recommended!
JWDJ_SERVE_STATIC_FILES=0

# Where the client dist is located (for django)
JWDJ_CLIENT_DIST=/static

```
