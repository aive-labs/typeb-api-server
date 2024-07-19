from sqlalchemy.orm import Session

from src.users.infra.entity.user_entity import UserEntity


def validate_phone_callback(phone_callback, db: Session):
    select_query = db.query(UserEntity).filter(
        # UserEntity.sys_id == 'WP', #매장사용자
        UserEntity.test_callback_number
        == phone_callback
    )

    return db.query(select_query.exists()).scalar()
