from typing import cast

from pycrdt import Array, Map

from .event import Event
from .models import CatalogueModel


class Catalogue:
    def __init__(self, model: CatalogueModel) -> None:
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
