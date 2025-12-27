
# Autoservice REST API

Simple REST API for an autoservice domain, built with **FastAPI**, **SQLAlchemy**, **Alembic**, and **PostgreSQL**.  
The project satisfies all requirements of the DBMS assignment, including CRUD, migrations, analytics queries, JSONB search, and pagination.

---

## Tech stack

- Python 3.12
- FastAPI
- SQLAlchemy 2.0
- Alembic
- PostgreSQL 16
- Docker / Docker Compose

---

## How to run

### 1. Start containers

```bash
docker-compose up --build -d
````

API will be available at:

```
http://localhost:5400
```

Swagger UI:

```
http://localhost:5400/docs
```

---

### 2. Install psql client in API container (one time)

```bash
docker-compose exec -u 0 api bash -lc "apt-get update && apt-get install -y postgresql-client"
```

---

### 3. Initialize database and owner

Creates:

* database `autoservice`
* owner role `autoservice_owner`

```bash
docker-compose exec -e PGPASSWORD=postgres api bash -lc "scripts/init_db.sh"
```

---

### 4. Run migrations

```bash
docker-compose exec api bash -lc "PYTHONPATH=/app alembic -c /app/alembic.ini upgrade head"
```

Check current revision:

```bash
docker-compose exec api bash -lc "PYTHONPATH=/app alembic -c /app/alembic.ini current"
```

---

### 5. Restart API

```bash
docker-compose restart api
```

---

### 6. Seed database via REST API

This script inserts a large amount of data **only through HTTP requests**.

```bash
python3 scripts/seed_via_api.py
```

---

## CRUD API (criterion 2)

CRUD is implemented for all main entities:

* Cars: `/cars`
* Mechanics: `/mechanics`
* Orders: `/orders`

Supported operations:

* `POST`
* `GET` (list and by id)
* `PUT`
* `DELETE`

All list endpoints support pagination and sorting.

---

## Migrations (criterion 4)

At least two migrations are implemented:

1. **Add new columns**

   * `status` (string)
   * `meta` (JSONB)

2. **Indexes and extensions**

   * `pg_trgm` extension
   * `GIN + gin_trgm_ops` index on `orders.meta::text`
   * additional composite indexes

Migration files are located in:

```
alembic/versions/
```

---

## Analytics API (criterion 5)

All complex queries are implemented as REST endpoints and available in Swagger UI.

### 1. SELECT with multiple WHERE conditions

```
GET /analytics/orders/filter
```

Example parameters:

* `brand`
* `min_cost`
* `max_cost`
* `grade_gte`
* `issue_from`
* `issue_to`
* `sort_by`
* `sort_dir`
* `limit`
* `offset`

---

### 2. JOIN query

```
GET /analytics/orders/with-details
```

Returns orders joined with:

* cars
* mechanics

---

### 3. UPDATE with non-trivial condition

```
POST /analytics/orders/close-overdue
```

Logic:

```sql
UPDATE orders
SET status = 'done'
WHERE actual_end_date IS NOT NULL
  AND actual_end_date > planned_end_date;
```

---

### 4. GROUP BY query

```
GET /analytics/revenue/by-mechanic
```

Aggregates:

* total revenue per mechanic
* number of orders

---

### 5. Sorting via API parameters

Sorting is supported using:

* `sort_by`
* `sort_dir`

Available in all list and analytics endpoints.

---

## JSONB + pg_trgm + regex search (criterion 6)

### JSON field

* `orders.meta` (JSONB)
* Filled with structured data during seeding

### Index

* `GIN ((meta::text) gin_trgm_ops)`
* `pg_trgm` extension enabled via migration

### Regex search via REST API

```
GET /analytics/orders/search-meta
```

Example patterns:

* `urgent`
* `noise`
* `urgent|noise`
* `client note #[0-9]+`

Internally uses PostgreSQL regex operator:

```sql
meta::text ~ '<pattern>'
```

---

## Pagination (criterion 7)

Pagination is implemented using:

* `limit`
* `offset`

Available in:

* `/cars`
* `/mechanics`
* `/orders`
* `/analytics/orders/filter`
* `/analytics/orders/with-details`
* `/analytics/orders/search-meta`

Example:

```
GET /orders?limit=10&offset=20
```

