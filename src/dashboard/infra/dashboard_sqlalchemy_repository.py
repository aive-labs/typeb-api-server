from typing import List

import pandas as pd
from sqlalchemy import (
    Float,
    Integer,
    String,
    and_,
    case,
    func,
    literal,
    not_,
    or_,
)
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.common.utils.data_converter import DataConverter
from src.dashboard.infra.entity.dash_daily_send_info_entity import (
    DashDailySendInfoEntity,
)
from src.dashboard.infra.entity.dash_end_table_entity import DashEndTableEntity
from src.search.routes.dto.id_with_item_response import IdWithItem


class DashboardSqlAlchemy:

    def get_dashboard_campaign_ids(self, db: Session, start_date: str, end_date: str) -> List[str]:
        entity = (
            db.query(CampaignEntity.campaign_id)
            .filter(
                not_(
                    or_(CampaignEntity.start_date > end_date, CampaignEntity.end_date < start_date)
                ),
            )
            .all()
        )

        return [item.campaign_id for item in entity]

    def get_campaign_stats(
        self, db: Session, start_date, end_date, campaign_ids: List[str]
    ) -> pd.DataFrame:
        response_cus_cd = (
            db.query(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
            )
            .group_by(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .having(func.sum(DashEndTableEntity.sale_amt) > 0)
            .subquery()
        )

        coupon_usage_cus_cd = (
            db.query(
                DashEndTableEntity.cus_cd.label("coupon_usage_cus_cd"),
                DashEndTableEntity.campaign_id,
                literal(1).label("coupon_usage_use_yn"),
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
                DashEndTableEntity.coupon_usage == 1,
            )
            .group_by(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .subquery()
        )

        campaign_stats_data = (
            db.query(
                DashEndTableEntity.campaign_id,
                DashEndTableEntity.strategy_theme_id,
                DashEndTableEntity.audience_id,
                DashEndTableEntity.coupon_no,
                DashEndTableEntity.media,
                func.count(func.distinct(response_cus_cd.c.cus_cd)).label("t_response_cust_count"),
                func.sum(
                    case(
                        (response_cus_cd.c.cus_cd.is_not(None), DashEndTableEntity.sale_qty),
                        else_=0,
                    )
                ).label("t_response_quantity"),
                func.sum(
                    case(
                        (response_cus_cd.c.cus_cd.is_not(None), DashEndTableEntity.sale_amt),
                        else_=0,
                    )
                ).label("t_response_revenue"),
                case(
                    (func.count(func.distinct(response_cus_cd.c.cus_cd)) == 0, 0),
                    else_=func.cast(
                        (
                            func.sum(
                                case(
                                    (
                                        response_cus_cd.c.cus_cd.is_not(None),
                                        DashEndTableEntity.sale_amt,
                                    ),
                                    else_=0,
                                )
                            )
                            / func.count(func.distinct(response_cus_cd.c.cus_cd))
                        ),
                        Integer,
                    ),
                ).label("t_response_unit_price"),
                func.count(
                    func.distinct(
                        case(
                            (
                                coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                DashEndTableEntity.cus_cd,
                            ),
                            else_=None,
                        )
                    )
                ).label("e_response_cust_count"),
                func.sum(
                    case(
                        (
                            coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                            DashEndTableEntity.sale_qty,
                        ),
                        else_=literal(0),
                    )
                ).label("e_response_quantity"),
                func.sum(
                    case(
                        (
                            coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                            DashEndTableEntity.sale_amt,
                        ),
                        else_=literal(0),
                    )
                ).label("e_response_revenue"),
                case(
                    (
                        func.count(
                            func.distinct(
                                case(
                                    (
                                        coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                        DashEndTableEntity.cus_cd,
                                    )
                                )
                            )
                        )
                        == 0,
                        0,
                    ),
                    else_=func.cast(
                        (
                            func.sum(
                                case(
                                    (
                                        coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                        DashEndTableEntity.sale_amt,
                                    ),
                                    else_=literal(0),
                                )
                            )
                            / func.count(
                                func.distinct(
                                    case(
                                        (
                                            coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                            DashEndTableEntity.cus_cd,
                                        )
                                    )
                                )
                            )
                        ),
                        Integer,
                    ),
                ).label("e_response_unit_price"),
            )
            .outerjoin(
                response_cus_cd,
                and_(
                    DashEndTableEntity.cus_cd == response_cus_cd.c.cus_cd,
                    DashEndTableEntity.campaign_id == response_cus_cd.c.campaign_id,
                ),
            )
            .outerjoin(
                coupon_usage_cus_cd,
                and_(
                    DashEndTableEntity.cus_cd == coupon_usage_cus_cd.c.coupon_usage_cus_cd,
                    DashEndTableEntity.campaign_id == coupon_usage_cus_cd.c.campaign_id,
                    DashEndTableEntity.coupon_usage == coupon_usage_cus_cd.c.coupon_usage_use_yn,
                ),
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
                DashEndTableEntity.campaign_id.in_(campaign_ids),
            )
            .group_by(
                DashEndTableEntity.campaign_id,
                DashEndTableEntity.strategy_theme_id,
                DashEndTableEntity.audience_id,
                DashEndTableEntity.coupon_no,
                DashEndTableEntity.media,
            )
            .subquery()
        )

        dash_daily_send_info = (
            db.query(
                DashDailySendInfoEntity.campaign_id,
                func.max(DashDailySendInfoEntity.campaign_name).label("campaign_name"),
                func.max(DashDailySendInfoEntity.start_date).label("start_date"),
                func.max(DashDailySendInfoEntity.end_date).label("end_date"),
                func.max(DashDailySendInfoEntity.campaign_status_name).label(
                    "campaign_status_name"
                ),
                DashDailySendInfoEntity.strategy_theme_id,
                func.max(DashDailySendInfoEntity.strategy_theme_name).label("strategy_theme_name"),
                DashDailySendInfoEntity.audience_id,
                func.max(DashDailySendInfoEntity.audience_name).label("audience_name"),
                DashDailySendInfoEntity.coupon_no,
                func.max(DashDailySendInfoEntity.coupon_name).label("coupon_name"),
                DashDailySendInfoEntity.media,
                func.sum(DashDailySendInfoEntity.tot_recipient_count).label("tot_recipient_count"),
                func.sum(DashDailySendInfoEntity.tot_success_count).label("tot_success_count"),
                func.cast(func.sum(DashDailySendInfoEntity.tot_send_cost), Integer).label(
                    "tot_send_cost"
                ),
            )
            .filter(
                DashDailySendInfoEntity.campaign_id.in_(campaign_ids),
            )
            .group_by(
                DashDailySendInfoEntity.campaign_id,
                DashDailySendInfoEntity.strategy_theme_id,
                DashDailySendInfoEntity.audience_id,
                DashDailySendInfoEntity.coupon_no,
                DashDailySendInfoEntity.media,
            )
            .subquery()
        )

        results = (
            db.query(
                dash_daily_send_info.c.campaign_id,
                dash_daily_send_info.c.campaign_name,
                dash_daily_send_info.c.start_date,
                dash_daily_send_info.c.end_date,
                dash_daily_send_info.c.campaign_status_name,
                dash_daily_send_info.c.strategy_theme_id,
                dash_daily_send_info.c.strategy_theme_name,
                dash_daily_send_info.c.audience_id,
                dash_daily_send_info.c.audience_name,
                dash_daily_send_info.c.coupon_no,
                dash_daily_send_info.c.coupon_name,
                dash_daily_send_info.c.media,
                dash_daily_send_info.c.tot_recipient_count.label("recipient_count"),
                dash_daily_send_info.c.tot_success_count.label("sent_cust_count"),
                dash_daily_send_info.c.tot_send_cost.label("media_cost"),
                campaign_stats_data.c.t_response_cust_count.label("response_cust_count"),
                (
                    case(
                        (campaign_stats_data.c.t_response_cust_count == 0, 0),
                        else_=(
                            campaign_stats_data.c.t_response_cust_count
                            / dash_daily_send_info.c.tot_recipient_count
                        ),
                    )
                ).label("response_rate"),
                campaign_stats_data.c.t_response_quantity.label("response_quantity"),
                campaign_stats_data.c.t_response_revenue.label("response_revenue"),
                campaign_stats_data.c.t_response_unit_price.label("response_unit_price"),
                (
                    (
                        campaign_stats_data.c.t_response_revenue
                        / dash_daily_send_info.c.tot_send_cost
                    )
                    * 100
                ).label("response_roi"),
                campaign_stats_data.c.e_response_cust_count,
                (
                    case(
                        (campaign_stats_data.c.e_response_cust_count == 0, 0),
                        else_=(
                            campaign_stats_data.c.e_response_cust_count
                            / dash_daily_send_info.c.tot_recipient_count
                        ),
                    )
                ).label("e_response_rate"),
                campaign_stats_data.c.e_response_quantity,
                campaign_stats_data.c.e_response_revenue,
                campaign_stats_data.c.e_response_unit_price,
            )
            .outerjoin(
                campaign_stats_data,
                and_(
                    campaign_stats_data.c.campaign_id == dash_daily_send_info.c.campaign_id,
                    campaign_stats_data.c.strategy_theme_id
                    == dash_daily_send_info.c.strategy_theme_id,
                    campaign_stats_data.c.audience_id == dash_daily_send_info.c.audience_id,
                    campaign_stats_data.c.coupon_no == dash_daily_send_info.c.coupon_no,
                    campaign_stats_data.c.media == dash_daily_send_info.c.media,
                ),
            )
            .order_by(
                dash_daily_send_info.c.campaign_id.desc(),
                dash_daily_send_info.c.strategy_theme_id,
                dash_daily_send_info.c.audience_id,
            )
        )

        return DataConverter.convert_query_to_df(results)

    def get_campaign_group_stats(
        self,
        db: Session,
        start_date,
        end_date,
        campaign_ids: List[str],
        group_code_lv1=None,
        group_code_lv2=None,
    ) -> pd.DataFrame:
        response_cus_cd = (
            db.query(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
            )
            .group_by(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .having(func.sum(DashEndTableEntity.sale_amt) > 0)
            .subquery()
        )

        coupon_usage_cus_cd = (
            db.query(
                DashEndTableEntity.cus_cd.label("coupon_usage_cus_cd"),
                DashEndTableEntity.campaign_id,
                literal(1).label("coupon_usage_use_yn"),
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
                DashEndTableEntity.coupon_usage == 1,
            )
            .group_by(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .subquery()
        )

        campaign_group_stats = (
            db.query(
                DashEndTableEntity.campaign_id,
                func.max(DashEndTableEntity.campaign_name).label("campaign_name"),
                (
                    getattr(DashEndTableEntity, group_code_lv1)
                    if group_code_lv1 != None
                    else literal("필터없음").label("filter_column1")
                ),
                (
                    getattr(DashEndTableEntity, group_code_lv2)
                    if group_code_lv2 != None
                    else literal("필터없음").label("filter_column2")
                ),
                func.count(func.distinct(response_cus_cd.c.cus_cd)).label("t_response_cust_count"),
                func.sum(
                    case(
                        (response_cus_cd.c.cus_cd.is_not(None), DashEndTableEntity.sale_qty),
                        else_=0,
                    )
                ).label("t_response_quantity"),
                func.sum(
                    case(
                        (response_cus_cd.c.cus_cd.is_not(None), DashEndTableEntity.sale_amt),
                        else_=0,
                    )
                ).label("t_response_revenue"),
                case(
                    (func.count(func.distinct(response_cus_cd.c.cus_cd)) == 0, 0),
                    else_=func.cast(
                        (
                            func.sum(
                                case(
                                    (
                                        response_cus_cd.c.cus_cd.is_not(None),
                                        DashEndTableEntity.sale_amt,
                                    ),
                                    else_=0,
                                )
                            )
                            / func.count(func.distinct(response_cus_cd.c.cus_cd))
                        ),
                        Integer,
                    ),
                ).label("t_response_unit_price"),
                func.count(
                    func.distinct(
                        case(
                            (
                                coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                DashEndTableEntity.cus_cd,
                            ),
                            else_=None,
                        )
                    )
                ).label("e_response_cust_count"),
                func.sum(
                    case(
                        (
                            coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                            DashEndTableEntity.sale_qty,
                        ),
                        else_=0,
                    )
                ).label("e_response_quantity"),
                func.sum(
                    case(
                        (
                            coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                            DashEndTableEntity.sale_amt,
                        ),
                        else_=0,
                    )
                ).label("e_response_revenue"),
                case(
                    (
                        func.count(
                            func.distinct(
                                case(
                                    (
                                        coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                        DashEndTableEntity.cus_cd,
                                    )
                                )
                            )
                        )
                        == 0,
                        0,
                    ),
                    else_=func.cast(
                        (
                            func.sum(
                                case(
                                    (
                                        coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                        DashEndTableEntity.sale_amt,
                                    ),
                                    else_=literal(0),
                                )
                            )
                            / func.count(
                                func.distinct(
                                    case(
                                        (
                                            coupon_usage_cus_cd.c.coupon_usage_use_yn == 1,
                                            DashEndTableEntity.cus_cd,
                                        )
                                    )
                                )
                            )
                        ),
                        Integer,
                    ),
                ).label("e_response_unit_price"),
            )
            .outerjoin(
                response_cus_cd,
                and_(
                    DashEndTableEntity.cus_cd == response_cus_cd.c.cus_cd,
                    DashEndTableEntity.campaign_id == response_cus_cd.c.campaign_id,
                ),
            )
            .outerjoin(
                coupon_usage_cus_cd,
                and_(
                    DashEndTableEntity.cus_cd == coupon_usage_cus_cd.c.coupon_usage_cus_cd,
                    DashEndTableEntity.campaign_id == coupon_usage_cus_cd.c.campaign_id,
                    DashEndTableEntity.coupon_usage == coupon_usage_cus_cd.c.coupon_usage_use_yn,
                ),
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
                DashEndTableEntity.campaign_id.in_(campaign_ids),
            )
            .group_by(
                DashEndTableEntity.campaign_id,
            )
        )

        if group_code_lv1 != None:
            campaign_group_stats = campaign_group_stats.group_by(
                getattr(DashEndTableEntity, group_code_lv1)
            )

        if group_code_lv2 != None:
            campaign_group_stats = campaign_group_stats.group_by(
                getattr(DashEndTableEntity, group_code_lv2)
            )

        dash_daily_send_info = (
            db.query(
                DashDailySendInfoEntity.campaign_id,
                func.max(DashDailySendInfoEntity.campaign_name).label("campaign_name"),
                func.max(DashDailySendInfoEntity.start_date).label("start_date"),
                func.max(DashDailySendInfoEntity.end_date).label("end_date"),
                func.max(DashDailySendInfoEntity.campaign_status_name).label(
                    "campaign_status_name"
                ),
                (
                    getattr(DashDailySendInfoEntity, group_code_lv1)
                    if group_code_lv1 != None
                    else literal("필터없음").label("filter_column1")
                ),
                (
                    getattr(DashDailySendInfoEntity, group_code_lv2)
                    if group_code_lv2 != None
                    else literal("필터없음").label("filter_column2")
                ),
                func.sum(DashDailySendInfoEntity.tot_recipient_count).label("tot_recipient_count"),
                func.sum(DashDailySendInfoEntity.tot_success_count).label("tot_success_count"),
                func.cast(func.sum(DashDailySendInfoEntity.tot_send_cost), Integer).label(
                    "tot_send_cost"
                ),
            )
            .filter(
                DashDailySendInfoEntity.campaign_id.in_(campaign_ids),
            )
            .group_by(
                DashDailySendInfoEntity.campaign_id,
            )
        )

        if group_code_lv1 != None:
            dash_daily_send_info = dash_daily_send_info.group_by(
                getattr(DashDailySendInfoEntity, group_code_lv1)
            )
        if group_code_lv2 != None:
            dash_daily_send_info = dash_daily_send_info.group_by(
                getattr(DashDailySendInfoEntity, group_code_lv2)
            )

        campaign_group_stats = campaign_group_stats.subquery()
        dash_daily_send_info = dash_daily_send_info.subquery()

        results = db.query(
            dash_daily_send_info.c.campaign_id,
            dash_daily_send_info.c.campaign_name,
            (
                getattr(dash_daily_send_info.c, group_code_lv1)
                if group_code_lv1 != None
                else literal("필터없음")
            ).label("group_code_lv1"),
            func.cast(
                (
                    getattr(dash_daily_send_info.c, group_code_lv1)
                    if group_code_lv1 != None
                    else literal("필터없음")
                ),
                String,
            ).label("group_name_lv1"),
            (
                getattr(dash_daily_send_info.c, group_code_lv2)
                if group_code_lv2 != None
                else literal("필터없음")
            ).label("group_code_lv2"),
            func.cast(
                (
                    getattr(dash_daily_send_info.c, group_code_lv2)
                    if group_code_lv2 != None
                    else literal("필터없음")
                ),
                String,
            ).label("group_name_lv2"),
            func.cast(dash_daily_send_info.c.tot_recipient_count, Integer).label("recipient_count"),
            func.cast(dash_daily_send_info.c.tot_success_count, Integer).label("sent_cust_count"),
            func.cast(campaign_group_stats.c.t_response_cust_count, Integer).label(
                "response_cust_count"
            ),
            func.cast(
                case(
                    (campaign_group_stats.c.t_response_cust_count == 0, 0),
                    else_=(
                        campaign_group_stats.c.t_response_cust_count
                        / dash_daily_send_info.c.tot_recipient_count
                    ),
                ),
                Float,
            ).label("response_rate"),
            (campaign_group_stats.c.t_response_quantity).label("response_quantity"),
            (campaign_group_stats.c.t_response_revenue).label("response_revenue"),
            (campaign_group_stats.c.t_response_unit_price).label("response_unit_price"),
            func.cast(
                (campaign_group_stats.c.t_response_revenue / dash_daily_send_info.c.tot_send_cost),
                Float,
            ).label("response_roi"),
            (campaign_group_stats.c.e_response_cust_count).label("e_response_cust_count"),
            func.cast(
                case(
                    (campaign_group_stats.c.e_response_cust_count == 0, 0),
                    else_=(
                        campaign_group_stats.c.e_response_cust_count
                        / dash_daily_send_info.c.tot_recipient_count
                    ),
                ),
                Float,
            ).label("e_response_rate"),
            (campaign_group_stats.c.e_response_quantity).label("e_response_quantity"),
            (campaign_group_stats.c.e_response_revenue).label("e_response_revenue"),
            (campaign_group_stats.c.e_response_unit_price).label("e_response_unit_price"),
        )

        if group_code_lv1 == None:
            results = results.outerjoin(
                campaign_group_stats,
                campaign_group_stats.c.campaign_id == dash_daily_send_info.c.campaign_id,
            )

        elif group_code_lv1 != None and group_code_lv2 == None:
            results = results.outerjoin(
                campaign_group_stats,
                and_(
                    campaign_group_stats.c.campaign_id == dash_daily_send_info.c.campaign_id,
                    getattr(campaign_group_stats.c, group_code_lv1)
                    == getattr(dash_daily_send_info.c, group_code_lv1),
                ),
            )

        elif group_code_lv1 != None and group_code_lv2 != None:
            results = results.outerjoin(
                campaign_group_stats,
                and_(
                    campaign_group_stats.c.campaign_id == dash_daily_send_info.c.campaign_id,
                    getattr(campaign_group_stats.c, group_code_lv1)
                    == getattr(dash_daily_send_info.c, group_code_lv1),
                    getattr(campaign_group_stats.c, group_code_lv2)
                    == getattr(dash_daily_send_info.c, group_code_lv2),
                ),
            )

        return DataConverter.convert_query_to_df(results)

    def get_audience_options(
        self, db: Session, start_date, end_date, campaign_ids
    ) -> List[IdWithItem]:
        audience_data = (
            db.query(
                DashEndTableEntity.audience_id,
                func.max(DashEndTableEntity.audience_name).label("audience_name"),
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
                DashEndTableEntity.campaign_id.in_(campaign_ids),
            )
            .group_by(
                DashEndTableEntity.audience_id,
            )
            .all()
        )
        return [IdWithItem(id=data.audience_id, name=data.audience_name) for data in audience_data]

    def get_audience_stats(self, db: Session, start_date, end_date) -> pd.DataFrame:
        response_cus_cd = (
            db.query(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
            )
            .group_by(
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
            )
            .having(func.sum(DashEndTableEntity.sale_amt) > 0)
            .subquery()
        )

        dash_daily_send_info = (
            db.query(
                DashDailySendInfoEntity.campaign_id,
                func.max(DashDailySendInfoEntity.campaign_name).label("campaign_name"),
                func.max(DashDailySendInfoEntity.start_date).label("start_date"),
                func.max(DashDailySendInfoEntity.end_date).label("end_date"),
                DashDailySendInfoEntity.strategy_theme_id,
                func.max(DashDailySendInfoEntity.strategy_theme_name).label("strategy_theme_name"),
                DashDailySendInfoEntity.audience_id,
                func.max(DashDailySendInfoEntity.audience_name).label("audience_name"),
                func.sum(DashDailySendInfoEntity.tot_recipient_count).label("tot_recipient_count"),
                func.sum(DashDailySendInfoEntity.tot_success_count).label("tot_success_count"),
                func.cast(func.sum(DashDailySendInfoEntity.tot_send_cost), Integer).label(
                    "tot_send_cost"
                ),
            )
            .group_by(
                DashDailySendInfoEntity.campaign_id,
                DashDailySendInfoEntity.strategy_theme_id,
                DashDailySendInfoEntity.audience_id,
            )
            .subquery()
        )

        audience_stats = (
            db.query(
                DashEndTableEntity.campaign_id,
                DashEndTableEntity.strategy_theme_id,
                DashEndTableEntity.audience_id,
                func.count(func.distinct(DashEndTableEntity.cus_cd)).label("t_response_cust_count"),
                func.sum(DashEndTableEntity.sale_amt).label("t_response_revenue"),
            )
            .join(
                response_cus_cd,
                and_(
                    DashEndTableEntity.cus_cd == response_cus_cd.c.cus_cd,
                    DashEndTableEntity.campaign_id == response_cus_cd.c.campaign_id,
                ),
            )
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
            )
            .group_by(
                DashEndTableEntity.campaign_id,
                DashEndTableEntity.audience_id,
                DashEndTableEntity.strategy_theme_id,
            )
            .subquery()
        )

        results = db.query(
            dash_daily_send_info.c.campaign_id,
            dash_daily_send_info.c.campaign_name,
            dash_daily_send_info.c.start_date,
            dash_daily_send_info.c.end_date,
            dash_daily_send_info.c.strategy_theme_id,
            dash_daily_send_info.c.strategy_theme_name,
            dash_daily_send_info.c.audience_id,
            dash_daily_send_info.c.audience_name,
            dash_daily_send_info.c.tot_recipient_count.label("recipient_count"),
            audience_stats.c.t_response_cust_count.label("response_cust_count"),
            (
                audience_stats.c.t_response_cust_count / dash_daily_send_info.c.tot_recipient_count
            ).label("response_rate"),
            audience_stats.c.t_response_revenue.label("response_revenue"),
            (audience_stats.c.t_response_revenue / dash_daily_send_info.c.tot_send_cost).label(
                "response_roi"
            ),
        ).outerjoin(
            audience_stats,
            and_(
                audience_stats.c.campaign_id == dash_daily_send_info.c.campaign_id,
                audience_stats.c.strategy_theme_id == dash_daily_send_info.c.strategy_theme_id,
                audience_stats.c.audience_id == dash_daily_send_info.c.audience_id,
            ),
        )

        return DataConverter.convert_query_to_df(results)

    def get_audience_prch_item(
        self, db: Session, audience_id, start_date, end_date
    ) -> pd.DataFrame:
        reponse_cus_cd = (
            db.query(DashEndTableEntity.cus_cd)
            .filter(
                DashEndTableEntity.sale_dt >= start_date, DashEndTableEntity.sale_dt <= end_date
            )
            .group_by(DashEndTableEntity.cus_cd)
            .having(func.sum(DashEndTableEntity.sale_amt) > 0)
            .subquery()
        )

        audience_item_purchase = (
            db.query(
                DashEndTableEntity.category_name,
                DashEndTableEntity.rep_nm,
                DashEndTableEntity.product_name,
                func.count(func.distinct(DashEndTableEntity.cus_cd)).label("response_cust_count"),
                func.sum(DashEndTableEntity.sale_amt).label("tot_sale_amt"),
            )
            .join(reponse_cus_cd, DashEndTableEntity.cus_cd == reponse_cus_cd.c.cus_cd)
            .filter(
                DashEndTableEntity.sale_dt >= start_date,
                DashEndTableEntity.sale_dt <= end_date,
                DashEndTableEntity.audience_id == audience_id,
            )
            .group_by(
                DashEndTableEntity.category_name,
                DashEndTableEntity.rep_nm,
                DashEndTableEntity.product_name,
            )
        )

        return DataConverter.convert_query_to_df(audience_item_purchase)
