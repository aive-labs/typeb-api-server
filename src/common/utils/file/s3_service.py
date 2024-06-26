import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError


class S3Service:

    def __init__(self, bucket_name):
        self.s3_client = boto3.client("s3")
        self.bucket_name = bucket_name

    def generate_presigned_url_for_put(self, file_path: str) -> str:
        # ClientError처리
        return self.s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": file_path,
            },
            ExpiresIn=300,
        )

    # TODO: Cloudfront을 적용해서 변경해야함
    def generate_presigned_url_for_get(self, file_path: str):
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=604800,
            )
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
        return response

    def delete_object(self, key: str):
        try:
            # 파일 삭제
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=key)
        except NoCredentialsError as e:
            print("s3 delete - Credentials not available")
            raise e
        except ClientError as e:
            print(f"Error: {e}")
            raise e

    def put_object(self, key: str, body: str):
        try:
            self.s3_client.put_object(
                Bucket=self.bucket_name, Key=key, Body=body, ContentType="text/html"
            )
        except (BotoCoreError, ClientError) as e:
            raise e