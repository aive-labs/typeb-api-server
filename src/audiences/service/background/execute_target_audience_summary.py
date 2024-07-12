import math
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from sqlalchemy.orm import Session

from src.common.utils.data_converter import DataConverter
from src.core.container import Container


@inject
def execute_target_audience_summary(
    audience_id,
    db: Session,
    target_audience_summary_sqlalchemy=Provide[Container.target_audience_summary_sqlalchemy],
):
    today = datetime.now()
    yesterday = today - timedelta(days=1)
    three_months_ago = yesterday - timedelta(days=3 * 30)

    today_str = today.strftime("%Y%m%d")
    yesterday_str = yesterday.strftime("%Y%m%d")
    today_month_str = today.strftime("%Y%m")
    three_months_ago_str = three_months_ago.strftime("%Y%m%d")

    cust_ids_query = target_audience_summary_sqlalchemy.get_audience_cust_with_audience_id(
        audience_id, db
    )
    cust_ids = DataConverter.convert_query_to_df(cust_ids_query)["cus_cd"].tolist()
    print("cust_ids")
    print(cust_ids)

    purchase_records_query = target_audience_summary_sqlalchemy.get_purchase_records_3m(
        three_months_ago_str, yesterday_str, cust_ids, db
    )
    purchase_records_df = DataConverter.convert_query_to_df(purchase_records_query)
    print("-------------------")
    print("purchase_records_df")
    print(purchase_records_df)
    print("-------------------")

    response_data_query = target_audience_summary_sqlalchemy.get_response_data_3m(
        audience_id, three_months_ago_str, yesterday_str, db
    )
    response_data_df = DataConverter.convert_query_to_df(response_data_query)
    response_data_df = response_data_df.groupby(["cus_cd"])["response_count"].max().reset_index()

    all_cus_cnt = target_audience_summary_sqlalchemy.get_all_customer_count(db)
    audience_cnt = len(cust_ids)
    sale_audience_cnt = purchase_records_df["cus_cd"].unique().shape[0]
    print(sale_audience_cnt)
    print(type(sale_audience_cnt))
    audience_sale_amt = purchase_records_df["sale_amt"].sum()
    print(audience_sale_amt)
    print(type(audience_sale_amt))
    audience_freq = purchase_records_df[["cus_cd", "sale_dt"]].drop_duplicates().shape[0]
    avg_pur_item_count = (
        purchase_records_df[["cus_cd", "sale_dt", "product_code"]]
        .drop_duplicates()
        .groupby(by=["cus_cd", "sale_dt"])
        .count()
        .mean()
        .values[0]  # pyright: ignore [reportAttributeAccessIssue]
    )
    main_rep_nm_list = (
        purchase_records_df[["rep_nm", "sale_qty", "sale_amt"]]  # pyright: ignore [reportCallIssue]
        .groupby(by=["rep_nm"])
        .sum()
        .sort_values(by=["sale_qty", "sale_amt"], ascending=False)
        .index[:3]
        .tolist()
    )

    # audience_count_by_month - 새로 생성 필요
    insert_to_count_by_month_list = []
    insert_to_count_by_month = {}
    insert_to_count_by_month["stnd_month"] = today_month_str
    insert_to_count_by_month["audience_count"] = audience_cnt
    insert_to_count_by_month["audience_count_gap"] = 0
    insert_to_count_by_month["net_audience_count"] = 0

    insert_to_count_by_month_list.append(insert_to_count_by_month)

    # audience_stats - 새로 생성 필요
    insert_to_audience_stats = {}
    insert_to_audience_stats["audience_count"] = audience_cnt
    insert_to_audience_stats["audience_count_gap"] = 0.0
    insert_to_audience_stats["net_audience_count"] = 0
    insert_to_audience_stats["agg_period_start"] = three_months_ago_str
    insert_to_audience_stats["agg_period_end"] = yesterday_str
    insert_to_audience_stats["excluded_customer_count"] = 0
    insert_to_audience_stats["audience_portion"] = (
        round(audience_cnt / all_cus_cnt, 3) * 100 if all_cus_cnt > 0 else 0
    )
    insert_to_audience_stats["audience_portion_gap"] = 0.0
    insert_to_audience_stats["audience_unit_price"] = (
        int(round(audience_sale_amt / sale_audience_cnt, -3)) if sale_audience_cnt > 0 else 0
    )
    insert_to_audience_stats["audience_unit_price_gap"] = 0.0
    insert_to_audience_stats["revenue_per_audience"] = int(round(audience_sale_amt, -3))
    insert_to_audience_stats["purchase_per_audience"] = (
        round(audience_freq / sale_audience_cnt, 1) if sale_audience_cnt > 0 else 0
    )
    insert_to_audience_stats["revenue_per_purchase"] = (
        int(round(audience_sale_amt / audience_freq, 3)) if audience_freq > 0 else 0
    )
    insert_to_audience_stats["avg_pur_item_count"] = (
        round(avg_pur_item_count, 1) if not math.isnan(avg_pur_item_count) else 0
    )
    insert_to_audience_stats["retention_rate_3m"] = (
        round(sale_audience_cnt / audience_cnt, 3) * 100 if audience_cnt > 0 else 0
    )
    insert_to_audience_stats["response_rate"] = (
        round(response_data_df.response_count.sum() / len(response_data_df), 3) * 100
        if len(response_data_df) > 0
        else 0.0
    )
    insert_to_audience_stats["stat_updated_at"] = today_str

    # primary_rep_product - 새로 생성 필요
    insert_to_rep_product_list = []

    insert_to_rep_product_list.extend(
        [
            {"main_product_id": main_rep_nm, "main_product_name": main_rep_nm}
            for main_rep_nm in main_rep_nm_list
        ]
    )

    target_audience_summary_sqlalchemy.insert_audience_stats(
        audience_id,
        insert_to_audience_stats,
        insert_to_count_by_month_list,
        insert_to_rep_product_list,
        main_rep_nm_list,
        db,
    )
