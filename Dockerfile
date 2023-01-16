# Client
FROM node AS builder

WORKDIR /app
ADD client .env /app/

RUN ./dockerBuild.sh


# NGINX
FROM nginx:alpine as nginx

COPY nginx.conf /etc/nginx/conf.d
COPY --from=builder /app/dist /static/
COPY .env patchNginxConf.sh /
RUN ./patchNginxConf.sh


# JaWannDennJetzt
FROM python:3-slim as backend
WORKDIR /app

ADD manage.py entrypoint.sh requirements.txt dockerBuild.sh .env external/wait-for-it.sh /app/
ADD server /app/server
RUN ./dockerBuild.sh
COPY --from=builder /app/dist /static/
ENTRYPOINT ["/app/entrypoint.sh"]
