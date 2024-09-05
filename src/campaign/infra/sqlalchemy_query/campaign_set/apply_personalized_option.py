import pandas as pd


def apply_personalized_option(campaign_set_df, is_personalized):
    if is_personalized:
        campaign_set_df = campaign_set_df.rename(columns={"age_group_10": "set_group_val"})
        campaign_set_df["set_group_category"] = "age_group_10"

        campaign_set_df["group_sort_num"] = campaign_set_df.groupby("set_sort_num")[
            "set_group_val"
        ].transform(lambda x: pd.factorize(x)[0] + 1)
    else:
        campaign_set_df["set_group_val"] = None
        campaign_set_df["set_group_category"] = None
        campaign_set_df["group_sort_num"] = 1
    return campaign_set_df
