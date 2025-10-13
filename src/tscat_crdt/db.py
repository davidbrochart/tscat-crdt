from collections import defaultdict
from collections.abc import Callable, Iterable
from functools import partial
from typing import Any

from pycrdt import (
    Doc,
    Map,
    MapEvent,
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
    def __init__(self) -> None:
        self._doc: Doc = Doc()
        self._catalogue_maps = self._doc.get("catalogues", type=Map)
        self._event_maps = self._doc.get("events", type=Map)
        self._synced: list[DB] = []
        self._catalogue_maps.observe(self._catalogues_changed)
        self._catalogue_delete_callbacks: dict[str, list[Callable[[], None]]] = defaultdict(list)
        self._catalogue_create_callbacks: list[Callable[[Any], None]] = []
        self._catalogues: dict[str, Catalogue] = {}
        self._event_maps.observe(self._events_changed)
        self._event_delete_callbacks: dict[str, list[Callable[[], None]]] = defaultdict(list)
        self._event_create_callbacks: list[Callable[[Any], None]] = []
        self._events: dict[str, Event] = {}

    def _catalogues_changed(self, event: MapEvent) -> None:
        keys = event.keys  # type: ignore[attr-defined]
        for uuid in keys:
            action = keys[uuid]["action"]
            if action == "delete":
                if uuid in self._catalogues:
                    self._catalogues[uuid]._deleted = True
                for delete_callback in self._catalogue_delete_callbacks[uuid]:
                    delete_callback()
            elif action == "add":
                for create_callback in self._catalogue_create_callbacks:
                    create_callback(self.get_catalogue(uuid))

    def _events_changed(self, event: MapEvent) -> None:
        keys = event.keys  # type: ignore[attr-defined]
        for uuid in keys:
            action = keys[uuid]["action"]
            if action == "delete":
                if uuid in self._events:
                    self._events[uuid]._deleted = True
                for delete_callback in self._event_delete_callbacks[uuid]:
                    delete_callback()
            elif action == "add":
                for create_callback in self._event_create_callbacks:
                    create_callback(self.get_event(uuid))

    @property
    def catalogues(self) -> set[Catalogue]:
        return {Catalogue.from_map(catalogue, self) for uuid, catalogue in self._catalogue_maps.items()}

    @property
    def events(self) -> set[Event]:
        return {Event.from_map(event, self) for uuid, event in self._event_maps.items()}

    def create_catalogue(self, model: CatalogueModel, events: Iterable[Event] | Event | None = None) -> Catalogue:
        catalogue = Catalogue.new(model, self)
        with self._doc.transaction():
            self._catalogue_maps[str(model.uuid)] = catalogue._map
            if events is not None:
                if isinstance(events, Event):
                    events = [events]
                for event in events:
                   catalogue.add_event(event)
        return catalogue

    def create_event(self, model: EventModel) -> Event:
        event = Event.new(model, self)
        self._event_maps[str(model.uuid)] = event._map
        return event

    def on_create_catalogue(self, callback: Callable[[Any], None]) -> None:
        self._catalogue_create_callbacks.append(callback)

    def on_create_event(self, callback: Callable[[Any], None]) -> None:
        self._event_create_callbacks.append(callback)

    def get_catalogue(self, uuid: str) -> Catalogue:
        return Catalogue.from_uuid(uuid, self)

    def get_event(self, uuid: str) -> Event:
        return Event.from_uuid(uuid, self)

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
                if str(exc) not in ("Already mutably borrowed", "Already in a transaction"):  # pragma: nocover
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
