from enum import Enum


class CampaignTimelineType(Enum):
    CAMPAIGN_EVENT = "campaign_event"
    STATUS_CHANGE = "status_change"
    APPROVAL = "approval"
    SEND_REQUEST = "send_request"
    HALT_MSG = "halt_msg"
    SEND_REQUEST_SUCCESS = "send_request_success"
    SEND_SUCCESS = "send_success"
