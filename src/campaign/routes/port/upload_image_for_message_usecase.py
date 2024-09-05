from abc import ABC, abstractmethod

from fastapi import UploadFile
from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.users.domain.user import User


class UploadImageForMessageUseCase(ABC):

    @transactional
    @abstractmethod
    async def exec(
        self, campaign_id, set_group_msg_seq, files: list[UploadFile], user: User, db: Session
    ) -> dict:
        pass
