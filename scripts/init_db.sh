set -e

DB_NAME="${DB_NAME:-autoservice}"
DB_USER="${DB_USER:-autoservice_owner}"
DB_PASS="${DB_PASS:-autoservice_pass}"

PGHOST="${PGHOST:-db}"
PGUSER="${PGUSER:-postgres}"

psql -h "$PGHOST" -U "$PGUSER" -v ON_ERROR_STOP=1 <<SQL
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN PASSWORD '${DB_PASS}';
  END IF;
END
\$\$;
SQL

DB_EXISTS=$(psql -h "$PGHOST" -U "$PGUSER" -tAc "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}'" || true)
if [ "$DB_EXISTS" != "1" ]; then
  psql -h "$PGHOST" -U "$PGUSER" -v ON_ERROR_STOP=1 -c "CREATE DATABASE ${DB_NAME} OWNER ${DB_USER};"
fi

psql -h "$PGHOST" -U "$PGUSER" -d "$DB_NAME" -v ON_ERROR_STOP=1 -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
