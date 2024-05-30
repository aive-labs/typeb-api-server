from src.audiences.infra.entity.customer_info_status_entity import (
    CustomerInfoStatusEntity,
)
from src.common.enums.str_enum import StrEnum
from src.common.infra.entity.channel_master_entity import ChannelMasterEntity


class CsvTemplates(StrEnum):
    cus_cd = ("고객번호", CustomerInfoStatusEntity)
    shop_cd = ("매장번호", ChannelMasterEntity)

    def __new__(cls, value, source):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.source = source  # type: ignore
        return obj

    def upper_title(self):
        return self.name.upper()
