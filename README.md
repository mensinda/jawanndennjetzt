# JaWannDennJetzt

![SC1](img/sc1.png)

This project aims to address one of mankinds toughest challenges to date: **Scheduling a date for a group of people.**

Taking inspiration from the similarly named project **_JaWannDenn_** (German for _'So, when is it gonna be?'_), we started from scratch and built **_JaWannDennJetzt_** (German for _'So, when is it **finally** gonna be?!'_).
It provides a useful poll creation tool to help tackle the above problem. Polls can be created and shared within seconds, while users can respond to them just as quickly\*. Should anything come up and a vote needs updating, the user can simply update their vote. Once all votes are in, the final result can be chosen from an easy to read vote overview.
This makes the entire scheduling process simple, quick and as straightforward as possible.

\*_theoretically, if the stars align and they already know their schedule_

# Running / Deploying via docker compose

We do not provide pre-built docker images because some configuration options are used at build time (the theme, for instance). However, building and running the docker images is fairly straightforward with docker compose:

First, clone this repository and copy the [`example.env`](/example.env) in the root directoy to a `.env` file (also in the root directry). Then adjust the configuration options. See [Configuration](#configuration) for more information.

The variables defined in the `.env` file can be overwritten with environment variables. However, this is not recommended since the variables should be identical both at build- and runtime.

---

JaWannDennJetzt currently supports two database engines: SQLite3 and PostgreSQL. Depending on which engine you have chosen, use the corresponding `docker-compose.*.yaml` file as a template for your `docker-compose.yaml`. If you are fine with the defaults, no further configuration should be required.

Now, you can use this command to build and run JaWannDennJetzt:

```bash
docker compose up --build
```

## Configuration

JaWannDennJetzt supports the following configuration options:

| Option                        | Description                                                                                                                                          | Type  |
|-------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|:-----:|
| `SECRET_KEY`                  | The [Django secret key](https://docs.djangoproject.com/en/4.1/ref/settings/#secret-key). This value **MUST** be changed!                             |  `R`  |
| `DEBUG`                       | Whether to run in debug mode. **DO NOT ENABLE THIS FOR PRODUCTION**                                                                                  | `B,R` |
| `NODE_ENV`                    | Should be set to `production` when running in a production environment                                                                               |  `B`  |
| `JWDJ_SUBPATH`                | Prefix from which the app should be served (default is "/"). A common use-case for such a setup is serving multiple applications on the same domain. |  `B`  |
| `JWDJ_THEME`                  | Which theme from [Bootswatch](https://bootswatch.com) to use                                                                                         |  `B`  |
| `JWDJ_DARK_DATE_PICKER`       | Enables the dark theme for the date picker.                                                                                                          |  `B`  |
| `JWDJ_WEB_FONTS`              | Whether to include external fonts or not. If this option is disabled, no external assets and services will be used.                                  |  `B`  |
| `JWDJ_FAVICON`                | The favicion of the site relative to `client/public`..                                                                                               |  `B`  |
| `JWDJ_OPEN_GRAPH_IMAGE`       | The image for the [Open Graph](https://ogp.me/) protocol relative to `client/public`.                                                                |  `B`  |
| `JWDJ_LOGO`                   | The logo to display in the navbar relative to `client/public`. Set this variable to an empty string to disable showing the logo                      |  `B`  |
| `JWDJ_LOGO_WIDTH`             | Width of the logo in the navbar                                                                                                                      |  `B`  |
| `JWDJ_LOGO_HEIGHT`            | Height of the logo in the navbar                                                                                                                     |  `B`  |
| `JWDJ_LOGO_VERTICAL_MARGIN`   | Advanced option to set the top and bottom margin. The main use-case is to set a negative margin for large logos. Must be a valid CSS margin value.   |  `B`  |
| `JWDJ_DARK_MODE_TOGGLE`       | Which dark mode toggle to use (suported values: [`fancy`, `minimal`, `off`])                                                                         |  `B`  |
| `JWDJ_SERVE_STATIC_FILES`     | Whether the static client HTML / CSS / JS should be served via the django backend (by default, static files are served via Nginx).                   |  `R`  |
| `JWDJ_CLIENT_DIST`            | Where the static files are located if `JWDJ_SERVE_STATIC_FILES` is enabled                                                                           |  `R`  |
| `JWDJ_DAYS_TO_KEEP`           | Number of days polls are kept                                                                                                                        |  `R`  |
| `JWDJ_MAX_POLL_COUNT`         | The total maximum number of polls that are allowed (primitive DOS protection)                                                                        |  `R`  |
| `JWDJ_MAX_OPTIONS_COUNT`      | The maximum number of options / days for each poll (primitive DOS protection)                                                                        |  `R`  |
| `JWDJ_MAX_BALLOT_COUNT`       | The maximum number of users that can vote on a poll (primitive DOS protection)                                                                       |  `R`  |
| `JWDJ_SESSION_CLEAN_INTERVAL` | The interval in days for cleaning expired sessions (use values <= 0 to disable)                                                                      |  `R`  |
| `SESSION_COOKIE_AGE`          | How long the [Django session cookie](https://docs.djangoproject.com/en/4.1/ref/settings/#session-cookie-age) is valid (defaults to 4 weeks)          |  `R`  |
| `ALLOWED_HOSTS`               | Comma seperated list of allowed host names (just the hostname without the subpath)                                                                   |  `R`  |
| `JWDJ_DATABASE_TYPE`          | Which database engine to use. Valid values are `sqlite3` and `postgresql`                                                                            |  `R`  |
| `JWDJ_SQLITE_FILE`            | Path to the SQLite3 DB                                                                                                                               |  `R`  |
| `JWDJ_POSTGRES_NAME`          | Name of the PostgreSQL DB                                                                                                                            |  `R`  |
| `JWDJ_POSTGRES_USER`          | Username used for the PostgreSQL DB                                                                                                                  |  `R`  |
| `JWDJ_POSTGRES_PASSWORD`      | The password for the PostgreSQL DB. **NOTE**: The value of this variable should be changed!                                                          |  `R`  |
| `JWDJ_POSTGRES_HOST`          | Hostname where the PostgreSQL DB is hosted                                                                                                           |  `R`  |
| `JWDJ_POSTGRES_PORT`          | Port of the PostgreSQL DB                                                                                                                            |  `R`  |

The `Type` column in the table indicates whether the variable is evaluated at runtime (`R`) or at build time (`B`). Changes to buildtime variables have no effect on already built images and only take effect when the image is rebuilt! Variables that are used both at build and runtime are marked with `B,R` and **should** be treated as build time variables.

### Theme customization

Any available Bootswatch theme can be used to style the application, which can further be customized to tweak the appearance even more precisely.

This is done by overriding the default values of the `_variables.scss` file provided by the selected Bootswatch theme. The default variables for each theme can be inspected on the [Bootswatch GitHub](https://github.com/thomaspark/bootswatch) under `dist/<theme>/_variables.scss`.

To get started on such a custom theme modification, copy the `example.variables.scss` in the `client` directory to `variables.scss` and alter any variables within to better suit your desired appearance.
The `variables.scss` file will then be automatically detected by the setup script.

NOTE: The final `variables.scss` **MUST** be in the `client` directory!

# Development setup

To run JaWannDennJetzt locally for development the following `.env` file is recommended:

```ini
SECRET_KEY=django-insecure-XXXX
DEBUG=1
NODE_ENV=debug
JWDJ_SERVE_STATIC_FILES=1

# Theme name from https://bootswatch.com
JWDJ_THEME=flatly

# Add "127.0.0.1:1337" to this list for running the provided docker compose config locally
ALLOWED_HOSTS=127.0.0.1,localhost,127.0.0.1:8080,127.0.0.1:8000,localhost:8080,localhost:8000

JWDJ_DATABASE_TYPE=sqlite3
# JWDJ_SQLITE_FILE=./db.sqlite3
```

First install the requirements, ideally in a [python venv](https://docs.python.org/3/library/venv.html):

```sh
pip install -r requirements.txt
```

Next, the database must be generated with the following command:

```sh
./manage.py migrate
```

Rerunning this command should only be required when the database is deleted or additional migration scripts are added.

The backend can then be started via:

```sh
./manage.py runserver
```

Now, the server should be running. Use a separate terminal to build and serve the client with the following commands:

```sh
cd client
yarn install # Should only be required once
yarn serve
```

The development app should then be availiable at [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Upgrading dependencies

### Server

`sed -i 's/[~=]=/>=/' requirements.txt; pip install -U -r requirements.txt; pip freeze > requirements.txt`

### Client

`yarn upgrade-interactive`

# Markdown extension

Currently, all text fields support the Markdown syntax. Additionally, JaWannDennJetzt adds support for colorizing
text with the following new HTML tags:

- `<m>` for muted text
- `<w>` for warning text
- `<d>` for error text
- `<s>` for success text
- `<i>` for info text

The actual colors will depend on the bootstrap theme of the client.
