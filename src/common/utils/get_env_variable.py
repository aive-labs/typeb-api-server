import os

from dotenv import load_dotenv


def get_env_variable(key: str) -> str:
    env_type = os.getenv("ENV_TYPE")

    env_files = {
        None: "config/env/.env",
        "test_code": "config/env/test.env",
        "nepa-stg": "config/env/local_nepa.env",
    }
    env_file = env_files.get(env_type, f"config/env/{env_type}.env")
    load_dotenv(env_file)

    value = os.getenv(key)

    if value is None:
        raise KeyError("설정 파일에 해당하는 값이 없습니다.")

    return value
