from datetime import datetime
from json import loads

from tscat_crdt import DB, EventModel


def test_event():
    db = DB()
    event_model = EventModel(
        start="2025-01-31",
        stop="2026-01-31",
        author="John",
    )
    event = db.create_event(event_model)

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
