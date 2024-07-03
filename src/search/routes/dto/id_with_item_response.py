from typing import Optional, Union

from pydantic import BaseModel


class IdWithItem(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None


class IdWithItemDescription(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None
    description: Optional[str] = None
