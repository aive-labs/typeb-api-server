from collections import defaultdict


def convert_to_set_group_message_list(set_group_messages):
    result_dict = defaultdict(list)
    # {set_seq: dict()}
    for item in set_group_messages:
        set_seq = item["set_seq"]
        result_dict[set_seq].append(item)

    result_dict = dict(result_dict)

    for k, _ in result_dict.items():
        # k -> set_seq
        set_group_list = result_dict[k]
        total_list = []
        for g_idx, _ in enumerate(set_group_list):
            # g_idx -> set_group index
            set_group_messages = result_dict[k][g_idx].copy()

            if len(total_list) == 0:
                sub_dict = {}
                sub_dict["set_group_seq"] = set_group_messages["set_group_seq"]
                sub_dict["group_sort_num"] = set_group_messages["group_sort_num"]
                sub_dict["set_seq"] = set_group_messages["set_seq"]
                set_group_messages.pop("set_group_seq")
                sub_dict["campaign_msg"] = (
                    set_group_messages
                    if set_group_messages["msg_send_type"] == "campaign"
                    else None
                )

                if sub_dict["campaign_msg"]:
                    sub_dict["campaign_msg"]["rec_explanation"] = set_group_messages[
                        "rec_explanation"
                    ]

                sub_dict["remind_msg_list"] = (
                    [set_group_messages]
                    if set_group_messages["msg_send_type"] == "remind"
                    else None
                )

                if sub_dict["remind_msg_list"]:
                    for i, _ in enumerate(sub_dict["remind_msg_list"]):
                        sub_dict["remind_msg_list"][i]["remind_seq"] = set_group_messages[
                            "remind_seq"
                        ]

                total_list.append(sub_dict)

            else:
                # total_list에 이미 있는 set_group_seq를 제외한 set_group_seq 리스트
                set_group_seqs = list({elem_dict["set_group_seq"] for elem_dict in total_list})

                if set_group_messages["set_group_seq"] not in set_group_seqs:
                    sub_dict = {}
                    sub_dict["set_group_seq"] = set_group_messages["set_group_seq"]
                    sub_dict["group_sort_num"] = set_group_messages["group_sort_num"]
                    sub_dict["set_seq"] = set_group_messages["set_seq"]
                    set_group_messages.pop("set_group_seq")

                    sub_dict["campaign_msg"] = (
                        set_group_messages
                        if set_group_messages["msg_send_type"] == "campaign"
                        else None
                    )

                    if sub_dict["campaign_msg"]:
                        sub_dict["campaign_msg"]["rec_explanation"] = set_group_messages[
                            "rec_explanation"
                        ]

                    sub_dict["remind_msg_list"] = (
                        [set_group_messages]
                        if set_group_messages["msg_send_type"] == "remind"
                        else None
                    )

                    if sub_dict["remind_msg_list"]:
                        for i, _ in enumerate(sub_dict["remind_msg_list"]):
                            sub_dict["remind_msg_list"][i]["remind_seq"] = set_group_messages[
                                "remind_seq"
                            ]

                    total_list.append(sub_dict)

                else:
                    # total_list에 이미 있는 set_group_seq가 있는 경우 append

                    total_list_index = None
                    for idx, elem_dict in enumerate(total_list):

                        if elem_dict["set_group_seq"] == set_group_messages["set_group_seq"]:
                            total_list_index = idx

                    set_group_messages.pop("set_group_seq")

                    # 리마인드 메세지가 들어온 경우
                    if set_group_messages["msg_send_type"] == "remind":

                        if total_list[total_list_index]["remind_msg_list"]:
                            # 리마인드 메세지가 1개 이상 들어와 있는 경우
                            total_list[total_list_index]["remind_msg_list"].append(
                                set_group_messages
                            )
                        else:
                            # 리마인드 메세지가 새로 들어오는 경우
                            total_list[total_list_index]["remind_msg_list"] = [set_group_messages]

                    # 캠페인 메세지가 들어온 경우
                    elif set_group_messages["msg_send_type"] == "campaign":
                        total_list[total_list_index]["campaign_msg"] = set_group_messages

        # 1개 set_seq에 대한 group_message 할당 완료
        result_dict[k] = total_list

    return result_dict
