#!/bin/sh

exec uvicorn main:app \
  --host ${FASTAPI_HOST} \
  --port ${FASTAPI_PORT} \
  --workers ${UVICORN_WORKERS}
