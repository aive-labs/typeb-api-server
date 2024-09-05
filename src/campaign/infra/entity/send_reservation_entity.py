from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)

from src.core.database import Base as Base


class SendReservationEntity(Base):
    __tablename__ = "send_reservation"

    send_resv_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    set_group_msg_seq = Column(Integer, ForeignKey("set_group_messages.set_group_msg_seq"))
    campaign_id = Column(String(10), nullable=False)
    campaign_name = Column(String(100))
    send_resv_date = Column(DateTime(timezone=True), nullable=False)
    send_resv_state = Column(String(2), nullable=False, server_default=text("'00'"))
    send_rslt_date = Column(DateTime(timezone=True))
    send_rslt_state = Column(String(4))
    phone_send = Column(String(15), nullable=False)
    phone_callback = Column(String(15), nullable=False)
    send_sv_type = Column(String(3), nullable=False)
    send_msg_type = Column(String(10), nullable=False)
    send_msg_subject = Column(String(40))
    send_msg_body = Column(String(3072))
    send_filecount = Column(Integer)
    send_filepath = Column(String)
    kko_yellowid = Column(String(100))
    kko_template_key = Column(String(50))
    kko_button_json = Column(String(3000))
    kko_ft_subject = Column(String(75))
    kko_ft_adflag = Column(String(1))
    kko_ft_wideimg = Column(String(1))
    kko_at_type = Column(String(20))
    kko_at_item_json = Column(String(1000))
    kko_at_accent = Column(String(69))
    kko_at_price = Column(Integer)
    kko_at_currency = Column(String(3))
    kko_send_timeout = Column(Integer)
    kko_ssg_retry = Column(Integer, nullable=False, server_default=text("0"))
    kko_resend_type = Column(String(5))
    kko_resend_msg = Column(String(2000))
    cus_cd = Column(String)
    msg_category = Column(String(8))
    remind_step = Column(Integer)
    sent_success = Column(String(5))
    shop_cd = Column(String(6))  # shop_cd
    shop_send_yn = Column(String, nullable=False)  # shop_send_yn
    test_send_yn = Column(String(5))
    audience_id = Column(String)
    coupon_no = Column(String)
    create_resv_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    create_resv_user = Column(String(20), nullable=False, default=text("(user)"))
    update_resv_date = Column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
    )
    update_resv_user = Column(String(20), nullable=False, default=text("(user)"))

    log_comment = Column(String)
    log_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
