from datetime import datetime

from pydantic import BaseModel

from src.audience.infra.entity.audience_entity import AudienceEntity
from src.audience.model.response.code_items import RepresentativeItems


class Audience(BaseModel):
    audience_id: str
    audience_name: str
    audience_status_code: str
    audience_status_name: str
    target_strategy: str
    is_exclude: bool
    create_type_code: str | None = None
    user_exc_deletable: bool | None = None
    update_cycle: str
    description: str | None = None
    audience_count: int | None = None
    audience_unit_price: float | None = None
    rep_list: list[RepresentativeItems] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def from_entity(entity: AudienceEntity) -> "Audience":
        return Audience(
            audience_id=entity.audience_id,
            audience_name=entity.audience_name,
            audience_status_code=entity.audience_status_code,
            audience_status_name=entity.audience_status_name,
            target_strategy=entity.target_strategy,
            is_exclude=entity.is_exclude,
            create_type_code=entity.create_type_code,
            user_exc_deletable=entity.user_exc_deletable,
            update_cycle=entity.update_cycle,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            # 추가 필드에 대한 초기값 설정
            audience_count=None,
            audience_unit_price=None,
            rep_list=None,
        )
