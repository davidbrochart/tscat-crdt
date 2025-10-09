from datetime import datetime
from typing import Any, cast
from uuid import UUID

from pycrdt import Array, Map

from .models import EventModel


class Event:
    def __init__(self, model: EventModel) -> None:
        self._map = Map(dict(
            uuid=str(model.uuid),
            start=str(model.start),
            stop=str(model.stop),
            author=model.author,
            tags=Array(model.tags),
            products=Array(model.products),
            rating=model.rating,
        ))

    @property
    def uuid(self) -> UUID:
        value = self._map["uuid"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "uuid", value))
        return model.uuid

    @property
    def author(self) -> str:
        value = self._map["author"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "author", value))
        return model.author

    @author.setter
    def author(self, value: Any) -> None:
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "author", value))
        self._map["author"] = str(model.author)

    @property
    def start(self) -> datetime:
        value = self._map["start"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "start", value))
        return model.start

    @start.setter
    def start(self, value: Any) -> None:
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "start", value))
        self._map["start"] = str(model.start)

    @property
    def stop(self) -> datetime:
        value = self._map["stop"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "stop", value))
        return model.stop

    @stop.setter
    def stop(self, value: Any) -> None:
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "stop", value))
        self._map["stop"] = str(model.stop)

    @property
    def tags(self) -> list[str]:
        value = self._map["tags"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "tags", value))
        return model.tags

    @tags.setter
    def tags(self, value: Any) -> None:
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "tags", value))
        with self._map.doc.transaction():
            tags = cast(Array, self._map["tags"])
            tags.extend(model.tags)

    @property
    def products(self) -> list[str]:
        value = self._map["products"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "products", value))
        return model.products

    @products.setter
    def products(self, value: Any) -> None:
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "products", value))
        with self._map.doc.transaction():
            products = cast(Array, self._map["products"])
            products.extend(model.products)

    @property
    def rating(self) -> int | None:
        value = self._map["rating"]
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "rating", value))
        return model.rating

    @rating.setter
    def rating(self, value: Any) -> None:
        model = cast(EventModel, EventModel.__pydantic_validator__.validate_assignment(EventModel.model_construct(), "rating", value))
        self._map["rating"] = model.rating
