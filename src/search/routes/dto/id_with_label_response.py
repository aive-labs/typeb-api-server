from typing import Optional, Union

from pydantic import BaseModel


class IdWithLabel(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None
    label: Optional[str] = None
