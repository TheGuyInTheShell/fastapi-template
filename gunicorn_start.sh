#!/bin/bash

NAME=fastapi-app
DIR=/path/to/app/directory
USER=user
GROUP=group
WORKERS=2
WORKER_CLASS=uvicorn.workers.UvicornWorker
VENV=$DIR/.venv/bin/activate
BIND=unix:$DIR/run/gunicorn.sock
LOG_LEVEL=error

cd $DIR
source /path/to/env/bin/activate

exec gunicorn ${NAME}:app \
    --workers $WORKERS \
    --worker-class $WORKER_CLASS \
    --bind $BIND \
    --log-level $LOG_LEVEL \
    --log-file \
    --access-logfile \
    --error-logfile \
    --capture-output \
    --daemon \
    --pid /path/to/pid/file \
    --user $USER \
    --group $GROUP \
    --threads 2 \
    --timeout 300 \
    --reload \
    --access-logfile \
    --error-logfile \
