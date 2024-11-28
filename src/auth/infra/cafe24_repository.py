from sqlalchemy.orm import Session

from src.auth.domain.cafe24_token import Cafe24Token
from src.auth.infra.cafe24_sqlalchemy_repository import Cafe24SqlAlchemyRepository
from src.auth.infra.dto.cafe24_mall_info import Cafe24MallInfo
from src.auth.infra.dto.cafe24_state_token import Cafe24StateToken
from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.service.port.base_cafe24_repository import BaseOauthRepository


class Cafe24Repository(BaseOauthRepository):

    def __init__(self, cafe24_sqlalchemy: Cafe24SqlAlchemyRepository):
        self.cafe24_sqlalchemy = cafe24_sqlalchemy

    def is_existing_state_token(self, state_token: str, db: Session) -> Cafe24StateToken:
        return self.cafe24_sqlalchemy.is_existing_state_token(state_token, db)

    def insert_basic_info(self, user_id: str, mall_id: str, state_token: str, db: Session):
        self.cafe24_sqlalchemy.insert_basic_info(user_id, mall_id, state_token, db)

    def get_state_token(self, state_token: str, db: Session) -> Cafe24StateToken:
        return self.cafe24_sqlalchemy.get_state_token(state_token, db)

    def save_tokens(self, cafe24_tokens: Cafe24TokenData, db: Session):
        self.cafe24_sqlalchemy.save_tokens(cafe24_tokens, db)

    def get_cafe24_info(self, user_id: str, db: Session) -> Cafe24MallInfo | None:
        return self.cafe24_sqlalchemy.get_cafe24_info(user_id, db)

    def get_token(self, mall_id: str, db: Session) -> Cafe24Token:
        return self.cafe24_sqlalchemy.get_token(mall_id, db)
