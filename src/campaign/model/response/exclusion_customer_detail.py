from pydantic import BaseModel


class ExcludeCustomerDetailStats(BaseModel):
    div: str  ## 컬럼명: 제외 구분
    id: str  ## 컬럼명: ID
    name: str  ## 컬럼명: 제외 그룹명
    count: int  ## 컬럼명: 제외 고객수(명)


class ExcludeCustomerDetail(BaseModel):
    excl_message: str
    excl_detail_stats: list[ExcludeCustomerDetailStats]
