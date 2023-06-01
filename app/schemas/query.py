from pydantic import BaseModel


class QueryBase(BaseModel):
    query: str