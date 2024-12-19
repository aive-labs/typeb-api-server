from sqlalchemy import Column, DateTime, String, func

from src.main.database import Base


class OnboardingEntity(Base):
    __tablename__ = "onboarding"

    mall_id = Column(String, primary_key=True, nullable=False)
    onboarding_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
