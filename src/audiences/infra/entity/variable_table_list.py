from sqlalchemy import ARRAY, Column, Integer, String

from src.core.database import Base

# class CustomerInfoStatusEntity(Base):
#     __tablename__ = "temp_cus_info_status"
#
#     cus_info_id = Column(Integer, primary_key=True)
#     shop_no = Column(BigInteger, nullable=False)
#     cus_cd = Column(String, nullable=True)
#     gender = Column(String, nullable=True)
#     this_year_birth_day = Column(String, nullable=True)
#     this_year_wedding_anniversary = Column(String, nullable=True)
#     age = Column(String, nullable=True)
#     age_group = Column(String, nullable=True)
#     created_date = Column(Date, nullable=True)
#     group_no = Column(BigInteger, nullable=True)
#     group_name = Column(String, nullable=True)
#     last_login_date = Column(Date, nullable=True)
#     last_purchase_date = Column(String, nullable=True)
#     last_purchase_months_ago = Column(String, nullable=True)
#     first_purchase_date = Column(String, nullable=True)
#     sms = Column(String, nullable=True)
#     news_mail = Column(String, nullable=True)
#     member_authentification = Column(String, nullable=True)
#     available_points = Column(String, nullable=True)
#     used_points = Column(String, nullable=True)
#     total_points = Column(String, nullable=True)
#     sale_amt_year = Column(String, nullable=True)
#     cv_model = Column(String, nullable=True)
#     r_score_3m = Column(Float, nullable=True)
#     f_score_3m = Column(Float, nullable=True)
#     m_score_3m = Column(Float, nullable=True)
#     rfm_score_3m = Column(String, nullable=True)
#     r_score_6m = Column(Float, nullable=True)
#     f_score_6m = Column(Float, nullable=True)
#     m_score_6m = Column(Float, nullable=True)
#     rfm_score_6m = Column(String, nullable=True)
#     r_score_9m = Column(Float, nullable=True)
#     f_score_9m = Column(Float, nullable=True)
#     m_score_9m = Column(Float, nullable=True)
#     rfm_score_9m = Column(String, nullable=True)
#     r_score_1y = Column(Float, nullable=True)
#     f_score_1y = Column(Float, nullable=True)
#     m_score_1y = Column(Float, nullable=True)
#     rfm_score_1y = Column(String, nullable=True)
#     etltime = Column(Date, nullable=True)


class CustomerInfoStatusEntity(Base):
    __tablename__ = "temp_cus_info_status"

    cus_info_status_seq = Column(Integer, primary_key=True)
    cus_cd = Column(String, primary_key=True)
    sex = Column(String, nullable=True)
    sex_nm = Column(String, nullable=True)
    this_year_birthday = Column(String, nullable=True)
    age = Column(Integer)
    age_group_10 = Column(String, nullable=True)
    age_group_5 = Column(String, nullable=True)
    hp_no_valid_yn = Column(String, nullable=True)
    join_dt = Column(String, nullable=True)
    join_shop = Column(String, nullable=True)
    join_re_shop_cd2 = Column(String, nullable=True)
    join_shop_tp2 = Column(String, nullable=True)
    join_shop_tp2_nm = Column(String, nullable=True)
    join_shop_tp4 = Column(String, nullable=True)
    join_shop_tp4_nm = Column(String, nullable=True)
    join_shop_tp5 = Column(String, nullable=True)
    join_shop_tp5_nm = Column(String, nullable=True)
    join_area = Column(String, nullable=True)
    join_area_nm = Column(String, nullable=True)
    join_team_cd = Column(String, nullable=True)
    join_team_nm = Column(String, nullable=True)
    nepa_join_dt = Column(String, nullable=True)
    main_shop = Column(String, nullable=True)
    main_re_shop_cd2 = Column(String, nullable=True)
    main_shop_tp2 = Column(String, nullable=True)
    main_shop_tp2_nm = Column(String, nullable=True)
    main_shop_tp4 = Column(String, nullable=True)
    main_shop_tp4_nm = Column(String, nullable=True)
    main_shop_tp5 = Column(String, nullable=True)
    main_shop_tp5_nm = Column(String, nullable=True)
    main_area = Column(String, nullable=True)
    main_area_nm = Column(String, nullable=True)
    main_team_cd = Column(String, nullable=True)
    main_team_nm = Column(String, nullable=True)
    kids_yn = Column(String, nullable=True)
    cus_grade1 = Column(String, nullable=True)
    cus_grade1_nm = Column(String, nullable=True)
    sale_amt_year = Column(Integer)
    next_cus_grade = Column(String, nullable=True)
    next_cus_grade_nm = Column(String, nullable=True)
    rest_amt = Column(Integer)
    cus_div = Column(String, nullable=True)
    cus_div_nm = Column(String, nullable=True)
    illegality_yn = Column(String, nullable=True)
    last_contact_dt = Column(String, nullable=True)
    buy_shop_dt = Column(String, nullable=True)
    last_purchase_months_ago = Column(Integer, nullable=True)
    expected_date_dormancy = Column(String, nullable=True)
    sms_rcv_yn = Column(String, nullable=True)
    adver_rcv_yn_email = Column(String, nullable=True)
    cv_model = Column(String, nullable=True)
    ord_lv1 = Column(String, nullable=True)
    prd_lv1 = Column(String, nullable=True)
    promo_lv1 = Column(String, nullable=True)
    mix_lv1 = Column(String, nullable=True)
    ord_lv2 = Column(String, nullable=True)
    prd_lv2 = Column(String, nullable=True)
    promo_lv2 = Column(String, nullable=True)
    ltv_frequency = Column(Integer)
    price_group = Column(String, nullable=True)
    first_sale_dt = Column(String, nullable=True)
    on_join_yn = Column(String, nullable=True)
    on_reg_dt = Column(String, nullable=True)
    on_user_no = Column(String, nullable=True)
    on_user_stat = Column(String, nullable=True)
    on_withdraw_dt = Column(String, nullable=True)
    on_withdraw_yn = Column(String, nullable=True)
    long_term_inactive_yn = Column(String, nullable=True)
    remain_point = Column(Integer)
    rep_it_gb_nm = Column(String, nullable=True)
    rep_item_nm = Column(String, nullable=True)
    rep_nm = Column(String, nullable=True)
    comp_send_term = Column(Integer)
    shop_send_term = Column(Integer)
    buy_within_14days_yn = Column(String, nullable=True)
    use_off_grd_cpn_yn = Column(String, nullable=True)
    use_on_grd_cpn_yn = Column(String, nullable=True)
    join_event_point = Column(String, nullable=True)


class CustomerProductPurchaseSummaryEntity(Base):
    __tablename__ = "cus_product_purchase_summary"

    cus_product_prucahse_seq = Column(Integer, primary_key=True)
    cus_cd = Column(String, nullable=True)
    sup_gu_grp_nm = Column(String, nullable=True)
    it_gb_nm = Column(String, nullable=True)
    item_nm = Column(String, nullable=True)
    item_sb_nm = Column(String, nullable=True)
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
