from pydantic import BaseModel


class ReviewerResponse(BaseModel):
    user_id: int
    user_name_object: str
    test_callback_number: str
    default_reviewer_yn: str
