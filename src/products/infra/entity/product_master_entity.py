from sqlalchemy import (
    TIMESTAMP,
    BigInteger,
    Column,
    DateTime,
    Integer,
    String,
    func,
    text,
)

from src.core.database import Base


class ProductMasterEntity(Base):
    __tablename__ = "product_master"

    shop_no = Column(Integer)
    product_no = Column(Integer)
    product_code = Column(String, primary_key=True, index=True)
    custom_product_code = Column(String)
    brand_code = Column(String)
    trend_code = Column(String)
    product_name = Column(String)
    eng_product_name = Column(String)
    supply_product_name = Column(String)
    internal_product_name = Column(String)
    model_name = Column(String)
    brand_name = Column(String)
    trend_name = Column(String)
    category_no = Column(Integer)
    category_name = Column(String)
    category_depth = Column(String)
    full_category_name_1 = Column("full_category_name.1", String)
    full_category_name_2 = Column("full_category_name.2", String)
    full_category_name_3 = Column("full_category_name.3", String)
    full_category_name_4 = Column("full_category_name.4", String)
    full_category_no_1 = Column("full_category_no.1", String)
    full_category_no_2 = Column("full_category_no.2", String)
    full_category_no_3 = Column("full_category_no.3", String)
    full_category_no_4 = Column("full_category_no.4", String)
    is_bundle = Column(String)
    made_date = Column(TIMESTAMP(timezone=True))
    release_date = Column(TIMESTAMP(timezone=True))
    created_date = Column(TIMESTAMP(timezone=True))
    detail_image = Column(String)
    list_image = Column(String)
    tiny_image = Column(String)
    small_image = Column(String)
    additional_image = Column(String)
    display = Column(String)
    selling = Column(String)
    product_condition = Column(String)
    sold_out = Column(String)
    price = Column(String)
    retail_price = Column(String)
    additional_price = Column(String, nullable=True)
    discountprice = Column(BigInteger, nullable=True)
    cloth_fabric = Column(String)
    product_material = Column(String)
    summary_description = Column(String)
    simple_description = Column(String)
    product_tag = Column(String)
    buy_limit_by_product = Column(String)
    single_purchase_restriction = Column(String)
    adult_certification = Column(String)
    expiration_date_start_date = Column("expiration_date.start_date", String)
    expiration_date_end_date = Column("expiration_date.end_date", String)
    options = Column(String)
    variants = Column(String)
    exposure_limit_type = Column(String)
    exposure_group_list = Column(String)
    set_product_type = Column(String)
    shipping_fee_type = Column(String)
    main = Column(String)
    memos = Column(String)
    hits = Column(BigInteger)
    seo = Column(String)
    project_no = Column(String)
    exchange_info = Column(String)
    additional_information = Column(String)
    relational_product = Column(String)
    discount_value_unit = Column("period_sale.discount_value_unit", String, nullable=True)
    discount_value = Column("period_sale.discount_value", BigInteger, nullable=True)

    # 화면에서 수정 가능한 필드
    comment = Column(String)
    recommend_yn = Column(String, default="Y")
    rep_nm = Column(String)

    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    etltime = Column(TIMESTAMP(timezone=True))
