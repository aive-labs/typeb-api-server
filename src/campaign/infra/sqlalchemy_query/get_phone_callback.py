from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.users.infra.entity.user_entity import UserEntity


def get_phone_callback(user_id, db: Session):
    user = db.query(UserEntity).filter(UserEntity.user_id == user_id).first()

    if not user:
        raise NotFoundException(detail={"message": "사용자를 찾지 못했습니다."})

    if user.sys_id == "WP":
        # 영업점 : 매장 번호
        phone_callback = user.test_callback_number

    elif user.sys_id == "HO":

        if user.parent_dept_cd == "50D000":
            # 영업팀
            phone_callback = "{{주관리매장전화번호}}"

        else:
            # 본사 : 대표번호
            phone_callback = "1666-3096"

    else:
        raise ValueError("valid sys_id")

    return phone_callback
