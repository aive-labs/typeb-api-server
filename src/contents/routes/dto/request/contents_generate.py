from typing import List, Optional

from pydantic import BaseModel, Field

from src.contents.routes.dto.request.contents_create import ProductObject


class ContentsGenerate(BaseModel):
    product_object: Optional[List[ProductObject]] = Field(
        default=[], description="List of product objects"
    )
    template: str = Field(..., description="Template code")
    subject: str = Field(..., description="Subject code")
    additional_prompt: str = Field(default="", description="Additional prompt")
    emphasis_context: str = Field(default="", description="Emphasis context")
