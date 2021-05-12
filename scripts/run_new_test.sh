#!/usr/bin/env bash

# Use this to configure whatever backend test you need to run over and over again
cd "$(dirname "$0")/.." || exit
docker-compose -f test.yaml exec -T api python manage.py test api.warehouse.pallets --tag=incoming
