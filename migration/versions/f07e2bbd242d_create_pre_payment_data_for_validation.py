"""create pre payment data for validation

Revision ID: f07e2bbd242d
Revises:
Create Date: 2024-08-13 14:01:37.315498

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import BigInteger, Boolean, DateTime, String, func

# revision identifiers, used by Alembic.
revision: str = "f07e2bbd242d"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pre_data_for_validation",
        sa.Column("order_id", String, primary_key=True, nullable=False),
        sa.Column("amount", BigInteger, nullable=False),
        sa.Column("created_by", String, nullable=False),
        sa.Column("created_at", DateTime(timezone=True), default=func.now()),
        sa.Column("updated_by", String, nullable=False),
        sa.Column("updated_at", DateTime(timezone=True), default=func.now()),
        sa.Column("is_deleted", Boolean, nullable=False, default=False),
    )


def downgrade() -> None:
    op.drop_table("pre_data_for_validation")
