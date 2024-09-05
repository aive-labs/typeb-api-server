def get_values_from_dict(dict_data, keys):
    """
    딕셔너리로부터 특정 key에 대한 key:value만 포함하는 딕셔너리를 만드는 함수
    """
    return {key: dict_data[key] for key in keys if key in dict_data}
