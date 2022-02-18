#!/bin/sh

set -o errexit
set -o pipefail
set -o nounset

PROC=${PROC_TYPE:="none"}

if [ "$PROC" == "worker" ]; then
    exec celery -A task_manager worker -l INFO
elif [ "$PROC" == "beat" ]; then
    exec celery -A task_manager beat -l INFO
elif [ "$PROC" == "django" ]; then
    python manage.py migrate --noinput
    python manage.py tailwind install
    python manage.py tailwind build
    python manage.py collectstatic --noinput

    gunicorn task_manager.wsgi --bind 0.0.0.0:8000 --chdir=/app
else
    until [ "$PROC" == "django" ] || [ "$PROC" == "worker" ] || [ "$PROC" == "beat" ]; do
        echo "Unknown PROC_TYPE: $PROC"
        sleep 1
    done
fi
