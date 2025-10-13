from datetime import datetime
from json import loads

import pytest

from tscat_crdt import DB, EventModel


def test_event():
    db = DB()
    event_model = EventModel(
        start="2025-01-31",
        stop="2026-01-31",
        author="John",
    )

    event = None

    def create_event_callback(_event):
        nonlocal event
        event = _event

    db.on_create_event(create_event_callback)

    assert event == db.create_event(event_model)

    assert loads(repr(event)) == {
        "uuid": str(event_model.uuid),
        "author": "John",
        "products": [],
        "rating": None,
        "start": "2025-01-31 00:00:00",
        "stop": "2026-01-31 00:00:00",
        "tags": [],
    }

    assert event.uuid == event_model.uuid

    assert event.start == datetime(2025, 1, 31, 0, 0)
    event.start = "2025-01-30"
    assert event.start == datetime(2025, 1, 30, 0, 0)

    assert event.stop == datetime(2026, 1, 31, 0, 0)
    event.stop = "2026-01-30"
    assert event.stop == datetime(2026, 1, 30, 0, 0)

    assert event.author == "John"
    event.author = "Jeane"
    assert event.author == "Jeane"

    assert event.tags == []
    event.tags = ["foo", "bar"]
    assert event.tags == ["foo", "bar"]

    assert event.products == []
    event.products = ["a", "b"]
    assert event.products == ["a", "b"]

    assert event.rating is None
    event.rating = 2
    assert event.rating == 2

    assert event != 0

    values = []

    def callback(value):
        values.append(value)

    event.on_change("start", callback)
    event.start = "2025-01-29"
    event.stop = "2026-01-29"
    event.start = "2025-01-28"

    assert values == [datetime(2025, 1, 29, 0, 0), datetime(2025, 1, 28, 0, 0)]

    values.clear()
    event.on_change("stop", callback)
    event.stop = "2026-01-28"
    assert values == [datetime(2026, 1, 28, 0, 0)]

    values.clear()
    event.on_change("author", callback)
    event.author = "Mike"
    assert values == ["Mike"]

    values.clear()
    event.on_change("tags", callback)
    event.tags = ["baz"]
    assert values == [["baz"]]

    deleted = False

    def delete_callback():
        nonlocal deleted
        deleted = True

    event.on_delete(delete_callback)
    event.delete()

    assert deleted

    with pytest.raises(RuntimeError) as excinfo:
        event.author = "Paul"
    assert str(excinfo.value) == "Event has been deleted"
