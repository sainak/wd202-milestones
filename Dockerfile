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
  && apk add --no-cache postgresql-dev

RUN python -m pip install --upgrade pipenv wheel

WORKDIR ${APP_HOME}

RUN groupadd -r web && useradd -d ${APP_HOME} -r -g web web \
  && chown web:web -R ${APP_HOME} \
  && mkdir -p /var/www/django/static /var/www/django/media \
  && chown web:web /var/www/django/static /var/www/django/media

COPY --chown=web:web ./Pipenv ./Pipenv.lock ${APP_HOME}

RUN pipenv install --system --deploy --ignore-pipfile --clear

USER web

# App
FROM base AS app

COPY --chown=web:web . ${APP_HOME}

RUN python ./manage.py tailwind install \
  python ./manage.py tailwind build

COPY --chown=web:web ./scripts /app
RUN chmod +x start-celery-worker start-celery-beat start-django
