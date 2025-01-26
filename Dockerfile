# Client
FROM docker.io/node:23.6.1 AS builder

WORKDIR /app
COPY client /app/
COPY .env.client.tmp /.env

RUN yarn install
RUN yarn build


# NGINX
FROM docker.io/nginx:alpine as nginx

COPY nginx.conf /etc/nginx/conf.d
COPY --from=builder /app/dist /static/
COPY .env.client.tmp docker/patchNginxConf.sh /
RUN ./patchNginxConf.sh


# JaWannDennJetzt
FROM docker.io/python:3.13-alpine as backend
WORKDIR /app

COPY manage.py requirements.txt docker/setupBackend.sh docker/entrypoint.sh external/wait-for-it.sh /app/
COPY server /app/server
RUN ./setupBackend.sh

# Copy to /static_raw and then to /static in the entrypoint.sh. This way the static content
# can be exposed via `-v ./static:/static/`.
COPY --from=builder /app/dist /static_raw/
ENTRYPOINT ["/app/entrypoint.sh"]
