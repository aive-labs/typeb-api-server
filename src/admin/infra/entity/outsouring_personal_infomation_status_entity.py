from sqlalchemy import Column, DateTime, String, event, func

from src.main.database import Base


class OutSouringPersonalInformationStatusEntity(Base):
    __tablename__ = "outsourcing_personal_information_status"

    term_status = Column(String, nullable=False, primary_key=True)

    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)


@event.listens_for(OutSouringPersonalInformationStatusEntity.__table__, "after_create")
def insert_personal_information_initial_value(target, connection, **kw):
    connection.execute(
        target.insert().values(term_status="pending", created_by="aivelabs", updated_by="aivelabs")
    )
