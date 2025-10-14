from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventModel(BaseModel):
    uuid: UUID = Field(default_factory=lambda: uuid4())
    start: datetime
    stop: datetime
    author: str
    tags: list[str] = Field(default_factory=list)
    products: list[str] = Field(default_factory=list)
    rating: int | None = None


class CatalogueModel(BaseModel):
    uuid: UUID = Field(default_factory=lambda: uuid4())
    name: str
    author: str
    tags: list[str] = Field(default_factory=list)
    events: dict[str, bool] = Field(default_factory=dict)
