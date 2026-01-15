#!/bin/sh

if [ -f migrate.sh ]; then
    chmod +x ./migrate.sh
    ./migrate.sh
fi

exec uvicorn main:app \
  --host ${FASTAPI_HOST} \
  --port ${FASTAPI_PORT} \
  --workers ${UVICORN_WORKERS}
