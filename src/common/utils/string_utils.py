import random
import string

import pandas as pd


def generate_random_string(length=6):
    characters = string.ascii_letters + string.digits  # 대소문자 알파벳과 숫자를 포함
    return "".join(random.choice(characters) for _ in range(length))


def is_convertible_to_int(value):
    try:
        int(value)  # 주어진 값을 int로 변환 시도
        return True  # 변환이 성공하면 True 반환
    except (ValueError, TypeError):
        return False  # 변환이 실패하면 False 반환


def replace_multiple(text, row, columns, pers_var_map):
    """
    text: 치환 대상이 되는 문자열
    row: 현재 처리 중인 DataFrame의 행
    columns: 치환해야 할 컬럼명이 담긴 리스트 {{col}} -> col
    """

    for col in columns:

        var_col = pers_var_map.get(col)  # value or None

        if var_col is None:  # (방어코드)개인화 변수목록에 없는 변수
            continue

        if var_col in list(row.index):  # 현재 행에 치환 대상 컬럼이 있는지 확인
            print(row[var_col])

            if (
                pd.isna(row[var_col]) or row[var_col] == "None"
            ):  # (방어코드)치환되는 값이 None 또는 NaN인 경우 치환하지 않음
                continue

            replace_text = "{{" + str(col) + "}}"
            # print(f'replace_text: {replace_text}')
            text = text.replace(replace_text, str(row[var_col]))  # 컬럼 값으로 치환
            print(f"replaced text: {text}")
    print("----")

    return text
