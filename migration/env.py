# env.py
import importlib
import os

# env.py
import pkgutil
from logging.config import fileConfig

import psycopg2
from alembic import context
from sqlalchemy import engine_from_config, pool, text

from src.common.utils.get_env_variable import get_env_variable
from src.core.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def import_all_modules(package_name):
    """주어진 패키지의 모든 서브 모듈을 임포트합니다."""
    package = importlib.import_module(package_name)
    for _, name, _ in pkgutil.walk_packages(package.__path__, package_name + "."):
        importlib.import_module(name)


# src 패키지 내의 모든 모듈 임포트, 엔티티를 문제없이 읽기 위해 실행
import_all_modules("src")


def get_db_list_for_migration() -> list:
    user_db_conn = psycopg2.connect(
        dbname=get_env_variable("user_db_name"),
        user=get_env_variable("user_db_user"),
        password=get_env_variable("user_db_password"),
        host=get_env_variable("user_db_host"),
        port=get_env_variable("user_db_port"),
    )

    with user_db_conn.cursor() as cursor:
        cursor.execute("select distinct mall_id from public.clients")
        result = cursor.fetchall()
        mall_ids = [row[0] for row in result]

    user_db_conn.close()

    target_db_name = os.getenv("TARGET_DB_NAME")
    if target_db_name:
        mall_ids = [mall_id for mall_id in mall_ids if mall_id == target_db_name]

    return [
        f"{get_env_variable('prefix_db_url')}/{'aivelabsdb' if mall_id == 'aivelabs' else mall_id}"
        for mall_id in mall_ids
    ]


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object.schema == target_metadata.schema
    else:
        return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    db_urls = get_db_list_for_migration()
    print("🔅DB MIGRATION TARGET")
    for db_url in db_urls:
        print(
            "---------------------------------------------------------------------------------------------------------"
        )
        print(f"✅ {db_url} / schema: {target_metadata.schema} ✅")
        # print(f"tables: {target_metadata.tables.keys()}")

        mall_id = db_url.split("/")[-1]
        config.set_main_option("sqlalchemy.url", db_url)
        config.set_main_option("version_locations", f"migration/versions/{mall_id}/schemas")
        config.set_main_option("script_location", "migration")
        section = config.get_section(config.config_ini_section)

        # 데이터베이스마다 연결하고 마이그레이션 실행
        connectable = engine_from_config(
            section,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                version_table_schema=target_metadata.schema,
                include_object=include_object,
            )

            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {target_metadata.schema}"))

            with context.begin_transaction():
                context.run_migrations()


run_migrations_online()
