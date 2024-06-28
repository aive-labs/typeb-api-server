from core.database import get_db_session
from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.auth.infra.cafe24_repository import Cafe24Repository
from src.auth.service.auth_service import ALGORITHM, SECRET_KEY, reuseable_oauth
from src.core.container import Container
from src.core.exceptions.exceptions import AuthException, CredentialException
from src.core.schema import schema_context
from src.users.infra.user_repository import UserRepository


@inject
def get_current_user(
    token: str = Depends(reuseable_oauth),
    db: Session = Depends(get_db_session),
    user_repository: UserRepository = Depends(Provide[Container.user_repository]),
    cafe24_repository: Cafe24Repository = Depends(Provide[Container.cafe24_repository]),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise AuthException("해당하는 이메일을 찾지 못하였습니다.")
    except JWTError as e:
        raise CredentialException("유효하지 않은 토큰입니다.") from e

    user = user_repository.get_user_by_email(email=email, db=db)

    if user is None:
        raise AuthException("해당 사용자를 찾지 못했습니다.")

    if user.user_id is None:
        raise AuthException("해당 사용자 id를 찾지 못했습니다.")

    cafe24_info = cafe24_repository.get_cafe24_info_by_user_id(str(user.user_id), db=db)

    if cafe24_info:
        mall_id = cafe24_info.mall_id if cafe24_info.mall_id else None
        user.mall_id = mall_id

        print(f"Cafe24: Login Mall Id -> Schema: {mall_id}")
        schema_context.set(mall_id if mall_id else "aivelabs_sv")
    else:
        print("Non Cafe24: Login Mall Id -> Schema: aivelabs_sv")
        schema_context.set("aivelabs_sv")

    return user
