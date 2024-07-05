from src.common.enums.str_enum import StrEnum
from enum import Enum

class CampaignProgress(StrEnum):
    base_complete = "base_complete"
    set_complete = "set_complete"
    message_complete = "message_complete"
    decription_complete = "decription_complete"


class CampaignProgressEnum(Enum):
    BASE_COMPLETE = "base_complete"
    SET_COMPLETE = "set_complete"
    MESSAGE_COMPLETE = "message_complete"
    DESCRIPTION_COMPLETE = "decription_complete"
