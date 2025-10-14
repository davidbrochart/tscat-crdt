import sys
from collections.abc import Callable
from dataclasses import dataclass
from json import dumps
from typing import Any, TYPE_CHECKING, cast

from pycrdt import Map

from .event import Event
from .models import CatalogueModel
from .utils import get_getter, get_setter

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self

if TYPE_CHECKING:
    from .db import DB


@dataclass(eq=False)
class Catalogue:
    _uuid: str
    _map: Map
    _db: "DB"

    def _check_deleted(self):
        if self._uuid not in self._db._catalogue_maps:
            raise RuntimeError("Catalogue has been deleted")

    def __eq__(self, other: Any) -> bool:
        with self._map.doc.transaction():
            self._check_deleted()
            if not isinstance(other, Catalogue):
                return NotImplemented

            return self._uuid == other._uuid

    def __repr__(self) -> str:
        with self._map.doc.transaction():
            self._check_deleted()
            dct = self._map.to_py()
            assert dct is not None
            dct["events"] = [key for key, val in dct["events"].items() if val]
            return dumps(dct)

    def __hash__(self) -> int:
        with self._map.doc.transaction():
            self._check_deleted()
            return hash(self._uuid)

    @classmethod
    def new(cls, model: CatalogueModel, db: "DB") -> Self:
        uuid = str(model.uuid)
        map = Map(dict(
            uuid=uuid,
            name=model.name,
            author=model.author,
            tags=model.tags,
            events=Map(model.events),
        ))
        self = cls(uuid, map, db)
        db._catalogues[uuid] = self
        return self

    @classmethod
    def from_map(cls, map: Map, db: "DB") -> Self:
        uuid = map["uuid"]
        self = cls(uuid, map, db)
        db._catalogues[uuid] = self
        return self

    @classmethod
    def from_uuid(cls, uuid: str, db: "DB") -> Self:
        map = db._catalogue_maps[uuid]
        self = cls(uuid, map, db)
        db._catalogues[uuid] = self
        return self

    def on_change(self, name: str, callback: Callable[[Any], None]) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            self._db._catalogue_change_callbacks[self._uuid][name].append(callback)

    def on_delete(self, callback: Callable[[], None]) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            self._db._catalogue_delete_callbacks[self._uuid].append(callback)

    def on_add_events(self, callback: Callable[[list[Event]], None]) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            self._db._catalogue_change_callbacks[self._uuid]["added_events"].append(callback)

    def on_remove_events(self, callback: Callable[[list[Event]], None]) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            self._db._catalogue_change_callbacks[self._uuid]["removed_events"].append(callback)

    def add_event(self, event: Event) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            events = cast(Map, self._map["events"])
            events[event._uuid] = True

    def remove_event(self, event: Event) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            events = cast(Map, self._map["events"])
            del events[event._uuid]

    def delete(self):
        with self._map.doc.transaction():
            self._check_deleted()
            del self._db._catalogue_maps[self._uuid]

    @property
    def events(self) -> set[Event]:
        with self._map.doc.transaction():
            self._check_deleted()
            event_uuids = cast(Map, self._map["events"])
            return {Event.from_map(self._db._event_maps[uuid], self._db) for uuid, val in event_uuids.items() if val}

    @events.setter
    def events(self, value: set[Event]) -> None:
        with self._map.doc.transaction():
            self._check_deleted()
            events = cast(Map, self._map["events"])
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
