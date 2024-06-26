from sqlalchemy import Column, Integer, String

from src.core.database import Base as Base


class CustomerInfoStatusEntity(Base):
    __tablename__ = "cus_info_status"

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
