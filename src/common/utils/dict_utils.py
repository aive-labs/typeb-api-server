def is_empty_cond(cond: dict | None):
    if isinstance(cond, dict):
        # 딕셔너리인 경우 모든 값에 대해 재귀적으로 확인
        return all(is_empty_cond(value) for value in cond.values())
    else:
        # 기본 경우: 값이 None이거나 빈 리스트인지 확인
        return cond is None or cond == []
