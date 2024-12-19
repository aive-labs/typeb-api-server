from datetime import datetime

from pydantic import BaseModel


class AudienceInfo(BaseModel):
    audience_id: str
    audience_name: str
    audience_status_code: str
    audience_status_name: str
    target_strategy: str
    is_exclude: bool
    user_exc_deletable: bool | None
    update_cycle: str | None
    description: str | None
    created_at: datetime | None = None
    updated_at: datetime | None = None
    owned_by_dept: str | None
    audience_count: int
    audience_unit_price: float
    main_product_id: str | None
    main_product_name: str | None

    @staticmethod
    def from_query(data) -> list["AudienceInfo"]:
        # 반환 타입 정의시 List[AudienceInfo]로 하면 에러 발생
        # 클래스 정의가 완료되기 전에 타입 힌트에서 해당 클래스를 참조할 때 발생할 수 있기 때문
        return [
            AudienceInfo(
                audience_id=row.audience_id,
                audience_name=row.audience_name,
                audience_status_code=row.audience_status_code,
                audience_status_name=row.audience_status_name,
                target_strategy=row.target_strategy,
                is_exclude=row.is_exclude,
                user_exc_deletable=row.user_exc_deletable,
                update_cycle=row.update_cycle,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
                owned_by_dept=row.owned_by_dept,
                audience_count=row.audience_count,
                audience_unit_price=row.audience_unit_price,
                main_product_id=row.main_product_id,
                main_product_name=row.main_product_name,
            )
            for row in data
        ]
