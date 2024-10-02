import boto3


class AwsService:
    # boto3 클라이언트 생성

    @staticmethod
    def get_key_from_parameter_store(parameter_name, with_decryption=True):
        ssm = boto3.client("ssm", region_name="ap-northeast-2")
        try:
            response = ssm.get_parameter(Name=parameter_name, WithDecryption=with_decryption)
            return response["Parameter"]["Value"]
        except Exception as e:
            print(f"Error getting parameter {parameter_name}: {e}")
            return None
