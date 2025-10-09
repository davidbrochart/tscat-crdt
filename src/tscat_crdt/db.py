from functools import partial

from pycrdt import (
    Doc,
    Map,
    TransactionEvent,
    YMessageType,
    create_sync_message,
    create_update_message,
    handle_sync_message,
)

from .catalogue import Catalogue
from .event import Event
from .models import CatalogueModel, EventModel


class DB:
    def __init__(self):
        self._doc = Doc()
        self._catalogues = self._doc.get("catalogues", type=Map)
        self._events = self._doc.get("events", type=Map)
        self._synced = []

    @property
    def catalogues(self):
        return self._catalogues.to_py()

    @property
    def events(self):
        return self._events.to_py()

    def create_catalogue(self, model: CatalogueModel) -> Catalogue:
        catalogue = Catalogue(model)
        self._catalogues[str(model.uuid)] = catalogue._map
        return catalogue

    def create_event(self, model: EventModel) -> Event:
        event = Event(model)
        self._events[str(model.uuid)] = event._map
        return event

    def _handle_sync_message(self, message: bytes, db: "DB", init: bool = False) -> None:
        if init:
            _message = create_sync_message(self._doc)
            db._handle_sync_message(_message, self)

        message_type = message[0]
        if message_type == YMessageType.SYNC:
            try:
                reply = handle_sync_message(message[1:], self._doc)
                if reply is not None:
                    db._handle_sync_message(reply, self)
            except RuntimeError as exc:
                if str(exc) != "Already mutably borrowed":
                    raise

    def sync(self, db: "DB") -> None:
        if db in self._synced or self in db._synced:
            return

        self._synced.append(db)
        message = create_sync_message(self._doc)
        db._handle_sync_message(message, self, True)

        self._doc.observe(partial(send_update, db, self))
        db._doc.observe(partial(send_update, self, db))


def send_update(destination: DB, source: DB, event: TransactionEvent) -> None:
    message = create_update_message(event.update)
    destination._handle_sync_message(message, source)
