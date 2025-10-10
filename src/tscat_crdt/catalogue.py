import sys
from dataclasses import dataclass
from json import dumps
from typing import Any, TYPE_CHECKING, cast
from uuid import UUID

from pycrdt import Array, Map

from .event import Event
from .models import CatalogueModel

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self

if TYPE_CHECKING:
    from .db import DB


@dataclass(eq=False)
class Catalogue:
    _map: Map
    _db: "DB"

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Catalogue):
            return NotImplemented

        return self._map["uuid"] == other._map["uuid"]

    def __repr__(self) -> str:
        return dumps(self._map.to_py())

    def __hash__(self) -> int:
        return hash(self._map["uuid"])

    @classmethod
    def new(cls, model: CatalogueModel, db: "DB") -> Self:
        map = Map(dict(
            name=model.name,
            author=model.author,
            uuid=str(model.uuid),
            tags=Array(model.tags),
            events=Array(model.events),
        ))
        return cls(map, db)

    @classmethod
    def from_map(cls, map: Map, db: "DB") -> Self:
        return cls(map, db)

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
    def events(self) -> set[Event]:
        event_uuids = cast(Array, self._map["events"])
        return {Event.from_map(self._db._events[uuid]) for uuid in event_uuids}

    @events.setter
    def events(self, value: set[Event]) -> None:
        with self._map.doc.transaction():
            events = cast(Array, self._map["events"])
            events.clear()
            for event in value:
                self.add_event(event)
