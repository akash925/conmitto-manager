#!/usr/bin/env bash
set -e

echo env

POSTGRES="psql --username ${POSTGRES_USER}"

echo "Creating POSTGRES_DB: ${POSTGRES_DB}"
echo "Creating DB_NAME: ${DB_NAME}"

$POSTGRES <<EOSQL
CREATE DATABASE ${DB_NAME} OWNER ${POSTGRES_USER};
CREATE DATABASE test_db OWNER ${POSTGRES_USER};

EOSQL

#echo "Creating schema..."
#psql -d ${DB_NAME} -a -U${POSTGRES_USER} -f /schema.sql
#
#echo "Populating database..."
#psql -d ${DB_NAME} -a  -U${POSTGRES_USER} -f /data.sql