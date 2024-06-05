import math
from datetime import datetime, timedelta

from dependency_injector.wiring import Provide, inject
from fastapi import HTTPException
from sqlalchemy import and_, func, literal

from src.audiences.enums.audience_type import AudienceType
from src.audiences.infra.entity.audience_count_by_month_entity import (
    AudienceCountByMonthEntity,
)
from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMapping,
)
from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.audiences.infra.entity.customer_info_status_entity import (
    CustomerInfoStatusEntity,
)
from src.audiences.infra.entity.primary_rep_product_entity import (
    PrimaryRepProductEntity,
)
from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.core.container import Container
from src.dashboard.infra.entity.dash_end_table_entity import DashEndTable
from src.utils.data_converter import DataConverter


@inject
def execute_target_audience_summary(
    audience_id,
    db=Provide[Container.db],
):

    today = datetime.now()
    yesterday = today - timedelta(days=1)
    three_months_ago = yesterday - timedelta(days=3 * 30)

    today_str = today.strftime("%Y%m%d")
    yesterday_str = yesterday.strftime("%Y%m%d")
    today_month_str = today.strftime("%Y%m")
    three_months_ago_str = three_months_ago.strftime("%Y%m%d")

    cust_ids_query = get_audience_cust_with_audience_id(db, audience_id)
    cust_ids = DataConverter.convert_query_to_df(cust_ids_query)["cus_cd"].tolist()

    purchase_records_query = get_puchase_records_3m(
        db, three_months_ago_str, yesterday_str, cust_ids
    )
    purchase_records_df = DataConverter.convert_query_to_df(purchase_records_query)

    response_data_query = get_response_data_3m(
        db, audience_id, three_months_ago_str, yesterday_str
    )
    response_data_df = DataConverter.convert_query_to_df(response_data_query)
    response_data_df = (
        response_data_df.groupby(["cus_cd"])["response_count"].max().reset_index()
    )

    all_cus_cnt = get_all_cus_cnt(db)
    audience_cnt = len(cust_ids)
    sale_audience_cnt = purchase_records_df["cus_cd"].unique().shape[0]
    audience_sale_amt = purchase_records_df["sale_amt"].sum()
    audience_freq = (
        purchase_records_df[["cus_cd", "sale_dt"]].drop_duplicates().shape[0]
    )
    avg_pur_item_count = (
        purchase_records_df[["cus_cd", "sale_dt", "sty_cd"]]
        .drop_duplicates()
        .groupby(by=["cus_cd", "sale_dt"])
        .count()
        .mean()
        .values[0]
    )
    main_rep_nm_list = (
        purchase_records_df[["rep_nm", "sale_qty", "sale_amt"]]
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
    insert_to_count_by_month["audience_type_code"] = AudienceType.custom.value
    insert_to_count_by_month["audience_count"] = audience_cnt
    insert_to_count_by_month["audience_count_gap"] = 0
    insert_to_count_by_month["net_audience_count"] = 0

    insert_to_count_by_month_list.append(insert_to_count_by_month)

    # audience_stats - 새로 생성 필요
    insert_to_audience_stats = {}
    insert_to_audience_stats["audience_count"] = audience_cnt
    insert_to_audience_stats["audience_count_gap"] = 0.0
    insert_to_audience_stats["net_audience_count"] = 0
    insert_to_audience_stats["audience_type_code"] = AudienceType.custom.value
    insert_to_audience_stats["agg_period_start"] = three_months_ago_str
    insert_to_audience_stats["agg_period_end"] = yesterday_str
    insert_to_audience_stats["excluded_customer_count"] = 0
    insert_to_audience_stats["audience_portion"] = (
        round(audience_cnt / all_cus_cnt, 3) * 100 if all_cus_cnt > 0 else 0
    )
    insert_to_audience_stats["audience_portion_gap"] = 0.0
    insert_to_audience_stats["audience_unit_price"] = (
        int(round(audience_sale_amt / sale_audience_cnt, -3))
        if sale_audience_cnt > 0
        else 0
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

    try:
        # #audience_count_by_month -bulk
        insert_to_count_by_month_list_add = [
            {**data_dict, "audience_id": audience_id}
            for data_dict in insert_to_count_by_month_list
        ]
        insert_query = AudienceCountByMonthEntity.__table__.insert().values(
            insert_to_count_by_month_list_add
        )
        db.execute(insert_query)

        # #audience_stats
        insert_to_audience_stats["audience_id"] = audience_id
        audience_stats_req = AudienceStatsEntity(**insert_to_audience_stats)
        db.add(audience_stats_req)

        # primary_rep_product -bulk
        if main_rep_nm_list:
            insert_to_rep_product_list_add = [
                {**data_dict, "audience_id": audience_id}
                for data_dict in insert_to_rep_product_list
            ]
            insert_query = PrimaryRepProductEntity.__table__.insert().values(
                insert_to_rep_product_list_add
            )
            db.execute(insert_query)

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Failed to compute the representative value for the audience",
        ) from e

    finally:
        db.close()


def get_audience_cust_with_audience_id(db, audience_id):
    with db() as db:
        return db.query(AudienceCustomerMapping.cus_cd).filter(
            AudienceCustomerMapping.audience_id == audience_id
        )


def get_puchase_records_3m(db, three_months_ago, today, cust_list):
    with db() as db:
        return db.query(
            PurchaseAnalyticsMasterStyle.cus_cd,
            PurchaseAnalyticsMasterStyle.recp_no,
            PurchaseAnalyticsMasterStyle.sale_dt,
            PurchaseAnalyticsMasterStyle.sty_cd,
            PurchaseAnalyticsMasterStyle.sty_nm,
            PurchaseAnalyticsMasterStyle.rep_nm,
            PurchaseAnalyticsMasterStyle.sale_qty,
            PurchaseAnalyticsMasterStyle.sale_amt,
        ).filter(
            PurchaseAnalyticsMasterStyle.sale_dt.between(three_months_ago, today),
            PurchaseAnalyticsMasterStyle.cus_cd.in_(cust_list),
        )


def get_response_data_3m(db, audience_id: str, three_months_ago, yst_date):
    with db() as db:
        campaigns_subquery = (
            db.query(CampaignEntity.campaign_id)
            .filter(CampaignEntity.send_date.between(three_months_ago, yst_date))
            .subquery()
        )

        send_count_subquery = (
            db.query(
                SendReservationEntity.campaign_id,
                SendReservationEntity.cus_cd,
                literal(1).label("send_count"),
            )
            .join(
                campaigns_subquery,
                SendReservationEntity.campaign_id == campaigns_subquery.c.campaign_id,
            )
            .filter(
                SendReservationEntity.test_send_yn == "n",
                SendReservationEntity.audience_id == audience_id,
            )
            .group_by(SendReservationEntity.campaign_id, SendReservationEntity.cus_cd)
            .subquery()
        )

        response_count_subquery = (
            db.query(
                DashEndTable.cus_cd,
                DashEndTable.campaign_id,
                literal(1).label("response_count"),
            )
            .group_by(DashEndTable.cus_cd, DashEndTable.campaign_id)
            .having(func.sum(DashEndTable.sale_amt) > 0)
            .subquery()
        )

        return (
            db.query(
                send_count_subquery.c.campaign_id,
                send_count_subquery.c.cus_cd,
                func.count(response_count_subquery.c.response_count).label(
                    "response_count"
                ),
            )
            .outerjoin(
                response_count_subquery,
                and_(
                    send_count_subquery.c.campaign_id
                    == response_count_subquery.c.campaign_id,
                    send_count_subquery.c.cus_cd == response_count_subquery.c.cus_cd,
                ),
            )
            .group_by(send_count_subquery.c.campaign_id, send_count_subquery.c.cus_cd)
        )


def get_all_cus_cnt(db):
    with db() as db:
        return db.query(
            func.distinct(CustomerInfoStatusEntity.cus_cd).label("cus_cd")
        ).count()
