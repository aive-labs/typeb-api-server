from enum import Enum


class CampaignTimelineType(Enum):
    CAMPAIGN_EVENT = "campaign_event"
    STATUS_CHANGE = "status_change"
    APPROVAL = "approval"
    SEND_MSG = "send_msg"
    HALT_MSG = "halt_msg"
    SEND_TO_MSG_SERVER = "send_to_msg_server"
    SEND_SUCCESS = "send_success"
