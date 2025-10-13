from collections.abc import Callable
from typing import Any

from pydantic import BaseModel


def get_getter(model_type: type[BaseModel], name: str) -> Callable[[Any], Any]:
    def getter(self: Any) -> Any:
        self._check_deleted()
        value = self._map[name]
        model = model_type.__pydantic_validator__.validate_assignment(model_type.model_construct(), name, value)
        return getattr(model, name)

    getter.__name__ = name
    return getter


def get_setter(model_type: type[BaseModel], name: str, func: Callable[[Any], Any] | None = None) -> Callable[[Any, Any], None]:
    def setter(self: Any, value: Any):
        self._check_deleted()
        model = model_type.__pydantic_validator__.validate_assignment(model_type.model_construct(), name, value)
        val = getattr(model, name)
        if func is not None:
            val = func(val)
        self._map[name] = val

    setter.__name__ = name
    return setter
