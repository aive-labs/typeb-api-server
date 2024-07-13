from enum import Enum


class CampaignApprovalStatus(Enum):
    APPROVED = "approved"
    REVIEW = "review"
    REJECTED = "rejected"
    CANCELED = "canceled"
