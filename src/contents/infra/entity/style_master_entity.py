# class StyleMasterEntity(Base):
#     __tablename__ = "style_master"
#
#     comp_cd = Column(String(4))
#     br_div = Column(String(5))
#     sty_cd = Column(String, primary_key=True, index=True)
#     sty_nm = Column(String, nullable=False)
#     rep_nm = Column(String, nullable=False)
#     year_cd = Column(String(2), nullable=False)
#     year2 = Column(String, nullable=False)
#     item_gu = Column(String(4))
#     item_gu_nm = Column(String(4))
#     kids_yn = Column(String(2))
#     running_yn = Column(String)
#     season = Column(String(5), nullable=False)
#     sty_season_nm = Column(String)
#     sty_season_grop_nm = Column(String)
#     sup_gu = Column(String)
#     sup_gu_grp_nm = Column(String)
#     it_gb = Column(String)
#     it_gb_nm = Column(String)
#     item = Column(String)
#     item_nm = Column(String)
#     item_sb = Column(String)
#     item_sb_nm = Column(String)
#     d_line = Column(String)
#     d_line_nm = Column(String)
#     purpose1 = Column(String)
#     purpose2 = Column(String)
#     purpose3 = Column(String)
#     prd_fit = Column(String)
#     prd_length = Column(String)
#     prd_core_mat = Column(String)
#     prd_design = Column(String)
#     prd_target = Column(String)
#     sty_gb = Column(String)
#     cons_pri = Column(Integer, nullable=False)
#     image_path = Column(String)
#     des_remark = Column(String)
#     des_remark_mood = Column(String)
#     des_remark_tpo = Column(String)
#     des_remark_func = Column(String)
#     des_remark_mat = Column(String)
#     des_remark_eco = Column(String)
#     des_remark_add = Column(String)
#     down_wgt = Column(String)
#     additional_description = Column(String)
#     size_range = Column(String)
#     colors = Column(String)
#     sex = Column(String)
#     inte_d_line = Column(String)
#     eco_yn = Column(String)
#     etl_time = Column(DateTime(timezone=True), default=datetime.now())
