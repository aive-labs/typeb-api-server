import random
import string


def generate_random_string(length=6):
    characters = string.ascii_letters + string.digits  # 대소문자 알파벳과 숫자를 포함
    return "".join(random.choice(characters) for _ in range(length))


def is_convertible_to_int(value):
    try:
        int(value)  # 주어진 값을 int로 변환 시도
        return True  # 변환이 성공하면 True 반환
    except (ValueError, TypeError):
        return False  # 변환이 실패하면 False 반환
