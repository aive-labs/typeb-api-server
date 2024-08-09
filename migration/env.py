from logging.config import fileConfig

import psycopg2
from alembic import context
from sqlalchemy import create_engine, pool

from src.common.utils.get_env_variable import get_env_variable
from src.core.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

user_db_conn = psycopg2.connect(
    dbname=get_env_variable("user_db_name"),
    user=get_env_variable("user_db_user"),
    password=get_env_variable("user_db_password"),
    host=get_env_variable("user_db_host"),
    port=get_env_variable("user_db_port"),
)


def get_db_list_for_migration() -> list:
    with user_db_conn.cursor() as cursor:
        cursor.execute("select distinct mall_id from public.clients")
        result = cursor.fetchall()
        mall_ids = [row[0] for row in result]
    return [f"{get_env_variable('prefix_db_url')}/{mall_id}" for mall_id in mall_ids]


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    db_urls = get_db_list_for_migration()
    print("🔅DB MIGRATION TARGET")
    for db_url in db_urls:
        connectable = create_engine(db_url, poolclass=pool.NullPool)
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                version_table_schema=target_metadata.schema,
                include_schemas=True,
            )

            with context.begin_transaction():
                context.execute(f"SET search_path TO {target_metadata.schema}")
                context.run_migrations()

        print(f"✅ {db_url}")


run_migrations_online()
