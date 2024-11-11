from sqlalchemy import (
    TIMESTAMP,
    Column,
    Numeric,
    PrimaryKeyConstraint,
    String,
)

from src.core.database import Base


class DashDailyPurchaseMaster(Base):
    __tablename__ = "dash_daily_purchase_master"
    __table_args__ = {
        "schema": "aivelabs_sv",
        "primary_key": PrimaryKeyConstraint(
            "cus_cd",
            "order_item_code",
            name="dash_daily_purchase_master_pkey",
        ),
    }

    cus_cd = Column(String, primary_key=True, nullable=True)
    sale_dt = Column(String, nullable=True)
    recp_no = Column(String, nullable=True)
    order_item_code = Column(String, primary_key=True, nullable=True)
    product_name = Column(String, nullable=True)
    category_name = Column(String, nullable=True)
    rep_nm = Column(String, nullable=True)
    coupon_code = Column(String, nullable=True)
    sale_amt = Column(Numeric, nullable=True)
    sale_qty = Column(Numeric, nullable=True)
    etltime = Column(TIMESTAMP(timezone=True), nullable=True)
