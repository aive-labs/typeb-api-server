import random
import string


def generate_random_string(length=6):
    characters = string.ascii_letters + string.digits  # 대소문자 알파벳과 숫자를 포함
    return "".join(random.choice(characters) for _ in range(length))
