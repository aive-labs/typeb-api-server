"""initiliaze GA integration table

Revision ID: 6dd339072495
Revises: ceca92cbab88
Create Date: 2024-11-11 11:19:19.308588

"""

from typing import Sequence, Union

from alembic import op

from src.common.utils.get_env_variable import get_env_variable

# revision identifiers, used by Alembic.
revision: str = "6dd339072495"
down_revision: Union[str, None] = "ceca92cbab88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    ga_account_id = get_env_variable("aace_ga_account_id")
    gtm_account_id = get_env_variable("aace_gtm_account_id")
    op.execute(
        f"""
        INSERT INTO aivelabs_sv.ga_integration (
            mall_id,
            ga_account_id,
            ga_account_name,
            gtm_account_id,
            gtm_account_name,
            created_at,
            updated_at,
            ga_script_status
        ) VALUES (
            'aivelabs',
            '{ga_account_id}',
            'aace-clients',
            '{gtm_account_id}',
            'aace-gtm-clients',
            NOW() AT TIME ZONE 'UTC',
            NOW() AT TIME ZONE 'UTC',
            'pending'
        );
    """
    )


def downgrade():
    # 데이터를 삭제하는 코드를 넣을 수 있습니다 (옵션)
    op.execute(
        """
        DELETE FROM aivelabs_sv.ga_integration
        WHERE mall_id = 'aivelabs'
          AND ga_account_id = 335947243
          AND gtm_account_id = 6257307560;
    """
    )
