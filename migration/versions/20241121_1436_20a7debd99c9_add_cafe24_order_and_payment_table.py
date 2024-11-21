"""add cafe24 order and payment table

Revision ID: 20a7debd99c9
Revises: ceca92cbab88
Create Date: 2024-11-21 14:36:15.433449

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision: str = "20a7debd99c9"
down_revision: Union[str, None] = "ceca92cbab88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)

    # 테이블 존재 여부 확인
    if "cafe24_orders" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'cafe24_orders' already exists. Skipping creation.")
    else:
        op.create_table(
            "cafe24_orders",
            sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
            sa.Column("order_id", sa.String(64), unique=True, nullable=False),
            sa.Column("cafe24_order_id", sa.String(255), nullable=False),
            sa.Column("order_name", sa.String(255), nullable=False),
            sa.Column("order_amount", sa.Float, nullable=False),
            sa.Column("currency", sa.String(20), nullable=False),
            sa.Column("return_url", sa.String, nullable=False),
            sa.Column("automatic_payment", sa.String(4), nullable=False),
            sa.Column("confirmation_url", sa.String, nullable=False),
            sa.Column("created_by", sa.String, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_by", sa.String, nullable=False),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
            ),
            schema="aivelabs_sv",
        )

    if "cafe24_payments" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'cafe24_payments' already exists. Skipping creation.")
    else:
        op.create_table(
            "cafe24_payments",
            sa.Column("order_id", sa.String, primary_key=True, nullable=False),
            sa.Column("payment_status", sa.String, nullable=False),
            sa.Column("title", sa.String, nullable=False),
            sa.Column("approval_no", sa.String, nullable=False),
            sa.Column("payment_gateway_name", sa.String, nullable=False),
            sa.Column("payment_method", sa.String, nullable=False),
            sa.Column("payment_amount", sa.Float, nullable=False),
            sa.Column("refund_amount", sa.Float, nullable=False),
            sa.Column("currency", sa.String, nullable=False),
            sa.Column("locale_code", sa.String, nullable=False),
            sa.Column("automatic_payment", sa.String, nullable=False),
            sa.Column("pay_date", sa.DateTime, nullable=False),
            sa.Column("refund_date", sa.DateTime, nullable=True),
            sa.Column("expiration_date", sa.DateTime, nullable=False),
            sa.Column("created_by", sa.String, nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
            sa.Column("updated_by", sa.String, nullable=False),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.func.now(),
                onupdate=sa.func.now(),
            ),
            schema="aivelabs_sv",
        )


def downgrade():
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)

    # 테이블 존재 여부 확인
    if "cafe24_payments" in inspector.get_table_names(schema="aivelabs_sv"):
        op.drop_table("cafe24_payments", schema="aivelabs_sv")

    if "cafe24_orders" in inspector.get_table_names(schema="aivelabs_sv"):
        op.drop_table("cafe24_orders", schema="aivelabs_sv")
