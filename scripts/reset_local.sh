#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit

docker-compose stop

docker-compose -f docker-compose.yaml -f override.dev.yaml -f ./api/compose/override.reset.yaml build api && docker-compose -f docker-compose.yaml -f override.dev.yaml -f ./api/compose/override.reset.yaml up api
