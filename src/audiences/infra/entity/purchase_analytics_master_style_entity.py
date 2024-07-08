from sqlalchemy import TIMESTAMP, BigInteger, Column, Date, Integer, String

from src.core.database import Base


class PurchaseAnalyticsMasterStyle(Base):
    __tablename__ = "temp_purchase_analytics_master_style"

    purchase_analytics_master_style_seq = Column(Integer, primary_key=True)
    recp_no = Column(String)
    cus_cd = Column(String)
    age = Column(String)
    sex = Column(String)
    shop_cd = Column(BigInteger)
    sale_dt = Column(String)
    yoil_nm = Column(String)
    sty_cd = Column(String)
    sty_nm = Column(String)
    sale_qty = Column(BigInteger)
    sale_amt = Column(BigInteger)
    cons_amt = Column(BigInteger)
    dc_rate = Column(String)
    milege_usage = Column(BigInteger)
    event_no = Column(String)
    rep_nm = Column(String)
    order_item_code = Column(String)
    market_id = Column(String)
    market_order_no = Column(String)
    item_no = Column(BigInteger)
    product_no = Column(BigInteger)
    option_id = Column(String)
    option_value = Column(String)
    option_price = Column(Integer)
    additional_discount_price = Column(Integer)
    coupon_discount_price = Column(Integer)
    app_item_discount_amount = Column(Integer)
    actual_order_amount_payment_amount = Column(
        "actual_order_amount.payment_amount", Integer
    )
    actual_refund_amount = Column(Integer)
    paid = Column(String)
    canceled = Column(String)
    payment_confirmation = Column(String)
    gift = Column(String)
    status_code = Column(String)
    status_text = Column(String)
    benefit_no = Column(String)
    benefit_code = Column(String)
    benefit_title = Column(String)
    benefit_percent = Column(String)
    benefit_value = Column(String)
    coupon_name = Column(String)
    coupon_percent = Column(String)
    coupon_value = Column(String)
    coupon_value_final = Column(String)
    group_no = Column(BigInteger)
    group_name = Column(String)
    name = Column(String)
    nick_name = Column(String)
    cellphone = Column(String)
    phone = Column(String)
    email = Column(String)
    wedding_anniversary = Column(String)
    city = Column(String)
    state = Column(String)
    zipcode = Column(String)
    address1 = Column(String)
    address2 = Column(String)
    birthday = Column(String)
    solar_calendar = Column(String)
    lifetime_member = Column(String)
    join_path = Column(String)
    sms = Column(String)
    news_mail = Column(String)
    member_authentification = Column(String)
    use_mobile_app = Column(String)
    use_blacklist = Column(String)
    blacklist_type = Column(String)
    total_points = Column(String)
    available_points = Column(String)
    last_login_date = Column(Date)
    brand_code = Column(String)
    trend_code = Column(String)
    eng_product_name = Column(String)
    supply_product_name = Column(String)
    internal_product_name = Column(String)
    model_name = Column(String)
    brand_name = Column(String)
    trend_name = Column(String)
    category_no = Column(BigInteger)
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
    made_date = Column(String)
    release_date = Column(String)
    created_date = Column(String)
    display = Column(String)
    selling = Column(String)
    product_condition = Column(String)
    sold_out = Column(String)
    price = Column(String)
    retail_price = Column(String)
    cloth_fabric = Column(String)
    product_material = Column(String)
    summary_description = Column(String)
    etltime = Column(TIMESTAMP(timezone=True))


# class PurchaseAnalyticsMasterStyle(Base):
#     __tablename__ = "purchase_analytics_master_style"
#
#     purchase_analytics_master_style_seq = Column(Integer, primary_key=True)
#     recp_no = Column(String, primary_key=True)
#     cus_cd = Column(String, primary_key=True)
#     age = Column(Integer)
#     sex = Column(String, nullable=True)
#     shop_cd = Column(String, nullable=True)
#     re_shop_cd2 = Column(String, nullable=True)
#     shop_tp2_nm = Column(String, nullable=True)
#     shop_tp4_nm = Column(String, nullable=True)
#     shop_tp5_nm = Column(String, nullable=True)
#     shop_mng_gb = Column(String, nullable=True)
#     shop_mng_gb_nm = Column(String, nullable=True)
#     team_cd = Column(String, nullable=True)
#     team_nm = Column(String, nullable=True)
#     sale_dt = Column(String, nullable=True)
#     yoil_nm = Column(String, nullable=True)
#     sty_cd = Column(String, primary_key=True)
#     sty_nm = Column(String, nullable=True)
#     running_yn = Column(String, nullable=True)
#     oldnew_yn = Column(String, nullable=True)
#     sale_qty = Column(Integer)
#     sale_amt = Column(Integer)
#     cons_amt = Column(Integer)
#     dc_rate = Column(Float)
#     milege_usage = Column(Integer)
#     event_tp = Column(String, nullable=True)
#     event_no = Column(String, nullable=True)
#     event_dc_amt = Column(Integer)
#     base_sale_pri = Column(Integer)
#     pnt_rate = Column(Integer)
#     pnt_samt = Column(Integer)
#     sty_season_nm = Column(String, nullable=True)
#     sty_season_grop_nm = Column(String, nullable=True)
#     year2 = Column(String, nullable=True)
#     sty_sex = Column(String, nullable=True)
#     it_gb_nm = Column(String, nullable=True)
#     item_nm = Column(String, nullable=True)
#     item_sb_nm = Column(String, nullable=True)
#     d_line_nm = Column(String, nullable=True)
#     sup_gu_grp_nm = Column(String, nullable=True)
#     purpose1 = Column(String, nullable=True)
#     purpose2 = Column(String, nullable=True)
#     purpose3 = Column(String, nullable=True)
#     rep_nm = Column(String, nullable=True)
#     prd_fit = Column(String, nullable=True)
#     prd_length = Column(String, nullable=True)
#     col_nm = Column(String, nullable=True)
#     col_gb_nm = Column(String, nullable=True)
#     prd_core_mat = Column(String, nullable=True)
#     size_cd = Column(String, nullable=True)
#     prd_design = Column(String, nullable=True)
#     prd_target = Column(String, nullable=True)
#     sty_gb = Column(String, nullable=True)
