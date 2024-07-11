from collections.abc import Callable
from contextlib import AbstractContextManager

from sqlalchemy.orm import Session

from src.users.domain.user import User
from src.users.infra.entity.user_entity import UserEntity
from src.users.infra.entity.user_password import UserPasswordEntity
from src.users.infra.entity.user_whitelist import UserWhitelist
from src.users.routes.dto.request.user_modify import UserModify


class UserSqlAlchemy:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def register_user(
        self,
        user_entity: UserEntity,
        user_password_entity: UserPasswordEntity,
        db: Session,
    ):

        db.add(user_entity)
        db.add(user_password_entity)
        db.commit()

        # commit을 하면 user_entity에 id값이 자동으로 할당이됨
        return User.from_entity(user_entity=user_entity)

    def find_user_by_email(self, email: str, db: Session):

        user = (
            db.query(UserEntity, UserPasswordEntity.login_pw)
            .join(
                UserPasswordEntity,
                UserEntity.login_id == UserPasswordEntity.login_id,
            )
            .filter(UserEntity.email == email)
            .first()
        )
        return user

    def get_user_signin(self, login_id: str, db: Session):

        return (
            db.query(UserEntity.user_id, UserEntity.login_id, UserPasswordEntity.login_pw)
            .join(
                UserPasswordEntity,
                UserEntity.login_id == UserPasswordEntity.login_id,
            )
            .filter(UserEntity.login_id == login_id)
            .first()
        )

    def get_user_by_id(self, user_id: int, db: Session):

        return db.query(UserEntity).filter(UserEntity.user_id == user_id).first()

    def get_all_users(self, db: Session):

        return db.query(UserEntity).all()

    def get_me(self, login_id: str, db: Session):

        return (
            db.query(
                UserEntity.user_id,
                UserEntity.username,
                UserEntity.email,
                UserEntity.login_id,
                UserEntity.role_id,
                UserEntity.photo_uri,
                UserEntity.sys_id,
                UserEntity.erp_id,
                UserEntity.department_id,
                UserEntity.department_name.label("department_full_name"),
                UserEntity.department_abb_name.label("department_name"),
                UserEntity.branch_manager,
                UserEntity.language,
                UserEntity.test_callback_number,
                UserEntity.parent_dept_cd,
            )
            .filter(UserEntity.login_id == login_id)
            .first()
        )

    def delete_user(self, user_id: int, db: Session):

        user = db.query(UserEntity).filter(UserEntity.user_id == user_id).first()
        if user:
            db.delete(user)
            db.commit()

    def get_whitelist_access(self, user_id: int, whitelist_field: str, db: Session):
        try:
            selected_col = getattr(UserWhitelist, whitelist_field)
        except AttributeError:
            return {"error": f"'{whitelist_field}' is not a valid field in UserWhitelist table"}

        return db.query(selected_col).filter(UserWhitelist.user_id == user_id).first()

    def update_user(self, user_modify: UserModify, db: Session):

        modified_user_dict = {
            key: value
            for key, value in user_modify.dict().items()
            if (key != "user_id") and (value is not None)
        }

        db.query(UserEntity).filter(UserEntity.user_id == user_modify.user_id).update(
            modified_user_dict
        )
        db.commit()
