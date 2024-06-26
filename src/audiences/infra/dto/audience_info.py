from datetime import datetime

from pydantic import BaseModel


class AudienceInfo(BaseModel):
    audience_id: int
    audience_name: str
    audience_type_code: str
    audience_type_name: str
    audience_status_code: str
    audience_status_name: str
    is_exclude: bool
    user_exc_deletable: bool
    update_cycle: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime
    audience_count: int
    audience_unit_price: float
    main_product_id: int | None
    main_product_name: str | None

    @staticmethod
    def from_query(data) -> list["AudienceInfo"]:
        # 반환 타입 정의시 List[AudienceInfo]로 하면 에러 발생
        # 클래스 정의가 완료되기 전에 타입 힌트에서 해당 클래스를 참조할 때 발생할 수 있기 때문
        return [
            AudienceInfo(
                audience_id=row.audience_id,
                audience_name=row.audience_name,
                audience_type_code=row.audience_type_code,
                audience_type_name=row.audience_type_name,
                audience_status_code=row.audience_status_code,
                audience_status_name=row.audience_status_name,
                is_exclude=row.is_exclude,
                user_exc_deletable=row.user_exc_deletable,
                update_cycle=row.update_cycle,
                description=row.description,
                created_at=row.created_at,
                updated_at=row.updated_at,
                audience_count=row.audience_count,
                audience_unit_price=row.audience_unit_price,
                main_product_id=row.main_product_id,
                main_product_name=row.main_product_name,
            )
            for row in data
        ]
