#!/bin/bash

set -e

echo "Запускаем миграции..."

SYNC_URL=${DATABASE_URL/+asyncpg/+psycopg2}

DATABASE_URL=${SYNC_URL} alembic -c app/infrastructure/database/alembic.ini upgrade head

echo "Миграции выполнены"