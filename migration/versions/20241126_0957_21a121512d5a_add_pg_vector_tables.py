"""add pg_vector tables

Revision ID: 21a121512d5a
Revises: 502d9913b4ef
Create Date: 2024-11-26 09:57:12.594924

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "21a121512d5a"
down_revision: Union[str, None] = "502d9913b4ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Activate VECTOR Extension
    op.execute(
        """
        CREATE EXTENSION IF NOT EXISTS vector SCHEMA aivelabs_sv;
        """
    )

    # CREATE langchain_pg_collection table
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS aivelabs_sv.langchain_pg_collection (
            name VARCHAR,
            cmetadata JSON,
            uuid UUID NOT NULL PRIMARY KEY
        );
    """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS langchain_pg_collection_pkey
        ON aivelabs_sv.langchain_pg_collection (uuid);
    """
    )

    # CREATE langchain_pg_embedding table
    op.execute(
        """
            CREATE TABLE IF NOT EXISTS aivelabs_sv.langchain_pg_embedding (
                collection_id UUID REFERENCES aivelabs_sv.langchain_pg_collection
                    ON DELETE CASCADE,
                embedding aivelabs_sv.VECTOR,
                document VARCHAR,
                cmetadata JSON,
                custom_id VARCHAR,
                uuid UUID NOT NULL PRIMARY KEY
            );
        """
    )

    # Create unique index for primary key
    op.execute(
        """
            CREATE UNIQUE INDEX IF NOT EXISTS langchain_pg_embedding_pkey
            ON aivelabs_sv.langchain_pg_embedding (uuid);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS langchain_pg_collection_pkey;
    """
    )
    op.execute(
        """
        DROP TABLE IF EXISTS aivelabs_sv.langchain_pg_collection;
    """
    )

    op.execute(
        """
           DROP INDEX IF EXISTS langchain_pg_embedding_pkey;
       """
    )
    op.execute(
        """
           DROP TABLE IF EXISTS aivelabs_sv.langchain_pg_embedding;
       """
    )
