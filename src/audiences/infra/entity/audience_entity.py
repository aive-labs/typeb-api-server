from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, text
from sqlalchemy.orm import relationship

from src.core.database import Base as Base


class AudienceEntity(Base):
    __tablename__ = "audiences"

    audience_id = Column(
        String,
        primary_key=True,
        index=True,
        server_default=text("'aud-' || LPAD(nextval('audience_seq')::TEXT, 6, '0')"),
    )
    audience_name = Column(String, nullable=False)
    main_mix_lv1 = Column(String)
    audience_status_code = Column(String, nullable=False)
    audience_status_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    create_type_code = Column(String, nullable=True)
    target_strategy = Column(String, nullable=True)
    owned_by_dept = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
    updated_by = Column(String, nullable=False, default=text("(user)"))
    is_exclude = Column(Boolean, nullable=False, default=False)
    update_cycle = Column(String(15), nullable=False, default="skip")
    default_excl_on_camp = Column(Boolean, nullable=False, default=False)
    user_exc_deletable = Column(Boolean, nullable=True)

    mapping = relationship("StrategyThemeAudienceMappingEntity", backref="audiences")
