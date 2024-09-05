import pandas as pd

from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.sqlalchemy_query.add_set_rep_contents import (
    add_set_rep_contents,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_base_obj import (
    get_campaign_base_obj,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_remind import get_campaign_remind
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets import get_campaign_sets
from src.campaign.infra.sqlalchemy_query.recurring_campaign.convert_to_set_group_message_list import (
    convert_to_set_group_message_list,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_campaign_reviewers import (
    get_campaign_reviewers,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_campaign_set_group_messages import (
    get_campaign_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_set_portion import (
    get_set_portion,
)
from src.campaign.utils.utils import set_summary_sentence
from src.core.exceptions.exceptions import NotFoundException


def get_campaigns_api_logic(db, campaign_id):
    org_campaign = get_campaign_base_obj(db, campaign_id)

    if not org_campaign:
        raise NotFoundException(detail={"message": "캠페인을 찾지 못했습니다."})
    campaign_base_dict = org_campaign.as_dict()

    campaign_type_code = campaign_base_dict["campaign_type_code"]

    if len(remind_query := get_campaign_remind(db, campaign_id=campaign_id)) > 0:
        remind_list = [row._asdict() for row in remind_query]
    else:
        remind_list = None

    campaign_base_dict["remind_list"] = remind_list

    sets = [row._asdict() for row in get_campaign_sets(campaign_id=campaign_id, db=db)]

    set_groups = [row._asdict() for row in get_campaign_set_groups(campaign_id=campaign_id, db=db)]

    # rep_nm_list & contents_names
    if campaign_type_code == CampaignType.EXPERT.value:
        sets = add_set_rep_contents(db, sets, set_groups, campaign_id)
    else:
        sets = [{**data_dict, "rep_nm_list": None, "contents_names": None} for data_dict in sets]

    set_group_messages = get_campaign_set_group_messages(campaign_id=campaign_id, db=db)

    set_group_message_list = convert_to_set_group_message_list(set_group_messages)

    recipient_portion, _, set_cus_count = get_set_portion(campaign_id, db)
    set_df = pd.DataFrame(sets)

    if len(set_df) > 0:
        recipient_descriptions = set_summary_sentence(set_cus_count, set_df)
    else:
        recipient_descriptions = None

    reviewer_list = get_campaign_reviewers(campaign_id, db)

    res = {
        "progress": campaign_base_dict["progress"],
        "base": campaign_base_dict,
        "set_summary": {
            "recipient_portion": recipient_portion,
            "recipient_descriptions": recipient_descriptions,
        },
        "set_list": sets,
        "set_group_list": set_groups,
        "set_group_message_list": set_group_message_list,
        "reviewers": reviewer_list,
    }

    return res
