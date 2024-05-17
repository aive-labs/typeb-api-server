from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from src.core.database import BaseModel as Base


class UserEntity(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    user_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(30), nullable=False)
    role_id = Column(String(15), unique=False, nullable=False)
    photo_uri = Column(String, unique=False)
    department_id = Column(String(20), unique=False, nullable=False)
    email = Column(String(20), unique=True, nullable=False)
    language = Column(String(10), unique=False, nullable=False)
    last_login = Column(DateTime)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
    login_id = Column(String(20), unique=True)
    erp_id = Column(String(20))
    sys_id = Column(String(2))
    boan_admin = Column(String(1))
    gw_position_cd = Column(String(10))
    gw_position_nm = Column(String(20))
    department_name = Column(String(150))
    department_abb_name = Column(String(150))
    test_callback_number = Column(String(20))
    cell_phone_number = Column(String(20))
    messenger_comment = Column(String(300))
    branch_manager = Column(String(20))
    parent_dept_cd = Column(String(20))

    # 1:n relationship
    # approvers = relationship('Approvers', backref='users')
