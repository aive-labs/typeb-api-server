from sqlalchemy import BigInteger, Column, event

from src.main.database import Base


class RemainingCreditEntity(Base):
    __tablename__ = "remaining_credit"
    remaining_credit = Column(BigInteger, nullable=False, primary_key=True)


@event.listens_for(RemainingCreditEntity.__table__, "after_create")
def insert_initial_value(target, connection, **kw):
    connection.execute(target.insert().values(remaining_credit=0))
