#!/usr/bin/env bash
set -e

DB_NAME="${DB_NAME:-autoservice}"
DB_USER="${DB_USER:-autoservice_owner}"
DB_PASS="${DB_PASS:-autoservice_pass}"

# запускать: psql -U postgres -f ...  ИЛИ внутри контейнера postgres
psql -U postgres <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;

DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_database WHERE datname = '${DB_NAME}') THEN
    CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};
  END IF;
END
\$\$;

GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};
SQL
