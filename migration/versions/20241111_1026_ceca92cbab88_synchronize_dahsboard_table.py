"""synchronize dahsboard table

Revision ID: ceca92cbab88
Revises: a8cb1cade643
Create Date: 2024-11-11 10:26:50.054080

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine import reflection

# revision identifiers, used by Alembic.
revision: str = "ceca92cbab88"
down_revision: Union[str, None] = "a8cb1cade643"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 데이터베이스 연결 가져오기
    conn = op.get_bind()
    inspector = reflection.Inspector.from_engine(conn)

    # 테이블 존재 여부 확인
    if "send_message_logs" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'send_message_logs' already exists. Skipping creation.")
    else:
        op.create_table(
            "send_message_logs",
            sa.Column("refkey", sa.String(100), nullable=False),
            sa.Column("http_status_code", sa.Integer, nullable=False),
            sa.Column("ppurio_messagekey", sa.String(2000), nullable=True),
            sa.Column("http_request_body", sa.String(), nullable=True),
            sa.Column("ppurio_status_code", sa.Integer, nullable=True),
            sa.Column(
                "created_at",
                sa.TIMESTAMP(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=True,
            ),
            sa.Column("send_resv_seq", sa.Integer, nullable=True),
            sa.PrimaryKeyConstraint("refkey", "http_status_code", name="send_message_logs_pkey"),
            schema="aivelabs_sv",
        )

    if "campaign_customer_snapshot" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'campaign_customer_snapshot' already exists. Skipping creation.")
    else:
        op.create_table(
            "campaign_customer_snapshot",
            sa.Column("cus_cd", sa.String, primary_key=True, nullable=False),
            sa.Column("campaign_id", sa.String(10), primary_key=True, nullable=False),
            sa.Column("campaign_name", sa.String, nullable=False),
            sa.Column("send_date", sa.String, nullable=False),
            sa.Column("start_date", sa.String, nullable=False),
            sa.Column("end_date", sa.String, nullable=False),
            sa.Column("campaign_status_name", sa.String, nullable=True),
            sa.Column("campaign_group_id", sa.String, nullable=True),
            sa.Column("strategy_id", sa.String, nullable=True),
            sa.Column("strategy_name", sa.String, nullable=True),
            sa.Column("group_sort_num", sa.Integer, nullable=True),
            sa.Column("strategy_theme_id", sa.Integer, nullable=True),
            sa.Column("strategy_theme_name", sa.String, nullable=True),
            sa.Column("audience_id", sa.String, nullable=False),
            sa.Column("audience_name", sa.String, nullable=False),
            sa.Column("coupon_no", sa.String, nullable=True),
            sa.Column("coupon_name", sa.String, nullable=True),
            sa.Column("age_group_10", sa.String, nullable=True),
            sa.Column("group_no", sa.BigInteger, nullable=True),
            sa.Column("group_name", sa.String, nullable=True),
            sa.Column("cv_lv2", sa.String, nullable=True),
            sa.Column("recsys_model_id", sa.Integer, nullable=True),
            sa.Column("recsys_model_name", sa.String, nullable=True),
            sa.Column("etltime", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("cus_cd", "campaign_id"),
            schema="aivelabs_sv",
        )

    if "dash_daily_campaign_cost" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'dash_daily_campaign_cost' already exists. Skipping creation.")
    else:
        op.create_table(
            "dash_daily_campaign_cost",
            sa.Column("cus_cd", sa.String, nullable=False),
            sa.Column("campaign_id", sa.String(10), nullable=False),
            sa.Column("send_resv_date", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.Column("sent_success", sa.Text, nullable=True),
            sa.Column("media", sa.Text, nullable=True),
            sa.Column("cost_per_send", sa.Float, nullable=True),
            sa.Column("etltime", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint("cus_cd", "campaign_id"),
            schema="aivelabs_sv",
        )

    if "dash_daily_date_ranges" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'dash_daily_date_ranges' already exists. Skipping creation.")
    else:
        op.create_table(
            "dash_daily_date_ranges",
            sa.Column("seq", sa.Text, nullable=True),
            sa.Column("sale_dt", sa.Text, nullable=True),
            sa.Column("campaign_id", sa.String(10), nullable=True),
            sa.Column("campaign_name", sa.Text, nullable=True),
            sa.Column("actual_start_date", sa.Text, nullable=True),
            sa.Column("send_date", sa.Text, nullable=True),
            sa.Column("start_date", sa.Text, nullable=True),
            sa.Column("end_date", sa.Text, nullable=True),
            sa.Column("campaign_status_name", sa.Text, nullable=True),
            sa.Column("group_sort_num", sa.Integer, nullable=True),
            sa.Column("strategy_theme_id", sa.Integer, nullable=True),
            sa.Column("strategy_theme_name", sa.Text, nullable=True),
            sa.Column("strategy_id", sa.String, nullable=True),
            sa.Column("strategy_name", sa.Text, nullable=True),
            sa.Column("audience_id", sa.String, nullable=True),
            sa.Column("audience_name", sa.Text, nullable=True),
            sa.Column("coupon_no", sa.String, nullable=True),
            sa.Column("coupon_name", sa.Text, nullable=True),
            sa.Column("media", sa.Text, nullable=True),
            sa.Column("etltime", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint(
                "campaign_id",
                "audience_id",
                "media",
                "sale_dt",
            ),
            schema="aivelabs_sv",
        )

    if "dash_daily_purchase_master" in inspector.get_table_names(schema="aivelabs_sv"):
        print("Table 'dash_daily_purchase_master' already exists. Skipping creation.")
    else:
        op.create_table(
            "dash_daily_purchase_master",
            sa.Column("cus_cd", sa.String, nullable=True),
            sa.Column("sale_dt", sa.String, nullable=True),
            sa.Column("recp_no", sa.String, nullable=True),
            sa.Column("order_item_code", sa.String, nullable=True),
            sa.Column("product_name", sa.String, nullable=True),
            sa.Column("category_name", sa.String, nullable=True),
            sa.Column("rep_nm", sa.String, nullable=True),
            sa.Column("coupon_code", sa.String, nullable=True),
            sa.Column("sale_amt", sa.Numeric, nullable=True),
            sa.Column("sale_qty", sa.Numeric, nullable=True),
            sa.Column("etltime", sa.TIMESTAMP(timezone=True), nullable=True),
            sa.PrimaryKeyConstraint(
                "cus_cd",
                "order_item_code",
            ),
            schema="aivelabs_sv",
        )


def downgrade():
    op.drop_table("send_message_logs", schema="aivelabs_sv")

    op.drop_table("campaign_customer_snapshot", schema="aivelabs_sv")

    op.drop_table("dash_daily_campaign_cost", schema="aivelabs_sv")

    op.drop_table("dash_daily_date_ranges", schema="aivelabs_sv")

    op.drop_table("dash_daily_purchase_master", schema="aivelabs_sv")
