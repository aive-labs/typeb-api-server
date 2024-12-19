from sqlalchemy import Column, String

from src.core.database import Base as Base


class PrimaryRepProductEntity(Base):
    __tablename__ = "primary_rep_product"

    audience_id = Column(String, primary_key=True, index=True)
    main_product_id = Column(String, primary_key=True, index=True)
    main_product_name = Column(String, nullable=False)
