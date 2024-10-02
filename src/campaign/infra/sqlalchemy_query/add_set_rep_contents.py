from src.campaign.infra.sqlalchemy_query.get_set_rep_nm_list import get_set_rep_nm_list
from src.common.utils.data_converter import DataConverter
from src.strategy.enums.recommend_model import RecommendModels


def add_set_rep_contents(sets, set_groups, campaign_id, db):
    recsys_model_enum_dict = RecommendModels.get_eums()
    personalized_recsys_model_id = [
        i["_value_"] for i in recsys_model_enum_dict if i["personalized"] is True
    ]

    new_collection_model_value = RecommendModels.NEW_COLLECTION.value
    if new_collection_model_value in personalized_recsys_model_id:
        personalized_recsys_model_id.remove(new_collection_model_value)

    not_personalized_set = []

    for idx, row in enumerate(sets):
        # row is dict
        recsys_model_id = row.get("recsys_model_id")
        recsys_model_id = int(float(recsys_model_id)) if recsys_model_id else None
        set_sort_num = row["set_sort_num"]

        if recsys_model_id in personalized_recsys_model_id:
            sets[idx]["rep_nm_list"] = ["개인화"]
            sets[idx]["contents_names"] = ["개인화"]
        else:
            sets[idx]["rep_nm_list"] = None
            sets[idx]["contents_names"] = None
            not_personalized_set.append(set_sort_num)

    # rep_nm_list
    rep_nm_query = get_set_rep_nm_list(
        campaign_id=campaign_id, set_sort_num_list=not_personalized_set, db=db
    )
    rep_nm_list_of_recipients = DataConverter.convert_query_to_df(rep_nm_query)
    sort_num_dict = (
        rep_nm_list_of_recipients.set_index("set_sort_num")["rep_nm_list"]
        .apply(lambda x: x if x != [None] else [])
        .to_dict()
    )
    for idx, set_dict in enumerate(sets):
        for set_sort_num in sort_num_dict:
            if set_dict["set_sort_num"] == set_sort_num:
                sets[idx]["rep_nm_list"] = sort_num_dict[set_sort_num]
    # contents_names
    result_dict = {}
    for item in set_groups:
        key = item["set_sort_num"]
        value = item["contents_name"]

        if key in result_dict and value is not None:
            result_dict[key].append(value)
        else:
            result_dict[key] = [] if value is None else [value]

    for idx, set_dict in enumerate(sets):
        for set_sort_num in result_dict:
            if set_dict["set_sort_num"] == set_sort_num:
                # 콘텐츠명 중복 제거
                sets[idx]["contents_names"] = list(set(result_dict[set_sort_num]))

    print("sets")
    print(sets)

    return sets
