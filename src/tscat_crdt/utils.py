from collections.abc import Callable
from functools import partial
from typing import Any

from pycrdt import Map, MapEvent, Subscription
from pydantic import BaseModel


def get_getter(model_type: type[BaseModel], name: str) -> Callable[[Any], Any]:
    def getter(self: Any) -> Any:
        value = self._map[name]
        model = model_type.__pydantic_validator__.validate_assignment(model_type.model_construct(), name, value)
        return getattr(model, name)

    getter.__name__ = name
    return getter


def get_setter(model_type: type[BaseModel], name: str, func: Callable[[Any], Any] | None = None) -> Callable[[Any, Any], None]:
    def setter(self: Any, value: Any):
        model = model_type.__pydantic_validator__.validate_assignment(model_type.model_construct(), name, value)
        val = getattr(model, name)
        if func is not None:
            val = func(val)
        self._map[name] = val

    setter.__name__ = name
    return setter


class Observable:
    _map: Map
    _subscription: Subscription | None = None
    _observed_keys: dict[str, list[Callable[[MapEvent], None]]] | None = None

    def _observe(self, model_type: type[BaseModel], key: str, callback) -> None:
        if self._subscription is None:
            self._observed_keys = {}
            self._subscription = self._map.observe_deep(partial(self._callback, model_type))
        assert self._observed_keys is not None
        if key not in self._observed_keys:
            self._observed_keys[key] = []
        self._observed_keys[key].append(callback)

    def _callback(self, model_type: type[BaseModel], events: list[MapEvent]) -> None:
        assert self._observed_keys is not None
        for event in events:
            if isinstance(event, MapEvent):
                changed_keys = event.keys  # type: ignore[attr-defined]
                for key in changed_keys:
                    if key in self._observed_keys:
                        callbacks = self._observed_keys[key]
                        for callback in callbacks:
                            value = changed_keys[key]["newValue"]
                            model = model_type.__pydantic_validator__.validate_assignment(model_type.model_construct(), key, value)
                            callback(getattr(model, key))
            else:  # ArrayEvent
                if "events" in self._observed_keys:
                    i = 0
                    uuids = []
                    for action in event.delta:
                        if "delete" in action:  # FIXME: handle removed events
                            i += action["delete"]
                        elif "insert" in action:
                            uuids.extend(action["insert"])
                            i += len(uuids)
                    if uuids:
                        from .event import Event

                        result = {Event.from_map(self._db._events[uuid]) for uuid in uuids}
                        callbacks = self._observed_keys["events"]
                        for callback in callbacks:
                            callback(result)
