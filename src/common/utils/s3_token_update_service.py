from io import StringIO

import boto3
import yaml


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
