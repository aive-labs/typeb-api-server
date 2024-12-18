from sqlalchemy import (
    ARRAY,
    TIMESTAMP,
    BigInteger,
    Column,
    Date,
    DateTime,
    Double,
    Float,
    Index,
    Integer,
    String,
)

from src.core.database import Base


class CustomerInfoStatusEntity(Base):
    __tablename__ = "cus_info_status"

    shop_no = Column(BigInteger, nullable=False)
    cus_cd = Column(String, nullable=False, primary_key=True)
    sex = Column(String, nullable=True)
    sex_nm = Column(String, nullable=True)
    this_year_birthday = Column(String, nullable=True)
    this_year_wedding_anniversary = Column(String, nullable=True)
    age = Column(String, nullable=True)
    age_group_10 = Column(String, nullable=True)
    age_group_5 = Column(String, nullable=True)
    created_date = Column(Date, nullable=True)

    group_no = Column(BigInteger, nullable=True)
    group_name = Column(String, nullable=True)
    last_login_date = Column(Date, nullable=True)
    last_purchase_date = Column(String, nullable=True)
    last_purchase_months_ago = Column(String, nullable=True)
    first_purchase_date = Column(String, nullable=True)

    sms = Column(String, nullable=True)
    news_mail = Column(String, nullable=True)
    member_authentication = Column(String, nullable=True)

    available_points = Column(Float, nullable=True)
    used_points = Column(Float, nullable=True)
    total_points = Column(Float, nullable=True)
    sale_amt_year = Column(String, nullable=True)

    cv_model = Column(String, nullable=True)
    r_score_3m = Column(Float, nullable=True)
    f_score_3m = Column(Float, nullable=True)
    m_score_3m = Column(Float, nullable=True)
    rfm_score_3m = Column(String, nullable=True)
    r_score_6m = Column(Float, nullable=True)
    f_score_6m = Column(Float, nullable=True)
    m_score_6m = Column(Float, nullable=True)
    rfm_score_6m = Column(String, nullable=True)
    r_score_9m = Column(Float, nullable=True)
    f_score_9m = Column(Float, nullable=True)
    m_score_9m = Column(Float, nullable=True)
    rfm_score_9m = Column(String, nullable=True)
    r_score_1y = Column(Float, nullable=True)
    f_score_1y = Column(Float, nullable=True)
    m_score_1y = Column(Float, nullable=True)
    rfm_score_1y = Column(String, nullable=True)

    coupon_expired = Column(String, nullable=True)
    coupon_list = Column(String, nullable=True)

    is_cart = Column(String, nullable=True)
    cart_product_no = Column(String, nullable=True)
    is_wishlist = Column(String, nullable=True)
    wishlist_product_no = Column(String, nullable=True)
    near_promotion_amount = Column(String, nullable=True)
    near_promotion_cnt = Column(String, nullable=True)
    promoted_customer = Column(String, nullable=True)
    promoted_date = Column(DateTime(timezone=True))

    purchase_cnt = Column(Integer, nullable=True)
    birthday_7_left = Column(String, nullable=True)
    first_purchase = Column(String, nullable=True)

    first_best_items = Column(String, nullable=True)
    best_promo_items = Column(String, nullable=True)
    best_gender_items = Column(String, nullable=True)
    best_category_items = Column(String, nullable=True)
    best_age_items = Column(String, nullable=True)
    best_new_items = Column(String, nullable=True)
    steady_items = Column(String, nullable=True)
    best_cross_items = Column(String, nullable=True)

    is_first_best_items = Column(String, nullable=True)
    is_steady_items = Column(String, nullable=True)
    is_best_new_items = Column(String, nullable=True)
    is_best_category_items = Column(String, nullable=True)
    is_best_promo_items = Column(String, nullable=True)
    is_best_cross_items = Column(String, nullable=True)

    first_best_items_link = Column(String, nullable=True)
    steady_items_link = Column(String, nullable=True)
    best_new_items_link = Column(String, nullable=True)
    best_category_items_link = Column(String, nullable=True)
    best_promo_items_link = Column(String, nullable=True)
    best_cross_items_link = Column(String, nullable=True)

    kakao_friends_yn = Column(String, nullable=True)
    etltime = Column(Date, nullable=True)


class CustomerProductPurchaseSummaryEntity(Base):
    __tablename__ = "cus_product_purchase_summary"

    cus_product_prucahse_seq = Column(Integer, primary_key=True)
    cus_cd = Column(String, nullable=True)
    sup_gu_grp_nm = Column(String, nullable=True)
    it_gb_nm = Column(String, nullable=True)
    item_nm = Column(String, nullable=True)
    item_sb_nm = Column(String, nullable=True)
    product_name = Column(String, nullable=True)
    option_value = Column(String, nullable=True)
    option_value_1 = Column(String, nullable=True)
    option_value_2 = Column(String, nullable=True)
    rep_nm = Column(String, nullable=True)
    purpose1 = Column(String, nullable=True)
    oldnew_yn = Column(String, nullable=True)
    col_gb_nm = Column(String, nullable=True)
    prd_length = Column(String, nullable=True)
    prd_fit = Column(String, nullable=True)
    prd_core_mat = Column(String, nullable=True)
    prd_design = Column(String, nullable=True)
    d_line_nm = Column(String, nullable=True)
    sty_season_nm = Column(String, nullable=True)
    sty_cd = Column(String, nullable=True)
    shop_tp2_nm = Column(String, nullable=True)
    shop_tp4_nm = Column(String, nullable=True)
    shop_tp5_nm = Column(String, nullable=True)
    sale_amt_before_3_years = Column(Integer)
    sale_amt_before_2_years = Column(Integer)
    sale_amt_before_1_year = Column(Integer)
    sale_amt_current_year = Column(Integer)
    sale_amt_2y = Column(Integer)
    sale_amt_1y = Column(Integer)
    sale_amt_6m = Column(Integer)
    sale_amt_3m = Column(Integer)
    sale_amt_1m = Column(Integer)
    sale_amt_ss = Column(Integer)
    sale_amt_fw = Column(Integer)
    sale_qty_before_3_years = Column(Integer)
    sale_qty_before_2_years = Column(Integer)
    sale_qty_before_1_year = Column(Integer)
    sale_qty_current_year = Column(Integer)
    sale_qty_2y = Column(Integer)
    sale_qty_1y = Column(Integer)
    sale_qty_6m = Column(Integer)
    sale_qty_3m = Column(Integer)
    sale_qty_1m = Column(Integer)
    sale_qty_ss = Column(Integer)
    sale_qty_fw = Column(Integer)
    sale_dt_array_before_3_years = Column(ARRAY(String), nullable=True)
    sale_dt_array_before_2_years = Column(ARRAY(String), nullable=True)
    sale_dt_array_before_1_year = Column(ARRAY(String), nullable=True)
    sale_dt_array_current_year = Column(ARRAY(String), nullable=True)
    sale_dt_array_2y = Column(ARRAY(String), nullable=True)
    sale_dt_array_1y = Column(ARRAY(String), nullable=True)
    sale_dt_array_6m = Column(ARRAY(String), nullable=True)
    sale_dt_array_3m = Column(ARRAY(String), nullable=True)
    sale_dt_array_1m = Column(ARRAY(String), nullable=True)
    sale_dt_array_ss = Column(ARRAY(String), nullable=True)
    sale_dt_array_fw = Column(ARRAY(String), nullable=True)
    milege_usage_before_3_years = Column(Integer)
    milege_usage_before_2_years = Column(Integer)
    milege_usage_before_1_year = Column(Integer)
    milege_usage_current_year = Column(Integer)
    milege_usage_2y = Column(Integer)
    milege_usage_1y = Column(Integer)
    milege_usage_6m = Column(Integer)
    milege_usage_3m = Column(Integer)
    milege_usage_1m = Column(Integer)
    milege_usage_ss = Column(Integer)
    milege_usage_fw = Column(Integer)


class GaViewMasterEntity(Base):
    __tablename__ = "ga_view_master"
    __table_args__ = (
        Index("ga_view_master_cus_cd_index", "cus_cd"),  # event_date와 product_code에 인덱스 생성
    )

    cus_cd = Column(String, nullable=False, primary_key=True)
    visit_dt = Column(String, nullable=False, primary_key=True)
    visit_page_title = Column("page_title", String, nullable=False, primary_key=True)
    page_entry_time = Column(TIMESTAMP(timezone=True), nullable=False, primary_key=True)
    visit_product_code = Column("product_code", String, nullable=True)
    visit_product_name = Column("product_name", String, nullable=True)
    visit_full_category_name_1 = Column("full_category_name_1", String, nullable=True)
    visit_full_category_name_2 = Column("full_category_name_2", String, nullable=True)
    visit_full_category_name_3 = Column("full_category_name_3", String, nullable=True)
    engagement_time_sec = Column(Double, nullable=True)
    etltime = Column(TIMESTAMP(timezone=True))
