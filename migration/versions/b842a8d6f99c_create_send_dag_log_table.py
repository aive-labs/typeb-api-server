"""create send_dag_log table

Revision ID: b842a8d6f99c
Revises:
Create Date: 2024-08-06 17:53:36.175669

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "b842a8d6f99c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    # 테이블 생성
    op.create_table(
        "send_dag_log",
        sa.Column("campaign_id", sa.String(length=20), nullable=False),
        sa.Column("send_resv_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("dag_run_id", sa.String, nullable=False),
    )


def downgrade() -> None:
    # 테이블 삭제
    op.drop_table("send_dag_log")
