import aiohttp
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth

from src.common.utils.get_env_variable import get_env_variable


class MessageReserveController:
    def __init__(self):
        self.airflow_api = get_env_variable("airflow_api")
        self.airflow_username = get_env_variable("airflow_username")
        self.airflow_password = get_env_variable("airflow_password")

    async def execute_dag(self, dag_name, input_vars):
        """Airflow DAG에 메시지 전송 요청을 보냅니다.
        dag_name: Airflow DAG 이름
        input_vars: 전달하고자 하는 JSON 데이터
        """

        # POST 요청 데이터
        data = {"conf": input_vars}

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.airflow_api}/dags/{dag_name}/dagRuns",
                data=data,
                auth=HTTPBasicAuth(self.airflow_username, self.airflow_password),
                ssl=False,
            ) as response:
                response = await response.json()

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=response.status_code,
                        detail={"code": "airflow call error", "message": response.text},
                    )

                return response
