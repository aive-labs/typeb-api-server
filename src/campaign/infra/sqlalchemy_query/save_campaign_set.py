from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.sqlalchemy_query.get_contents_name import (
    get_rep_nm_by_contents_id,
)


def save_campaign_set(db, campaign_df):
    """캠페인 오브젝트 저장 (CampaignSets, CampaignSetGroups)

    campaign_df: 캠페인 세트 데이터프레임
    """

    campaign_set_columns = [column.name for column in CampaignSetsEntity.__table__.columns]
    columns_col_list = campaign_df.columns.tolist()
    set_col_to_insert = [set_col for set_col in campaign_set_columns if set_col in columns_col_list]
    set_col_to_insert.append("set_group_list")

    # CampaignSets 인서트할 컬럼 필터
    campaign_set_df = campaign_df[set_col_to_insert]

    for _, row in campaign_set_df.iterrows():
        # CampaignSets 인서트
        set_list = row[set_col_to_insert].to_dict()
        set_list_insert = {key: value for key, value in set_list.items() if key != "set_group_list"}

        set_req = CampaignSetsEntity(**set_list_insert)

        set_group_req_list = []
        for set_group in row["set_group_list"]:
            # CampaignSetGroups 인서트
            set_group_req = CampaignSetGroupsEntity(**set_group)

            if set_group_req.contents_id:
                rep_nm = get_rep_nm_by_contents_id(set_group_req.contents_id, db)
                set_group_req.rep_nm = rep_nm

            set_group_req_list.append(set_group_req)

        set_req.set_group_list = set_group_req_list
        db.add(set_req)

    db.flush()
    return True
