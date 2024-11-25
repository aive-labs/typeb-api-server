"""add actual_amt column to purchase_analytis_master_style

Revision ID: 502d9913b4ef
Revises: 20a7debd99c9
Create Date: 2024-11-25 11:39:34.365703

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "502d9913b4ef"
down_revision: Union[str, None] = "20a7debd99c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "purchase_analytics_master_style",
        sa.Column("actual_amt", sa.Integer(), nullable=True),
        schema="aivelabs_sv",
    )


def downgrade() -> None:
    op.drop_column(
        "purchase_analytics_master_style",
        "actual_amt",
        schema="aivelabs_sv",
    )
