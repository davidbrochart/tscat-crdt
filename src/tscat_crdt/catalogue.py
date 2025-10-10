import sys
from collections.abc import Callable
from dataclasses import dataclass
from json import dumps
from typing import Any, TYPE_CHECKING, cast

from pycrdt import Array, Map

from .event import Event
from .models import CatalogueModel
from .utils import Observable, get_getter, get_setter

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self

if TYPE_CHECKING:
    from .db import DB


@dataclass(eq=False)
class Catalogue(Observable):
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
            uuid=str(model.uuid),
            name=model.name,
            author=model.author,
            tags=model.tags,
            events=Array(model.events),
        ))
        return cls(map, db)

    @classmethod
    def from_map(cls, map: Map, db: "DB") -> Self:
        return cls(map, db)

    def on_change(self, name: str, callback: Callable[[Any], None]) -> None:
        self._observe(CatalogueModel, name, callback)

    def add_event(self, event: Event) -> None:
        events = cast(Array, self._map["events"])
        events.append(event._map["uuid"])

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


Catalogue.uuid = getter = property(get_getter(CatalogueModel, "uuid"))  # type: ignore[attr-defined]
Catalogue.name = getter = property(get_getter(CatalogueModel, "name"))  # type: ignore[attr-defined]
Catalogue.name = getter.setter(get_setter(CatalogueModel, "name"))  # type: ignore[attr-defined]
Catalogue.author = getter = property(get_getter(CatalogueModel, "author"))  # type: ignore[attr-defined]
Catalogue.author = getter.setter(get_setter(CatalogueModel, "author"))  # type: ignore[attr-defined]
Catalogue.tags = getter = property(get_getter(CatalogueModel, "tags"))  # type: ignore[attr-defined]
Catalogue.tags = getter.setter(get_setter(CatalogueModel, "tags"))  # type: ignore[attr-defined]
