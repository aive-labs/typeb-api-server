from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.main.database import Base


class SubscriptionPlanEntity(Base):
    __tablename__ = "subscription_plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)
    price = Column(Integer, nullable=False)
    description = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())

    subscriptions = relationship(
        "SubscriptionEntity",
        back_populates="plan",
    )


class SubscriptionEntity(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    plan_id = Column(Integer, ForeignKey("subscription_plans.id"), nullable=False)
    status = Column(String, nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    auto_renewal = Column(Boolean, default=True)
    last_payment_date = Column(DateTime(timezone=True))
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())

    plan = relationship("SubscriptionPlanEntity", back_populates="subscriptions")
