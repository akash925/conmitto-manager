#!/bin/bash -xe

# Mainly used for passing -d so that the container can be run in detached mode
EXTRA_FLAGS=$1

cd "$(dirname "$0")/.." || exit
#if docker ps | grep --quiet conmitto-web_test_db; then
#  echo 'killing test containers'
#  docker-compose -f test.yaml stop
#fi
#if docker ps | grep --quiet conmitto-web_db; then
#  echo 'killing dev containers'
#  docker-compose -f docker-compose-dev.yaml stop
#fi
#
#if docker ps | grep --quiet django_server; then
#  echo 'killing django server'
#  docker-compose stop api
#fi

if [ -z "$EXTRA_FLAGS" ]; then
    docker-compose -f docker-compose.yaml -f override.dev.yaml build api && docker-compose -f docker-compose.yaml -f override.dev.yaml  up api
else
    docker-compose -f docker-compose.yaml -f override.dev.yaml  build api && docker-compose -f docker-compose.yaml -f override.dev.yaml  up "${EXTRA_FLAGS}" api
fi
