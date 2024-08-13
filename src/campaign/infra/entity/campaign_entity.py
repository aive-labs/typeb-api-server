from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    event,
    func,
)
from sqlalchemy.orm import relationship

from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.core.database import Base


class CampaignEntity(Base):
    __tablename__ = "campaigns"

    campaign_id = Column(
        String,
        primary_key=True,
        index=True,
    )
    campaign_name = Column(String, nullable=False)
    campaign_group_id = Column(
        String,
        nullable=False,
    )
    budget = Column(Integer, nullable=True)
    campaign_type_code = Column(String, nullable=False)
    campaign_type_name = Column(String, nullable=False)
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
    strategy_id = Column(String, ForeignKey("strategies.strategy_id"))
    strategy_theme_ids = Column(ARRAY(Integer), nullable=True)
    is_personalized = Column(Boolean, nullable=False)
    progress = Column(String, nullable=False)
    msg_delivery_vendor = Column(String, nullable=False)
    shop_send_yn = Column(String, nullable=False)
    retention_day = Column(Integer, nullable=True)
    owned_by_dept = Column(String, nullable=False)
    owned_by_dept_name = Column(String, nullable=False)  # 생성 부서명
    owned_by_dept_abb_name = Column(String, nullable=False)  # 생성 부서명2
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    created_by_name = Column(String, nullable=False)  # 생성 유저명
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False)

    # 1:n relationship

    # 1:n relationship
    remind_list = relationship(
        CampaignRemindEntity,
        back_populates="campaigns",
        lazy=True,
        cascade="all, delete-orphan",
    )

    # 1:n relationship
    camp_sets = relationship(
        CampaignSetsEntity,
        backref="campaigns",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


campaign_id_seq = Sequence("campaign_seq", schema="aivelabs_sv")
campaign_group_id_seq = Sequence("campaign_grp_seq", schema="aivelabs_sv")


@event.listens_for(CampaignEntity, "before_insert")
def generate_custom_campaign_id(mapper, connection, target):
    next_id = connection.execute(campaign_id_seq)
    target.campaign_id = f"cam-{str(next_id).zfill(6)}"

    next_grp_id = connection.execute(campaign_group_id_seq)
    target.campaign_group_id = f"grp-{str(next_grp_id).zfill(6)}"
