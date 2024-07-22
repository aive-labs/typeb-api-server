import requests
from requests.auth import HTTPBasicAuth

from src.common.utils.get_env_variable import get_env_variable


class MessageReserveController:
    def __init__(self):
        self.airflow_api = airflow_api = get_env_variable("airflow_api")
        self.airflow_username = username = get_env_variable("airflow_username")
        self.airflow_password = password = get_env_variable("airflow_password")

    def execute_dag(self, dag_name, input_vars):
        """Airflow DAG에 메시지 전송 요청을 보냅니다.
        dag_name: Airflow DAG 이름
        input_vars: 전달하고자 하는 JSON 데이터
        """

        # POST 요청 데이터
        data = {"conf": input_vars}

        # POST 요청 보내기
        response = requests.post(
            url=f"{self.airflow_api}/dags/{dag_name}/dagRuns",
            auth=HTTPBasicAuth(self.airflow_username, self.airflow_password),
            json=data,
        )

        return response.text
