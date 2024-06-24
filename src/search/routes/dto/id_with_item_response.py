from typing import Optional, Union

from pydantic import BaseModel


class IdWithItem(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None
