"""alter column name in dashboard tables

Revision ID: 79ede840a3cf
Revises: 228a55ff2bfe
Create Date: 2024-11-29 10:04:05.680156

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "79ede840a3cf"
down_revision: Union[str, None] = "228a55ff2bfe"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 컬럼 이름 변경
    op.execute(
        """
        ALTER TABLE aivelabs_sv.dash_daily_send_info
        RENAME COLUMN cust_grade1 TO group_no;
    """
    )

    op.execute(
        """
            ALTER TABLE aivelabs_sv.dash_daily_send_info
            RENAME COLUMN cust_grade1_nm TO group_name;
        """
    )

    # 컬럼 이름 변경
    op.execute(
        """
        ALTER TABLE aivelabs_sv.dash_end_table
        RENAME COLUMN cust_grade1 TO group_no;
    """
    )

    op.execute(
        """
            ALTER TABLE aivelabs_sv.dash_end_table
            RENAME COLUMN cust_grade1_nm TO group_name;
        """
    )


def downgrade() -> None:
    # 컬럼 이름 변경
    op.execute(
        """
        ALTER TABLE aivelabs_sv.dash_daily_send_info
        RENAME COLUMN group_no TO cust_grade1;
    """
    )

    op.execute(
        """
            ALTER TABLE aivelabs_sv.dash_daily_send_info
            RENAME COLUMN group_name TO cust_grade1_nm;
        """
    )

    # 컬럼 이름 변경
    op.execute(
        """
        ALTER TABLE aivelabs_sv.dash_end_table
        RENAME COLUMN group_no TO cust_grade1;
    """
    )

    op.execute(
        """
            ALTER TABLE aivelabs_sv.dash_end_table
            RENAME COLUMN group_name TO cust_grade1_nm;
        """
    )
