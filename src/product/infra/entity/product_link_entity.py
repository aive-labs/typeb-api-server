from sqlalchemy import Column, DateTime, Integer, String, func, text

from src.core.database import Base


class ProductLinkEntity(Base):
    __tablename__ = "product_links"

    product_link_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_code = Column(String)
    link_type = Column(String)
    title = Column(String)
    link = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
