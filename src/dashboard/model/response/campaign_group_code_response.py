from typing import List

from pydantic import BaseModel

from src.dashboard.model.response.campaign_group_stats_response import (
    CampaignGroupStats,
)
from src.search.model.id_with_item_response import IdWithItem


class CampaignGroupRes(BaseModel):
    group_stats: List[CampaignGroupStats | None]
    campaign_options: List[IdWithItem | None]
    group_code_lv1_options: List[IdWithItem | None]
    group_code_lv2_options: List[IdWithItem | None]
