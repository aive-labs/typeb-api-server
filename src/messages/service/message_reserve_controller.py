import aiohttp
from aiohttp import BasicAuth
from fastapi import HTTPException

from src.common.utils.get_env_variable import get_env_variable


class MessageReserveController:
    def __init__(self):
        self.airflow_api = get_env_variable("airflow_api")
        self.airflow_username = get_env_variable("airflow_username")
        self.airflow_password = get_env_variable("airflow_password")

    async def execute_dag(
        self, dag_name, input_vars, dag_run_id: str | None = None, logical_date: str | None = None
    ):
        """Airflow DAG에 메시지 전송 요청을 보냅니다.
        dag_name: Airflow DAG 이름
        input_vars: 전달하고자 하는 JSON 데이터
        """

        # POST 요청 데이터
        data = {"conf": input_vars}

        if dag_run_id:
            data["dag_run_id"] = dag_run_id

        if logical_date:
            data["logical_date"] = logical_date

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"{self.airflow_api}/dags/{dag_name}/dagRuns",
                json=data,
                auth=BasicAuth(self.airflow_username, self.airflow_password),
                ssl=False,
            ) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail={"code": "airflow call error", "message": response.text},
                    )
                response = await response.json()
                return response
