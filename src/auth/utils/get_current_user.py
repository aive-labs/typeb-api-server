from dependency_injector.wiring import Provide, inject
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from src.core.container import Container
from src.core.exceptions import AuthError, CredentialError, NotFoundError
from src.users.infra.user_repository import UserRepository

reuseable_oauth = OAuth2PasswordBearer(tokenUrl="/token", scheme_name="JWT")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"


@inject
def get_current_user(
    self,
    token: str = Depends(reuseable_oauth),
    user_repository: UserRepository = Depends(Provide[Container.user_repository]),
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise AuthError("해당하는 이메일을 찾지 못하였습니다.")
    except JWTError as e:
        raise CredentialError("유효하지 않은 토큰입니다.") from e

    user = user_repository.get_user_by_email(email=email)
    if user is None:
        raise NotFoundError("해당하는 사용자를 찾지 못하였습니다.")

    return user
