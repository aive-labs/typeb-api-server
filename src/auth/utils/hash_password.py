import hashlib

"""패스워드를 해싱하는 클래스입니다.
"""


def generate_hash(input_string: str) -> str:
    """
    주어진 입력 문자열을 SHA-256 해시 값으로 변환합니다.

    :param input_string: 해시할 입력 문자열
    :return: SHA-256 해시 값
    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode("utf-8"))
    return sha256_hash.hexdigest()


def create_hash(self, login_pw):
    pass


def verify_hash(self, password: str, input_hashed_password: str):
    pass
