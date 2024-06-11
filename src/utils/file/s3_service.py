import boto3


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
            ExpiresIn=600,
        )

    def generate_presigned_url_for_get(self, file_path: str):
        try:
            response = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": file_path},
                ExpiresIn=86400,
            )
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None
        return response
