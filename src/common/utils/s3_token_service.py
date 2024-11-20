import re
from datetime import datetime
from io import StringIO

import boto3
import pytz
import yaml

from src.core.exceptions.exceptions import Cafe24Exception, ValidationException


class S3TokenService:
    def __init__(self, bucket: str, key: str):
        self.s3_client = boto3.client("s3")
        self.bucket = bucket
        self.key = key

    def create_and_upload_yaml(self, data: dict):
        """
        Create a YAML file from a dictionary and upload it to S3.

        :param data: Dictionary to save as YAML.
        :param mallid: mallid
        """
        # Convert dictionary to YAML string
        yaml_content = yaml.dump(data, default_flow_style=False)

        # Use a StringIO buffer to simulate a file for uploading
        yaml_buffer = StringIO(yaml_content)

        # Upload the YAML file to the specified S3 path
        self.s3_client.put_object(
            Bucket=self.bucket,
            Key=self.key,
            Body=yaml_buffer.getvalue(),
        )

    def insert_csv(self, csv_buffer):
        self.s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=csv_buffer.getvalue())

    def upload_file(self, local_file_name, bucket_name, s3_file_name):
        self.s3_client.upload_file(local_file_name, bucket_name, s3_file_name)

    def read_access_token(self):
        try:
            # S3에서 파일 가져오기
            response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
            file_content = response["Body"].read().decode("utf-8")

            # YAML 파일 파싱
            data = yaml.safe_load(file_content)

            # access_token_expired_at과 access_token 가져오기
            mall_id = self.extract_mall_id()
            expired_at_str = data.get(mall_id, {}).get("access_token_expired_at")
            access_token = data.get(mall_id, {}).get("access_token")

            if not expired_at_str or not access_token:
                raise Cafe24Exception(detail={"message": "카페24 연동 정보가 존재하지 않습니다."})

            # access_token_expired_at을 한국 시간으로 파싱
            expired_at = datetime.strptime(expired_at_str, "%Y-%m-%d %H:%M:%S")
            korea_tz = pytz.timezone("Asia/Seoul")

            # 현재 시간을 한국 시간대로 가져오기
            current_time = datetime.now(korea_tz)

            if current_time > expired_at:
                raise Cafe24Exception(
                    detail={"message": "결저 요청에 실패했습니다. 잠시 후에 다시 시도해주세요."}
                )

            return access_token
        except Exception as e:
            raise Cafe24Exception(
                detail={"message": "결저 요청에 실패했습니다. 잠시 후에 다시 시도해주세요."}
            )

    def extract_mall_id(self):
        # 정규식을 사용하여 mall_id 추출
        pattern = r"cafe24_token/([^/]+)\.yml"
        match = re.search(pattern, self.key)

        if match:
            return match.group(1)  # 첫 번째 그룹 반환
        else:
            raise ValidationException(detail={"message": "카페24 요청 중 오류가 발생했습니다."})
