#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit
docker-compose -f docker-compose.yaml -f override.test.yaml exec -T api python manage.py flush --no-input
docker-compose -f docker-compose.yaml -f override.test.yaml exec -T api python manage.py create_test_org
