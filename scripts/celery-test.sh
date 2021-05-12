#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit
docker-compose -f test.yaml build celery && docker-compose -f test.yaml up rabbitmq celery
