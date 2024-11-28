import aioboto3
import boto3
from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

from src.common.utils.get_env_variable import get_env_variable


class S3Service:

    def __init__(self, bucket_name):
        self.s3_client = boto3.client("s3")
        self.cloudfront = boto3.client("cloudfront")
        self.bucket_name = bucket_name
        self.async_session = aioboto3.Session()

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
            raise e
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

    def get_object(self, key: str):
        return self.s3_client.get_object(Bucket=self.bucket_name, Key=key)

    async def get_object_async(self, file_key):
        async with self.async_session.client("s3") as s3:
            response = await s3.get_object(Bucket=self.bucket_name, Key=file_key)
            return response

    async def put_object_async(self, s3_file_key: str, file_read):
        async with self.async_session.client("s3") as s3:
            await s3.put_object(Bucket=self.bucket_name, Key=s3_file_key, Body=file_read)

    async def delete_object_async(self, s3_file_key: str):
        async with self.async_session.client("s3") as s3:
            await s3.delete_object(Bucket=self.bucket_name, Key=s3_file_key)

    def invalidate_cache(self, invalidation_path: str):
        distribution_id = get_env_variable("cloud_front_distribution_id")
        try:
            # Create invalidation in CloudFront
            response = self.cloudfront.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    "Paths": {"Quantity": 1, "Items": [invalidation_path]},
                    "CallerReference": str(
                        hash(invalidation_path)
                    ),  # Unique reference for this invalidation
                },
            )
            print("Cache Invalidation response:", response)
        except Exception as e:
            print(f"Error invalidating CloudFront cache: {e}")
            raise
