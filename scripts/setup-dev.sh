#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit
docker-compose -f docker-compose.yaml exec api python manage.py initadmin --setting=config.settings.dev;
docker-compose -f docker-compose.yaml exec api python manage.py create_test_org --setting=config.settings.dev;

