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

    @abstractmethod
    async def upload_for_carousel(
        self, file: UploadFile, set_group_msg_seq, user: User, db: Session
    ) -> str:
        pass
