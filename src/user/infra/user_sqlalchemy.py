from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.search.routes.dto.send_user_response import SendUserResponse
from src.user.domain.user import User
from src.user.infra.entity.user_entity import UserEntity
from src.user.infra.entity.user_password import UserPasswordEntity
from src.user.infra.entity.user_whitelist import UserWhitelist
from src.user.routes.dto.request.user_modify import UserModify


class UserSqlAlchemy:

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
        # jwt 토큰 발급을 위해 is_aivelabs_admin false 조건 확인 안함
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

    def get_user_by_id(self, user_id: int, db: Session):
        entity = (
            db.query(UserEntity)
            .filter(UserEntity.user_id == user_id, UserEntity.is_aivelabs_admin.is_(False))
            .first()
        )
        if entity is None:
            raise NotFoundException(detail={"message": "사용자를 찾지 못했습니다."})
        return entity

    def get_all_users(self, db: Session):
        return db.query(UserEntity, UserEntity.is_aivelabs_admin.is_(False)).all()

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
            .filter(UserEntity.login_id == login_id, UserEntity.is_aivelabs_admin.is_(False))
            .first()
        )

    def delete_user(self, user_id: int, db: Session):

        user = (
            db.query(UserEntity)
            .filter(UserEntity.user_id == user_id, UserEntity.is_aivelabs_admin.is_(False))
            .first()
        )
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

        db.query(UserEntity).filter(
            UserEntity.user_id == user_modify.user_id, UserEntity.is_aivelabs_admin.is_(False)
        ).update(modified_user_dict)
        db.commit()

    def get_send_user(self, db: Session, keyword=None) -> list[SendUserResponse]:
        base_query = db.query(
            func.concat(UserEntity.username, "/", UserEntity.department_abb_name).label(
                "user_name_object"
            ),
            UserEntity.test_callback_number,
            UserEntity.cell_phone_number,
            UserEntity.sys_id,
        ).filter(UserEntity.is_aivelabs_admin.is_(False))

        if keyword:
            keyword = f"%{keyword}%"
            base_query = base_query.filter(
                or_(
                    UserEntity.username.ilike(keyword),
                    UserEntity.department_abb_name.ilike(keyword),
                )
            )

        entities = base_query.all()

        recipient_response = [
            SendUserResponse(
                user_name_object=entity.user_name_object,
                test_callback_number=entity.cell_phone_number,
            )
            for entity in entities
        ]

        return recipient_response
