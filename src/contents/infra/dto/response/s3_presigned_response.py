from pydantic import BaseModel


class S3PresignedResponse(BaseModel):
    original_file_name: str
    s3_presigned_url: str
