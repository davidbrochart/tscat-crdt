from typing import Any, TYPE_CHECKING, cast
from uuid import UUID

from pycrdt import Array, Map

from .event import Event
from .models import CatalogueModel, EventModel

if TYPE_CHECKING:
    from .db import DB


class Catalogue:
    def __init__(self, model: CatalogueModel, db: "DB") -> None:
        self._db = db
        self._map = Map(dict(
            name=model.name,
            author=model.author,
            uuid=str(model.uuid),
            tags=Array(model.tags),
            events=Array(model.events),
        ))

    def add_event(self, event: Event) -> None:
        events = cast(Array, self._map["events"])
        events.append(event._map["uuid"])

    @property
    def uuid(self) -> UUID:
        value = self._map["uuid"]
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "uuid", value))
        return model.uuid

    @property
    def name(self) -> str:
        value = self._map["name"]
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "name", value))
        return model.name

    @name.setter
    def name(self, value: Any) -> None:
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "name", value))
        self._map["name"] = str(model.name)

    @property
    def author(self) -> str:
        value = self._map["author"]
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "author", value))
        return model.author

    @author.setter
    def author(self, value: Any) -> None:
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "author", value))
        self._map["author"] = str(model.author)

    @property
    def tags(self) -> list[str]:
        value = self._map["tags"]
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "tags", value))
        return model.tags

    @tags.setter
    def tags(self, value: Any) -> None:
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "tags", value))
        self._map["tags"] = model.tags

    @property
    def events(self) -> list[EventModel]:
        event_uuids = cast(Array, self._map["events"])
        value = [self._db._events[uuid].to_py() for uuid in event_uuids]
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "events", value))
        return model.events

    @events.setter
    def events(self, value: Any) -> None:
        model = cast(CatalogueModel, CatalogueModel.__pydantic_validator__.validate_assignment(CatalogueModel.model_construct(), "events", value))
        with self._map.doc.transaction():
            events = cast(Array, self._map["events"])
            events.clear()
            for event_model in model.events:
                event = self._db.create_event(event_model)
                self.add_event(event)
