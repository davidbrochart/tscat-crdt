import sys
from collections.abc import Callable
from dataclasses import dataclass
from json import dumps
from typing import Any, TYPE_CHECKING

from pycrdt import Map

from .models import EventModel
from .utils import get_getter, get_setter

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self

if TYPE_CHECKING:
    from .db import DB


@dataclass(eq=False)
class Event:
    _map: Map
    _db: "DB"
    _deleted: bool = False

    def __eq__(self, other: Any) -> bool:
        self._check_deleted()
        if not isinstance(other, Event):
            return NotImplemented

        return self._map["uuid"] == other._map["uuid"]

    def __repr__(self) -> str:
        self._check_deleted()
        return dumps(self._map.to_py())

    def __hash__(self) -> int:
        self._check_deleted()
        return hash(self._map["uuid"])

    @classmethod
    def new(cls, model: EventModel, db: "DB") -> Self:
        uuid = str(model.uuid)
        map = Map(dict(
            uuid=uuid,
            start=str(model.start),
            stop=str(model.stop),
            author=model.author,
            tags=model.tags,
            products=model.products,
            rating=model.rating,
        ))
        self = cls(map, db)
        db._events[uuid] = self
        return self

    @classmethod
    def from_map(cls, map: Map, db: "DB") -> Self:
        self = cls(map, db)
        uuid = map["uuid"]
        db._events[uuid] = self
        return self

    @classmethod
    def from_uuid(cls, uuid: str, db: "DB") -> Self:
        map = db._event_maps[uuid]
        self = cls(map, db)
        db._events[uuid] = self
        return self

    def _check_deleted(self):
        if self._deleted:
            raise RuntimeError("Event has been deleted")

    def on_change(self, name: str, callback: Callable[[Any], None]) -> None:
        self._check_deleted()
        uuid = self._map["uuid"]
        self._db._event_change_callbacks[uuid][name].append(callback)

    def on_delete(self, callback: Callable[[], None]) -> None:
        self._check_deleted()
        uuid = self._map["uuid"]
        self._db._event_delete_callbacks[uuid].append(callback)

    def delete(self):
        self._check_deleted()
        del self._db._event_maps[self._map["uuid"]]



Event.uuid = getter = property(get_getter(EventModel, "uuid"))  # type: ignore[attr-defined]
Event.author = getter = property(get_getter(EventModel, "author"))  # type: ignore[attr-defined]
Event.author = getter.setter(get_setter(EventModel, "author"))  # type: ignore[attr-defined]
Event.start = getter = property(get_getter(EventModel, "start"))  # type: ignore[attr-defined]
Event.start = getter.setter(get_setter(EventModel, "start", str))  # type: ignore[attr-defined]
Event.stop = getter = property(get_getter(EventModel, "stop"))  # type: ignore[attr-defined]
Event.stop = getter.setter(get_setter(EventModel, "stop", str))  # type: ignore[attr-defined]
Event.tags = getter = property(get_getter(EventModel, "tags"))  # type: ignore[attr-defined]
Event.tags = getter.setter(get_setter(EventModel, "tags"))  # type: ignore[attr-defined]
Event.products = getter = property(get_getter(EventModel, "products"))  # type: ignore[attr-defined]
Event.products = getter.setter(get_setter(EventModel, "products"))  # type: ignore[attr-defined]
Event.rating = getter = property(get_getter(EventModel, "rating"))  # type: ignore[attr-defined]
Event.rating = getter.setter(get_setter(EventModel, "rating"))  # type: ignore[attr-defined]
