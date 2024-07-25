from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import and_, func, literal
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.audiences.infra.entity.audience_count_by_month_entity import (
    AudienceCountByMonthEntity,
)
from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
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
from src.dashboard.infra.entity.dash_end_table_entity import DashEndTableEntity


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

    def get_audience_cust_with_audience_id(self, audience_id, db: Session):
        return db.query(AudienceCustomerMappingEntity.cus_cd).filter(
            AudienceCustomerMappingEntity.audience_id == audience_id
        )

    def get_all_customer_count(self, db: Session):
        return db.query(func.distinct(CustomerInfoStatusEntity.cus_cd).label("cus_cd")).count()

    def get_purchase_records_3m(self, three_months_ago, today, cust_list, db: Session):
        return db.query(
            PurchaseAnalyticsMasterStyle.cus_cd,
            PurchaseAnalyticsMasterStyle.recp_no,
            PurchaseAnalyticsMasterStyle.sale_dt,
            PurchaseAnalyticsMasterStyle.product_code,
            PurchaseAnalyticsMasterStyle.product_name,
            PurchaseAnalyticsMasterStyle.rep_nm,
            PurchaseAnalyticsMasterStyle.sale_qty,
            PurchaseAnalyticsMasterStyle.sale_amt,
        ).filter(
            PurchaseAnalyticsMasterStyle.sale_dt.between(three_months_ago, today),
            PurchaseAnalyticsMasterStyle.cus_cd.in_(cust_list),
        )

    def get_response_data_3m(self, audience_id: str, three_months_ago, yst_date, db: Session):
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
                DashEndTableEntity.cus_cd,
                DashEndTableEntity.campaign_id,
                literal(1).label("response_count"),
            )
            .group_by(DashEndTableEntity.cus_cd, DashEndTableEntity.campaign_id)
            .having(func.sum(DashEndTableEntity.sale_amt) > 0)
            .subquery()
        )

        return (
            db.query(
                send_count_subquery.c.campaign_id,
                send_count_subquery.c.cus_cd,
                func.count(response_count_subquery.c.response_count).label("response_count"),
            )
            .outerjoin(
                response_count_subquery,
                and_(
                    send_count_subquery.c.campaign_id == response_count_subquery.c.campaign_id,
                    send_count_subquery.c.cus_cd == response_count_subquery.c.cus_cd,
                ),
            )
            .group_by(send_count_subquery.c.campaign_id, send_count_subquery.c.cus_cd)
        )

    def insert_audience_stats(
        self,
        audience_id,
        insert_to_audience_stats,
        insert_to_count_by_month_list,
        insert_to_rep_product_list,
        main_rep_nm_list,
        db: Session,
    ):
        # #audience_count_by_month -bulk
        insert_to_count_by_month_list_add = [
            {**data_dict, "audience_id": audience_id} for data_dict in insert_to_count_by_month_list
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

            # insert 구문 생성
            insert_stmt = insert(PrimaryRepProductEntity).values(insert_to_rep_product_list_add)

            # 업데이트할 컬럼 설정 (여기서는 모든 컬럼을 업데이트)
            update_dict = {
                col.name: col
                for col in insert_stmt.excluded
                if col.name not in ("audience_id", "main_product_id")
            }

            # on_conflict_do_update 설정
            on_conflict_stmt = insert_stmt.on_conflict_do_update(
                index_elements=["audience_id", "main_product_id"], set_=update_dict
            )

            # upsert 쿼리 실행
            db.execute(on_conflict_stmt)
        db.commit()
