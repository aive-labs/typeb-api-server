from enum import Enum


class StrEnum(str, Enum):
    @classmethod
    def get_eums(cls):
        return [member.__dict__ for member in cls]

    @classmethod
    def get_name_eums(cls, str_name):
        for member in cls:
            if str_name == member.value:
                return member.__dict__
        raise ValueError("Invalid str_name provided")
