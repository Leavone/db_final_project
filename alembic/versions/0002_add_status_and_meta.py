from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_add_status_and_meta"
down_revision = "0001_initial"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("orders", sa.Column("status", sa.String(length=32), server_default="new", nullable=False))
    op.add_column("orders", sa.Column("meta", postgresql.JSONB(), server_default=sa.text("'{}'::jsonb"), nullable=False))
    op.create_index("ix_orders_status", "orders", ["status"])

def downgrade():
    op.drop_index("ix_orders_status", table_name="orders")
    op.drop_column("orders", "meta")
    op.drop_column("orders", "status")
