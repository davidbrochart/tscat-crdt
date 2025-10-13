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
    _deleted: bool = False

    def __eq__(self, other: Any) -> bool:
        self._check_deleted()
        if not isinstance(other, Catalogue):
            return NotImplemented

        return self._map["uuid"] == other._map["uuid"]

    def __repr__(self) -> str:
        self._check_deleted()
        return dumps(self._map.to_py())

    def __hash__(self) -> int:
        self._check_deleted()
        return hash(self._map["uuid"])

    @classmethod
    def new(cls, model: CatalogueModel, db: "DB") -> Self:
        uuid = str(model.uuid)
        map = Map(dict(
            uuid=uuid,
            name=model.name,
            author=model.author,
            tags=model.tags,
            events=Array(model.events),
        ))
        self = cls(map, db)
        db._catalogues[uuid] = self
        return self

    @classmethod
    def from_map(cls, map: Map, db: "DB") -> Self:
        self = cls(map, db)
        uuid = map["uuid"]
        db._catalogues[uuid] = self
        return self

    @classmethod
    def from_uuid(cls, uuid: str, db: "DB") -> Self:
        map = db._catalogue_maps[uuid]
        self = cls(map, db)
        db._catalogues[uuid] = self
        return self

    def _check_deleted(self):
        if self._deleted:
            raise RuntimeError("Catalogue has been deleted")

    def on_change(self, name: str, callback: Callable[[Any], None]) -> None:
        self._check_deleted()
        self._observe(CatalogueModel, name, callback)

    def on_delete(self, callback: Callable[[], None]) -> None:
        self._check_deleted()
        uuid = self._map["uuid"]
        self._db._catalogue_delete_callbacks[uuid].append(callback)

    def add_event(self, event: Event) -> None:
        self._check_deleted()
        events = cast(Array, self._map["events"])
        events.append(event._map["uuid"])

    def delete(self):
        self._check_deleted()
        del self._db._catalogue_maps[self._map["uuid"]]

    @property
    def events(self) -> set[Event]:
        self._check_deleted()
        event_uuids = cast(Array, self._map["events"])
        return {Event.from_map(self._db._event_maps[uuid], self._db) for uuid in event_uuids}

    @events.setter
    def events(self, value: set[Event]) -> None:
        self._check_deleted()
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
