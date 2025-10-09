from pycrdt import Array, Map

from .models import EventModel


class Event:
    def __init__(self, model: EventModel) -> None:
        self._map = Map(dict(
            uuid=str(model.uuid),
            start=str(model.start),
            stop=str(model.stop),
            author=model.author,
            tags=Array(model.tags),
            products=Array(model.products),
            rating=model.rating,
        ))
