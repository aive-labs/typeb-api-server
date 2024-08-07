import json
import re

import numpy as np
import pandas as pd

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.common.utils.data_converter import DataConverter
from src.common.utils.string_utils import replace_multiple


def create_dict_list(group):
    if group["name"].values[0] is not None:

        btn_list = group.apply(
            lambda row: {
                "kakao_link_buttons_seq": row["kakao_link_buttons_seq"],
                "name": row["name"],
                "type": row["type"],
                "url_pc": row["url_pc"],
                "url_mobile": row["url_mobile"],
            },
            axis=1,
        ).tolist()

        btn_list_sorted = sorted(btn_list, key=lambda x: x["kakao_link_buttons_seq"])

        btn_list_final = [
            {key: value for key, value in item.items() if key != "kakao_link_buttons_seq"}
            for item in btn_list_sorted
        ]
        btn_list_final = json.dumps(btn_list_final, ensure_ascii=False)
        return '{"button": ' + btn_list_final + "}"
    else:
        return None


def json_to_list(json_str):
    if json_str is not None:
        return json.loads(json_str)["button"]
    else:
        return []


def convert_to_button_format(db, set_group_msg_seqs, send_rsv_format):
    buttons = (
        db.query(
            SetGroupMessagesEntity.set_group_msg_seq,
            CampaignSetGroupsEntity.campaign_id,
            CampaignSetGroupsEntity.set_sort_num,
            CampaignSetGroupsEntity.group_sort_num,
            KakaoLinkButtonsEntity,
        )
        .join(
            SetGroupMessagesEntity,
            CampaignSetGroupsEntity.set_group_seq == SetGroupMessagesEntity.set_group_seq,
        )
        .join(
            KakaoLinkButtonsEntity,
            SetGroupMessagesEntity.set_group_msg_seq == KakaoLinkButtonsEntity.set_group_msg_seq,
        )
        .filter(KakaoLinkButtonsEntity.set_group_msg_seq.in_(set_group_msg_seqs))
        .distinct()
    )

    button_df = DataConverter.convert_query_to_df(buttons)

    if len(button_df) == 0:
        cols = [
            "campaign_id",
            "set_sort_num",
            "group_sort_num",
            "cus_cd",
            "set_group_msg_seq",
            "kko_button_json",
        ]
        empty_df = pd.DataFrame(columns=cols)
        return empty_df

    button_type_map = {"web_link_button": "WL"}
    button_df["button_type"] = button_df["button_type"].map(
        button_type_map
    )  # pyright: ignore [reportArgumentType]

    button_df = button_df.rename(
        columns={
            "web_link": "url_pc",
            "app_link": "url_mobile",
            "button_type": "type",
            "button_name": "name",
        }
    )

    selected_cols = [
        "campaign_id",
        "set_sort_num",
        "group_sort_num",
        "set_group_msg_seq",
        "kakao_link_buttons_seq",
        "name",
        "type",
        "url_pc",
        "url_mobile",
    ]
    button_df = button_df[selected_cols]

    keys = ["campaign_id", "set_sort_num", "group_sort_num", "set_group_msg_seq"]
    # contents_id, contents_link, contents_name
    send_rsv_btn = send_rsv_format.merge(button_df, on=keys, how="left")
    send_rsv_btn = send_rsv_btn.replace({np.nan: None})

    send_rsv_btn["url_pc_extracted"] = send_rsv_btn["url_pc"].apply(
        lambda x: re.findall(r"\{\{(.*?)\}\}", x) if x is not None else []
    )
    send_rsv_btn["url_mobile_extracted"] = send_rsv_btn["url_mobile"].apply(
        lambda x: re.findall(r"\{\{(.*?)\}\}", x) if x is not None else []
    )
    send_rsv_btn["name_extracted"] = send_rsv_btn["name"].apply(
        lambda x: re.findall(r"\{\{(.*?)\}\}", x) if x is not None else []
    )

    # 고객별로 개인화된 contents_uri ,name 처리
    pers_var_map = {
        "contents_url": "contents_url",
        "contents_name": "contents_name",
        "track_id": "track_id",
    }
    send_rsv_btn["url_pc"] = send_rsv_btn.apply(
        lambda x: replace_multiple(x["url_pc"], x, x["url_pc_extracted"], pers_var_map), axis=1
    )

    send_rsv_btn["url_mobile"] = send_rsv_btn.apply(
        lambda x: replace_multiple(x["url_mobile"], x, x["url_mobile_extracted"], pers_var_map),
        axis=1,
    )

    send_rsv_btn["name"] = send_rsv_btn.apply(
        lambda x: replace_multiple(x["name"], x, x["name_extracted"], pers_var_map), axis=1
    )

    # url_pc, url_link를 무조건 채워넣어줘야함
    cond = [
        (send_rsv_btn["url_pc"] == "") | (send_rsv_btn["url_pc"].isnull()),
        (send_rsv_btn["url_pc"] != "") & (send_rsv_btn["url_pc"].notnull()),
    ]
    choice = [
        send_rsv_btn["url_mobile"],  # url_pc와 동일한 값으로 채워줌
        send_rsv_btn["url_pc"],
    ]
    send_rsv_btn["url_pc"] = np.select(cond, choice)

    print("send_rsv_bt[send_rsv_btn]")
    print(send_rsv_btn.columns)
    print(send_rsv_btn[send_rsv_btn["type"].notnull()])

    if len(send_rsv_btn[send_rsv_btn["type"].notnull()]) == 0:
        cols = [
            "campaign_id",
            "set_sort_num",
            "group_sort_num",
            "cus_cd",
            "set_group_msg_seq",
            "kko_button_json",
        ]
        empty_df = pd.DataFrame(columns=cols)
        return empty_df

    group_keys = ["campaign_id", "set_sort_num", "group_sort_num", "cus_cd", "set_group_msg_seq"]

    button_df = (
        send_rsv_btn.groupby(group_keys).apply(create_dict_list).reset_index(name="kko_button_json")
    )

    print("버튼 포매팅 실패 row 수 :")
    notnullbtn = button_df[button_df["kko_button_json"].notnull()]
    print(len(notnullbtn[notnullbtn["kko_button_json"].str.contains("{{")]))

    return button_df
