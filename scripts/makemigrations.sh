#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit
docker-compose -f docker-compose.yaml -f override.dev.yaml exec api python manage.py makemigrations --setting=config.settings.dev;
docker-compose -f docker-compose.yaml -f override.dev.yaml exec api python manage.py migrate --setting=config.settings.dev;

