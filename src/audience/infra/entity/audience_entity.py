from sqlalchemy import Boolean, Column, DateTime, Sequence, String, event, func, text
from sqlalchemy.orm import relationship

from src.main.database import Base as Base


class AudienceEntity(Base):
    __tablename__ = "audience"

    audience_id = Column(
        String,
        primary_key=True,
        index=True,
    )
    audience_name = Column(String, nullable=False)
    main_mix_lv1 = Column(String)
    audience_status_code = Column(String, nullable=False)
    audience_status_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    create_type_code = Column(String, nullable=True)
    target_strategy = Column(String, nullable=True)
    owned_by_dept = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    is_exclude = Column(Boolean, nullable=False, default=False)
    update_cycle = Column(String(15), nullable=False, default="skip")
    default_excl_on_camp = Column(Boolean, nullable=False, default=False)
    user_exc_deletable = Column(Boolean, nullable=True)

    mapping = relationship("StrategyThemeAudienceMappingEntity", backref="audience")


audience_id_seq = Sequence("audience_seq", schema="aivelabs_sv")


@event.listens_for(AudienceEntity, "before_insert")
def generate_custom_audience_id(mapper, connection, target):
    next_id = connection.execute(audience_id_seq)
    target.audience_id = f"aud-{str(next_id).zfill(6)}"
