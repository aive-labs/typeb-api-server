"""add send_date column to dash_daily_send_info

Revision ID: 228a55ff2bfe
Revises: 21a121512d5a
Create Date: 2024-11-28 09:58:28.286154

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "228a55ff2bfe"
down_revision: Union[str, None] = "21a121512d5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "dash_daily_send_info",
        sa.Column("send_date", sa.String(), nullable=True),
        schema="aivelabs_sv",
    )


def downgrade() -> None:
    op.drop_column(
        "dash_daily_send_info",
        "send_date",
        schema="aivelabs_sv",
    )
