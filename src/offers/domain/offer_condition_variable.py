class OfferConditionVar:
    def __init__(self):
        self.sty_condition_dict = {
            "sty_cd": {
                "code": None,
                "name": "sty_cd",
                "name_kor": "스타일코드",
                "select_type": "text_input",
                "additional_var": None,
            },
            "year_cd": {
                "code": "year_cd",
                "name": "year2",
                "name_kor": "년도",
                "select_type": "multi_select",
                "additional_var": None,
            },
            "season": {
                "code": "season",
                "name": "sty_season_nm",
                "name_kor": "시즌",
                "select_type": "multi_select",
                "additional_var": None,
            },
            "sup_gu": {
                "code": "sup_gu",
                "name": "sup_gu_grp_nm",
                "name_kor": "구분",
                "select_type": "multi_select",
                "additional_var": ["year_cd", "season", "kids_yn", "item_gu"],
            },
            "it_gb": {
                "code": "it_gb",
                "name": "it_gb_nm",
                "name_kor": "복종",
                "select_type": "multi_select",
                "additional_var": ["year_cd", "season", "kids_yn", "item_gu"],
            },
            "item": {
                "code": "item",
                "name": "item_nm",
                "name_kor": "아이템",
                "select_type": "multi_select",
                "additional_var": ["year_cd", "season", "kids_yn", "item_gu"],
            },
            "item_sb": {
                "code": "item_sb",
                "name": "item_sb_nm",
                "name_kor": "아이템세부",
                "select_type": "multi_select",
                "additional_var": ["year_cd", "season", "kids_yn", "item_gu"],
            },
            "item_gu": {
                "code": "item_gu",
                "name": "item_gu_nm",
                "name_kor": "제품구분",
                "select_type": "multi_select",
                "additional_var": None,
            },
            "kids_yn": {
                "code": "kids_yn",
                "name": "kids_yn",
                "name_kor": "키즈 여부",
                "select_type": "multi_select",
                "additional_var": None,
            },
        }
        self.chn_condition_dict = {
            "shop_cd": {
                "code": "shop_cd",
                "name": "shop_cd",
                "name_kor": "매장코드",
                "select_type": "text_input",
                "additional_var": None,
            },
            "shop_tp": {
                "code": "shop_tp",
                "name": "shop_tp_nm",
                "name_kor": "매장형태",
                "select_type": "multi_select",
                "additional_var": ["shop_tp4", "shop_tp5", "area"],
            },
            "shop_tp4": {
                "code": "shop_tp4",
                "name": "shop_tp4_nm",
                "name_kor": "유통상세B",
                "select_type": "multi_select",
                "additional_var": ["shop_tp", "shop_tp5", "area"],
            },
            "shop_tp5": {
                "code": "shop_tp5",
                "name": "shop_tp5_nm",
                "name_kor": "유통상세C",
                "select_type": "multi_select",
                "additional_var": ["shop_tp", "shop_tp4", "area"],
            },
            "area_cd": {
                "code": "area_cd",
                "name": "area_nm",
                "name_kor": "지역구분",
                "select_type": "multi_select",
                "additional_var": ["shop_tp", "shop_tp4", "shop_tp5"],
            },
            "shop_mng_gb": {
                "code": "shop_mng_gb",
                "name": "shop_mng_gb_nm",
                "name_kor": "매장운영형태",
                "select_type": "multi_select",
                "additional_var": ["shop_tp", "shop_tp4", "shop_tp5"],
            },
        }

    def cond_option(self, cond_frame, tbl_data, option_model):
        condition_list = []
        for _, v in cond_frame.items():
            code = "code" if v.get("code") else "name"
            if v.get("select_type") == "multi_select":
                elem = {
                    (getattr(data, v.get(code)), getattr(data, v.get("name")))
                    for data in tbl_data
                }
                options = [
                    option_model.model_validate(
                        {
                            "id": (
                                item[0] if item[0] is not None else item[1]
                            ),  ## 컬럼에 코드값이 없는 경우 name으로 가져옴
                            "name": item[1],
                        }
                    )
                    for item in elem
                    if item[1] is not None
                ]
                condition_list.append(
                    {
                        "name": v.get("name_kor"),
                        "code": v.get(code),
                        "select_type": "multi_select",
                        "additional_var": v.get("additional_var"),
                        "options": options,
                    }
                )
            elif v.get("select_type") == "text_input":
                condition_list.append(
                    {
                        "name": v.get("name_kor"),
                        "code": v.get(code),
                        "select_type": "text_input",
                        "additional_var": v.get("additional_var"),
                        "options": [],
                    }
                )
        return condition_list
