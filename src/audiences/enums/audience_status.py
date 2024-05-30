from enum import StrEnum


class AudienceStatus(StrEnum):
    inactive = ("inactive", "미활성")
    active = ("active", "활성")
    notdisplay = ("notdisplay", "미표시")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description  # type: ignore
        return obj
