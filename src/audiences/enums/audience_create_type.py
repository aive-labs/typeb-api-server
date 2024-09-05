from src.common.enums.str_enum import StrEnum


class AudienceCreateType(StrEnum):
    Filter = ("filter", "대상 고객 필터링")
    Upload = ("upload", "고객목록 업로드")

    description: str

    def __new__(cls, code, description):
        obj = str.__new__(cls)
        obj._value_ = code
        obj.description = description  # type: ignore
        return obj
