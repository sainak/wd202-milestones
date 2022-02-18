ARG PYTHON_VERSION=3.10-alpine

FROM python:${PYTHON_VERSION} as base

ARG APP_HOME=/app
ARG BUILD_ENV=production

ENV BUILD_ENV=${BUILD_ENV} \
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100

RUN apk update \
  && apk upgrade \
  && apk add --no-cache postgresql-dev npm

RUN python -m pip install --upgrade pipenv wheel

WORKDIR ${APP_HOME}

RUN addgroup -S web && adduser -h ${APP_HOME} -S web web \
  && chown web:web -R ${APP_HOME} \
  && mkdir -p /var/www/django/static /var/www/django/media \
  && chown web:web /var/www/django/static /var/www/django/media

COPY --chown=web:web ./Pipfile ./Pipfile.lock ${APP_HOME}/

RUN pipenv install --system --deploy --ignore-pipfile --clear

USER web

# App
FROM base AS app

COPY --chown=web:web . ${APP_HOME}

RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT [ "./docker-entrypoint.sh" ]
