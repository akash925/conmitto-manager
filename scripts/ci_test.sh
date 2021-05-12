#!/bin/sh

cd "$(dirname "$0")/.." || exit
if docker ps | grep --quiet conmitto-web_db; then
  echo 'killing dev containers'
  docker-compose -f docker-compose-dev.yaml stop
fi

if docker ps | grep --quiet django_server; then
  echo 'killing django server'
  docker-compose stop api
fi

docker-compose -f test.yaml build api && docker-compose -f test.yaml up -d api
