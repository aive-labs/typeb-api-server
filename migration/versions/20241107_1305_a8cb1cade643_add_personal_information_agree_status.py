"""add personal_information_agree_status

Revision ID: a8cb1cade643
Revises: 349ffebc5779
Create Date: 2024-11-07 10:50:27.981601

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a8cb1cade643"
down_revision: Union[str, None] = "349ffebc5779"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "outsourcing_personal_information_status",
        sa.Column("term_status", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_by", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("term_status"),
        schema="aivelabs_sv",
    )


def downgrade() -> None:
    op.drop_table("outsourcing_personal_information_status", schema="aivelabs_sv")
