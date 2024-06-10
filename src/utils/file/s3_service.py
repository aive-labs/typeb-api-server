import logging
import os

import boto3
from botocore.exceptions import ClientError


class S3Service:

    def __init__(self):
        self.AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
        self.AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

        # S3 클라이언트 생성
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=self.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY,
        )

    def generate_presigned_url(self, files: list[str]):
        try:
            return [
                self.s3_client.generate_presigned_url(
                    "put_object",
                    Params={"Bucket": self.AWS_BUCKET_NAME, "Key": file},
                )
                for file in files
            ]
        except ClientError as e:
            logging.error(e)
            return None
