from pydantic import AnyHttpUrl, BaseModel


class Cafe24AppExecutionLink(BaseModel):
    url: AnyHttpUrl
