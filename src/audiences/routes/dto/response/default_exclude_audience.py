from typing import Optional, Union

from pydantic import BaseModel


class DefaultExcludeAudience(BaseModel):
    id: Optional[Union[str, int]] = None
    name: Optional[str] = None
    user_exc_deletable: Optional[bool] = None
