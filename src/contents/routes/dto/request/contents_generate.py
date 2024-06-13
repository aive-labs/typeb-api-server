from typing import List

from pydantic import BaseModel, Field

from src.contents.routes.dto.request.contents_create import StyleObject


class ContentsGenerate(BaseModel):
    style_object: List[StyleObject] = Field(..., description="List of style objects")
    template: str = Field(..., description="Template code")
    subject: str = Field(..., description="Subject code")
    additional_prompt: str = Field(..., description="Additional prompt")
    emphasis_context: str = Field(..., description="Emphasis context")
