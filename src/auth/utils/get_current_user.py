from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.auth.infra.cafe24_repository import Cafe24Repository
from src.auth.service.auth_service import reuseable_oauth
from src.common.utils.get_env_variable import get_env_variable
from src.core.container import Container
from src.core.db_dependency import get_db
from src.core.exceptions.exceptions import AuthException, CredentialException
from src.payment.routes.dto.response.my_subscription import MySubscription
from src.users.infra.user_repository import UserRepository


@inject
def get_current_user(
    token: str = Depends(reuseable_oauth),
    db: Session = Depends(get_db),
    user_repository: UserRepository = Depends(Provide[Container.user_repository]),
    cafe24_repository: Cafe24Repository = Depends(Provide[Container.cafe24_repository]),
):
    try:
        secret_key = get_env_variable("secret_key")
        algorithm = get_env_variable("hash_algorithm")
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        email = payload.get("email")
        if email is None:
            raise AuthException(detail={"message": "해당하는 이메일을 찾지 못하였습니다."})
    except JWTError as e:
        raise CredentialException(detail={"message": "유효하지 않은 토큰입니다."}) from e

    user = user_repository.get_user_by_email(email=email, db=db)

    if user is None:
        raise AuthException(detail={"message": "해당 사용자를 찾지 못했습니다."})

    if user.user_id is None:
        raise AuthException(detail={"message": "해당 사용자 id를 찾지 못했습니다."})

    cafe24_info = cafe24_repository.get_cafe24_info_by_user_id(str(user.user_id), db=db)

    if cafe24_info:
        mall_id = cafe24_info.mall_id if cafe24_info.mall_id else None
        user.mall_id = mall_id

    my_subscription = payload.get("subscription")
    if my_subscription:
        user.subscription = MySubscription(
            id=my_subscription["id"],
            name=my_subscription["name"],
            end_date=my_subscription["end_date"],
        )
    return user
