from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_, func, literal
from sqlalchemy.orm import Session

from src.audiences.infra.entity.audience_count_by_month_entity import (
    AudienceCountByMonthEntity,
)
from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMapping,
)
from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.audiences.infra.entity.primary_rep_product_entity import (
    PrimaryRepProductEntity,
)
from src.audiences.infra.entity.purchase_analytics_master_style_entity import (
    PurchaseAnalyticsMasterStyle,
)
from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.dashboard.infra.entity.dash_end_table_entity import DashEndTable


class TargetAudienceSummarySqlAlchemy:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def get_audience_cust_with_audience_id(self, audience_id):
        with self.db() as db:
            return db.query(AudienceCustomerMapping.cus_cd).filter(
                AudienceCustomerMapping.audience_id == audience_id
            )

    def get_all_customer_count(self):
        with self.db() as db:
            return db.query(
                func.distinct(CustomerInfoStatusEntity.cus_cd).label("cus_cd")
            ).count()

    def get_purchase_records_3m(self, three_months_ago, today, cust_list):
        with self.db() as db:
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

    def get_response_data_3m(self, audience_id: str, three_months_ago, yst_date):
        with self.db() as db:
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
                    SendReservationEntity.campaign_id
                    == campaigns_subquery.c.campaign_id,
                )
                .filter(
                    SendReservationEntity.test_send_yn == "n",
                    SendReservationEntity.audience_id == audience_id,
                )
                .group_by(
                    SendReservationEntity.campaign_id, SendReservationEntity.cus_cd
                )
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
                        send_count_subquery.c.cus_cd
                        == response_count_subquery.c.cus_cd,
                    ),
                )
                .group_by(
                    send_count_subquery.c.campaign_id, send_count_subquery.c.cus_cd
                )
            )

    def insert_audience_stats(
        self,
        audience_id,
        insert_to_audience_stats,
        insert_to_count_by_month_list,
        insert_to_rep_product_list,
        main_rep_nm_list,
    ):
        with self.db() as db:
            # #audience_count_by_month -bulk
            insert_to_count_by_month_list_add = [
                {**data_dict, "audience_id": audience_id}
                for data_dict in insert_to_count_by_month_list
            ]

            print("insert_to_count_by_month_list_add")
            print(insert_to_count_by_month_list_add)

            insert_query = AudienceCountByMonthEntity.__table__.insert().values(
                insert_to_count_by_month_list_add
            )
            print(insert_query)

            db.execute(insert_query)
            # #audience_stats
            insert_to_audience_stats["audience_id"] = audience_id

            print("insert_to_audience_stats")
            print(insert_to_audience_stats)
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
