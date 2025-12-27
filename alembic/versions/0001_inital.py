from alembic import op
import sqlalchemy as sa

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "cars",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("number", sa.String(length=32), nullable=False),
        sa.Column("brand", sa.String(length=64), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("owner_name", sa.String(length=128), nullable=False),
    )
    op.create_index("ix_cars_number", "cars", ["number"], unique=True)
    op.create_index("ix_cars_brand", "cars", ["brand"])
    op.create_index("ix_cars_year", "cars", ["year"])
    op.create_index("ix_cars_owner_name", "cars", ["owner_name"])

    op.create_table(
        "mechanics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("employee_no", sa.String(length=32), nullable=False),
        sa.Column("full_name", sa.String(length=128), nullable=False),
        sa.Column("experience_years", sa.Integer(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
    )
    op.create_index("ix_mechanics_employee_no", "mechanics", ["employee_no"], unique=True)
    op.create_index("ix_mechanics_full_name", "mechanics", ["full_name"])
    op.create_index("ix_mechanics_experience_years", "mechanics", ["experience_years"])
    op.create_index("ix_mechanics_grade", "mechanics", ["grade"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("car_id", sa.Integer(), sa.ForeignKey("cars.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mechanic_id", sa.Integer(), sa.ForeignKey("mechanics.id", ondelete="CASCADE"), nullable=False),
        sa.Column("cost", sa.Numeric(12, 2), nullable=False),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("work_type", sa.String(length=128), nullable=False),
        sa.Column("planned_end_date", sa.Date(), nullable=False),
        sa.Column("actual_end_date", sa.Date(), nullable=True),
    )

    op.create_index("ix_orders_car_id", "orders", ["car_id"])
    op.create_index("ix_orders_mechanic_id", "orders", ["mechanic_id"])
    op.create_index("ix_orders_cost", "orders", ["cost"])
    op.create_index("ix_orders_issue_date", "orders", ["issue_date"])
    op.create_index("ix_orders_work_type", "orders", ["work_type"])
    op.create_index("ix_orders_planned_end_date", "orders", ["planned_end_date"])
    op.create_index("ix_orders_actual_end_date", "orders", ["actual_end_date"])

def downgrade():
    op.drop_table("orders")
    op.drop_table("mechanics")
    op.drop_table("cars")
