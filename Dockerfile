FROM python:3.12-alpine

ENV TZ=America/New_York

WORKDIR /app

COPY requirements.txt /app/requirements.txt

RUN addgroup app \
  && adduser -S -g app app \
  && apk update \
  && apk add --no-cache bash tzdata mariadb-connector-c-dev \
  && apk add --no-cache --virtual .build-deps gcc libffi-dev openssl-dev musl-dev mariadb-dev \
  && python -m pip install -r requirements.txt \
  && chown -R app:app /app \
  && apk del .build-deps

COPY --chown=app:app . .

USER app
EXPOSE 8000

ENTRYPOINT ["bash", "entrypoint.sh"]