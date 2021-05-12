#!/usr/bin/env bash

cd "$(dirname "$0")/.." || exit
docker-compose exec api sh
