from sqlalchemy import TIMESTAMP, Column, Double, Index, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class GaViewMasterEntity(Base):
    __tablename__ = "ga_view_master"
    __table_args__ = (
        Index("idx_visit_product", "visit_dt"),  # event_date와 product_code에 인덱스 생성
        Index("idx_visit_product", "product_code"),  # event_date와 product_code에 인덱스 생성
        Index(
            "idx_visit_product", "visit_dt", "product_code"
        ),  # event_date와 product_code에 인덱스 생성
        Index("idx_category1", "full_category_name_1"),  # full_category_name.1에 인덱스 생성
        Index("idx_category2", "full_category_name_2"),  # full_category_name.2에 인덱스 생성
        Index("idx_category3", "full_category_name_3"),  # full_category_name.3에 인덱스 생성
        Index(
            "idx_visit_category1", "visit_dt", "full_category_name_1"
        ),  # full_category_name.1에 인덱스 생성
        Index(
            "idx_visit_category2", "visit_dt", "full_category_name_2"
        ),  # full_category_name.2에 인덱스 생성
        Index(
            "idx_visit_category3", "visit_dt", "full_category_name_3"
        ),  # full_category_name.3에 인덱스 생성
    )

    cus_cd = Column(String, nullable=False, primary_key=True)
    event_date = Column(String, nullable=False, primary_key=True)
    page_title = Column(String, nullable=False, primary_key=True)
    page_entry_time = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    product_code = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    full_category_name_1 = Column(String, nullable=True)
    full_category_name_2 = Column(String, nullable=True)
    full_category_name_3 = Column(String, nullable=True)
    engagement_time_sec = Column(Double, nullable=True)
    etltime = Column(TIMESTAMP(timezone=True))
