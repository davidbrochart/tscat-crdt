from json import loads

from tscat_crdt import DB, CatalogueModel, EventModel


def test_catalogue():
    db = DB()
    catalogue_model = CatalogueModel(
        name="cat0",
        author="John",
    )
    catalogue = db.create_catalogue(catalogue_model)
    event_model = EventModel(
        start="2025-01-31",
        stop="2026-01-31",
        author="John",
    )
    event0 = db.create_event(event_model)
    catalogue.add_event(event0)

    assert loads(repr(catalogue)) == {
        "uuid": str(catalogue_model.uuid),
        "events": [str(event_model.uuid)],
        "author": "John",
        "name": "cat0",
        "tags": [],
    }

    assert catalogue.uuid == catalogue_model.uuid

    assert catalogue.name == "cat0"
    catalogue.name = "cat1"
    assert catalogue.name == "cat1"

    assert catalogue.author == "John"
    catalogue.author = "Jeane"
    assert catalogue.author == "Jeane"

    assert catalogue.tags == []
    catalogue.tags = ["foo", "bar"]
    assert catalogue.tags == ["foo", "bar"]

    event1 = db.create_event(EventModel(
        start="2027-01-31",
        stop="2028-01-31",
        author="Jeane",
    ))
    assert catalogue.events == {event0}
    catalogue.events = {event1}
    assert catalogue.events == {event1}

    assert catalogue != 0

    values = []

    def callback(value):
        values.append(value)

    catalogue.on_change("name", callback)
    catalogue.name = "cat1"
    assert values == ["cat1"]

    values.clear()
    catalogue.on_change("author", callback)
    catalogue.author = "Mike"
    assert values == ["Mike"]

    values.clear()
    catalogue.on_change("events", callback)
    event2 = db.create_event(EventModel(
        start="2029-01-31",
        stop="2030-01-31",
        author="Mike",
    ))
    catalogue.events = {event0, event1, event2}
    assert catalogue.events == {event0, event1, event2}
    assert values == [{event0, event1, event2}]
