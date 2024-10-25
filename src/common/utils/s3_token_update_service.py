import boto3
import yaml


class S3TokenService:
    def __init__(self, bucket: str, key: str):
        self.s3_client = boto3.client("s3")
        self.bucket = bucket
        self.key = key

    def read_as_dict(self, section: str = None) -> dict:
        response = self.s3_client.get_object(Bucket=self.bucket, Key=self.key)
        content = response["Body"].read().decode("utf-8")
        yaml_dict = yaml.safe_load(content)
        return yaml_dict[section] if section else yaml_dict

    def update_dict(self, section: str, new_data_dict: dict):
        existing_data = self.read_as_dict() or {}

        if section not in existing_data:
            existing_data[section] = {}

        existing_data[section].update(new_data_dict)

        yaml_content = yaml.dump(existing_data, default_flow_style=False)
        self.s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=yaml_content)

    def insert_csv(self, csv_buffer):
        self.s3_client.put_object(Bucket=self.bucket, Key=self.key, Body=csv_buffer.getvalue())

    def upload_file(self, local_file_name, bucket_name, s3_file_name):
        self.s3_client.upload_file(local_file_name, bucket_name, s3_file_name)
