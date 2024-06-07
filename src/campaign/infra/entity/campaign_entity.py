from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base as Base


class CampaignEntity(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(
        String,
        primary_key=True,
        index=True,
        server_default=text(
            "'cam-' || LPAD(nextval('aivelabs_sv.campaign_seq')::TEXT, 6, '0')"
        ),
    )
    campaign_name = Column(String, nullable=False)
    campaign_group_id = Column(
        String,
        nullable=False,
        server_default=text(
            "'grp-' || LPAD(nextval('aivelabs_sv.campaign_grp_seq')::TEXT, 6, '0')"
        ),
    )
    budget = Column(Integer, nullable=True)
    campaign_type_code = Column(String, nullable=False)
    campaign_type_name = Column(String, nullable=False)
    audience_type_code = Column(String, nullable=True)
    medias = Column(String, nullable=False)
    campaign_status_group_code = Column(String, nullable=False)
    campaign_status_group_name = Column(String, nullable=False)
    campaign_status_code = Column(String, nullable=False)
    campaign_status_name = Column(String, nullable=False)
    send_type_code = Column(String, nullable=False)
    send_type_name = Column(String, nullable=False)
    repeat_type = Column(String, nullable=True)
    week_days = Column(String, nullable=True)
    send_date = Column(String, nullable=True)
    is_msg_creation_recurred = Column(Boolean, nullable=False)
    is_approval_recurred = Column(Boolean, nullable=False)
    datetosend = Column(String, nullable=True)
    timetosend = Column(String, nullable=False)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    group_end_date = Column(String)
    has_remind = Column(Boolean, nullable=False)
    campaigns_exc = Column(ARRAY(String), nullable=True)
    audiences_exc = Column(ARRAY(String), nullable=True)
    strategy_id = Column(String, ForeignKey("aivelabs_sv.strategies.strategy_id"))
    campaign_theme_ids = Column(ARRAY(Integer), nullable=True)
    is_personalized = Column(Boolean, nullable=False)
    progress = Column(String, nullable=False)
    msg_delivery_vendor = Column(String, nullable=False)
    shop_send_yn = Column(String, nullable=False)
    retention_day = Column(String, nullable=True)
    owned_by_dept = Column(String, nullable=False)
    owned_by_dept_name = Column(String, nullable=False)  # 생성 부서명
    owned_by_dept_abb_name = Column(String, nullable=False)  # 생성 부서명2
    created_at = Column(DateTime(timezone=True))
    created_by = Column(String, nullable=False)
    created_by_name = Column(String, nullable=False)  # 생성 유저명
    updated_at = Column(DateTime(timezone=True))
    updated_by = Column(String, nullable=False)

    # 1:n relationship
    remind_list = relationship(
        "CampaignRemindEntity", backref="campaigns", lazy=True, cascade="all, delete-orphan"
    )

    # 1:n relationship
    camp_sets = relationship(
        "CampaignSetsEntity", backref="campaigns", lazy=True, cascade="all, delete-orphan"
    )

    def as_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
