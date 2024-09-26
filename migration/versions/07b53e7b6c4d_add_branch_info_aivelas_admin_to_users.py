"""add branch info, aivelas_admin to users

Revision ID: 07b53e7b6c4d
Revises: 18e76296ab60
Create Date: 2024-09-26 14:15:30.823036

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "07b53e7b6c4d"
down_revision: Union[str, None] = "18e76296ab60"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("brand_name_ko", sa.String(100)), schema="aivelabs_sv")
    op.add_column("users", sa.Column("bran_name_en", sa.String(100)), schema="aivelabs_sv")
    op.add_column("users", sa.Column("is_aivelabs_admin", sa.Boolean), schema="aivelabs_sv")


def downgrade() -> None:
    op.drop_column("users", "brand_name_ko", schema="aivelabs_sv")
    op.drop_column("users", "bran_name_en", schema="aivelabs_sv")
    op.drop_column("users", "is_aivelabs_admin", schema="aivelabs_sv")
