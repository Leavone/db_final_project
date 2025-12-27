from alembic import op

revision = "0003_indexes_and_pg_trgm"
down_revision = "0002_add_status_and_meta"
branch_labels = None
depends_on = None

def upgrade():
    # required for gin_trgm_ops
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm;")

    # composite index example
    op.create_index("ix_orders_work_type_issue_date", "orders", ["work_type", "issue_date"])

    # GIN + pg_trgm index over meta::text (JSONB field)
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_orders_meta_trgm "
        "ON orders USING GIN ((meta::text) gin_trgm_ops);"
    )

def downgrade():
    op.execute("DROP INDEX IF EXISTS ix_orders_meta_trgm;")
    op.drop_index("ix_orders_work_type_issue_date", table_name="orders")
