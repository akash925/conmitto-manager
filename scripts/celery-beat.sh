#!/usr/bin/env bash
cd "$(dirname "$0")/.." || exit
docker-compose -f docker-compose-dev.yaml build celery-beat && docker-compose -f docker-compose-dev.yaml up celery-beat
