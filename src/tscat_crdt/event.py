import sys
from collections.abc import Callable
from dataclasses import dataclass
from json import dumps
from typing import Any

from pycrdt import Map

from .models import EventModel
from .utils import Observable, get_getter, get_setter

if sys.version_info >= (3, 11):
    from typing import Self
else:  # pragma: nocover
    from typing_extensions import Self


@dataclass(eq=False)
class Event(Observable):
    _map: Map

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Event):
            return NotImplemented

        return self._map["uuid"] == other._map["uuid"]

    def __repr__(self) -> str:
        return dumps(self._map.to_py())

    def __hash__(self) -> int:
        return hash(self._map["uuid"])

    @classmethod
    def new(cls, model: EventModel) -> Self:
        map = Map(dict(
            uuid=str(model.uuid),
            start=str(model.start),
            stop=str(model.stop),
            author=model.author,
            tags=model.tags,
            products=model.products,
            rating=model.rating,
        ))
        return cls(map)

    @classmethod
    def from_map(cls, map: Map) -> Self:
        return cls(map)

    def on_change(self, name: str, callback: Callable[[Any], None]) -> None:
        self._observe(EventModel, name, callback)


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
