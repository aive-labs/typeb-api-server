import re

import pandas as pd
from sqlalchemy import text

from src.admin.infra.entity.personal_variable_entity import PersonalVariablesEntity
from src.common.utils.string_utils import replace_multiple
from src.message_template.enums.message_type import MessageType


def extract_body(row):
    if row["send_msg_type"] == MessageType.KAKAO_CAROUSEL.value:
        return (
            re.findall(r"\{\{(.*?)\}\}", row["kko_button_json"])
            if row["kko_button_json"] is not None
            else []
        )
    else:
        return (
            re.findall(r"\{\{(.*?)\}\}", row["send_msg_body"])
            if row["send_msg_body"] is not None
            else []
        )


def replace_extract_body(row, pers_var_map):
    # send_msg_body를 직접 처리
    row["send_msg_body"] = replace_multiple(
        row["send_msg_body"], row, row["body_extracted"], pers_var_map
    )

    # send_msg_type이 KAKAO_CAROUSEL일 경우 kko_button_json을 처리
    if row["send_msg_type"] == MessageType.KAKAO_CAROUSEL.value:
        row["kko_button_json"] = replace_multiple(
            row["kko_button_json"], row, row["body_extracted"], pers_var_map
        )

    return row


# def replace_extract_body(row, pers_var_map):
#     row["send_msg_body"] = row.apply(
#         lambda x: replace_multiple(x["send_msg_body"], x, x["body_extracted"], pers_var_map), axis=1
#     )
#     if row["send_msg_type"] == MessageType.KAKAO_CAROUSEL.value:
#         row["kko_button_json"] = row.apply(
#             lambda x: replace_multiple(x["kko_button_json"], x, x["body_extracted"], pers_var_map),
#             axis=1,
#         )
#     return row


def personal_variable_formatting(db, df: pd.DataFrame, test_send_list: list | None = None):
    personal_variable_query = db.query(PersonalVariablesEntity)

    print(df)

    df["body_extracted"] = df.apply(extract_body, axis=1)
    pers_var = list(df["body_extracted"])
    print("pers_var")
    print(pers_var)

    from src.campaign.utils import utils

    flatten_pers_var = utils.flat(pers_var)
    flatten_pers_var = list(set(flatten_pers_var))
    print("사용된 개인화 변수심볼")
    print(flatten_pers_var)

    pers_var_map = {}
    for pers_var in flatten_pers_var:
        # ex. customer_name , 미구매기간

        if pers_var in [
            "rep_nm",
            "contents_url",
            "contents_name",
            "campaign_start_date",
            "campaign_end_date",
            "offer_start_date",
            "offer_end_date",
            "offer_amount",
        ]:
            pers_var_map[pers_var] = pers_var
            continue

        if pers_var in ["고객번호"]:
            pers_var_sb = "{{" + pers_var + "}}"
            personal_variable_obj = personal_variable_query.filter(
                PersonalVariablesEntity.variable_symbol == pers_var_sb
            ).first()
            pers_column = personal_variable_obj.variable_column
            pers_var_map[pers_var] = pers_column
            continue

        pers_var_sb = "{{" + pers_var + "}}"

        personal_variable_obj = personal_variable_query.filter(
            PersonalVariablesEntity.variable_symbol == pers_var_sb
        ).first()
        pers_column = personal_variable_obj.variable_column

        if personal_variable_obj is None:
            raise Exception("개인화 변수목록에 없는 변수가 메세지에 사용되었습니다.")

        pers_var_map[pers_var] = pers_column
        sql_query_txt = personal_variable_obj.variable_option
        sql_query = text(sql_query_txt)
        res = db.execute(sql_query)
        personal_val_df = pd.DataFrame(res.fetchall(), columns=res.keys())
        df = df.merge(personal_val_df, on="cus_cd", how="left")  # column add

    if test_send_list:
        test_replaced_df = pd.DataFrame()
        uniq_group_msg_seq = df["set_group_msg_seq"].unique()
        replace_dict = {
            "고객명": [rcp.user_name_object.split("/")[0] for rcp in test_send_list],
            "cust_name": [rcp.user_name_object.split("/")[0] for rcp in test_send_list],
            "cus_card_no": ["0" * 10 for _ in range(len(test_send_list))],
            # 'cus_cd': ['0'*10 for _ in range(len(test_send_list))],
            "call_back_no": [rcp.test_callback_number for rcp in test_send_list],
        }

        test_preset = ["고객명", "cust_name", "cus_card_no"]
        for msg_seq in uniq_group_msg_seq:
            temp_df = df[df.set_group_msg_seq == msg_seq]
            for col in test_preset:
                if col in temp_df.columns:
                    temp_df[col] = replace_dict[col]
            test_replaced_df = pd.concat([test_replaced_df, temp_df])
        df = test_replaced_df.copy()  # pyright: ignore [reportAssignmentType]
        del test_replaced_df

    # body_extracted 의 개인화 변수를 추가된 컬럼에서 포매팅
    # df["send_msg_body"] = df.apply(
    #     lambda x: replace_multiple(x["send_msg_body"], x, x["body_extracted"], pers_var_map), axis=1
    # )
    # if df["send_msg_type"][0] == "kakao_carousel":
    #     df["kko_button_json"] = df.apply(
    #         lambda x: replace_multiple(x["kko_button_json"], x, x["body_extracted"], pers_var_map),
    #         axis=1,
    #     )

    df = df.apply(replace_extract_body, axis=1, args=(pers_var_map,))

    print("본문 : 포매팅 성공 변수 리스트")
    print(len(df[~df["send_msg_body"].str.contains("{{")]))
    print(
        set([j for i in df[~df["send_msg_body"].str.contains("{{")]["body_extracted"] for j in i])
    )

    print("본문 : 포매팅 실패 변수 리스트")
    print(len(df[df["send_msg_body"].str.contains("{{")]))
    print(set([j for i in df[df["send_msg_body"].str.contains("{{")]["body_extracted"] for j in i]))

    del df["body_extracted"]

    # 발송번호 개인화
    if len(df[df["phone_callback"].str.contains("{{")]) > 0:

        df["phone_callback_extracted"] = df["phone_callback"].apply(
            lambda x: re.findall(r"\{\{(.*?)\}\}", x) if x is not None else []
        )

        pers_var = list(df["phone_callback_extracted"])
        flatten_pers_var = utils.flat(pers_var)
        flatten_pers_var = list(set(flatten_pers_var))

        if flatten_pers_var[0] != "주관리매장전화번호":
            raise Exception("유효하지 않은 매장전화번호 심볼이 사용되었습니다.")

        personal_variable_obj = personal_variable_query.filter(
            PersonalVariablesEntity.variable_symbol == "{{주관리매장전화번호}}"
        ).first()
        pers_column = personal_variable_obj.variable_column

        pers_var_map_2 = {
            flatten_pers_var[0]: pers_column
        }  # {'주관리매장전화번호': 'callback_number'}

        sql_query_txt = personal_variable_obj.variable_option
        sql_query = text(sql_query_txt)
        res = db.execute(sql_query)
        personal_val_df = pd.DataFrame(res.fetchall(), columns=res.keys())

        df = df.merge(personal_val_df, on="cus_cd", how="left")  # column add

        df["phone_callback"] = df.apply(
            lambda x: replace_multiple(
                x["phone_callback"], x, x["phone_callback_extracted"], pers_var_map_2
            ),
            axis=1,
        )

        del df["phone_callback_extracted"]

    return df
