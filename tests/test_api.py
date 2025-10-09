from tscat_crdt import DB, CatalogueModel, EventModel


def test_create_catalogue():
    db0 = DB()

    model0 = CatalogueModel(
        name="cat0",
        author="John",
    )
    db0.create_catalogue(model0)

    assert db0.catalogues == {
        str(model0.uuid): {
            "uuid": str(model0.uuid),
            "name": "cat0",
            "author": "John",
            "tags" : [],
            "events": [],
        },
    }

    db1 = DB()
    db1.sync(db0)
    assert db0.catalogues == db1.catalogues

    model1 = CatalogueModel(
        name="cat1",
        author="Jeane",
    )
    db1.create_catalogue(model1)

    assert len(db1.catalogues) == 2
    assert (
        str(model0.uuid),
        {
            "uuid": str(model0.uuid),
            "name": "cat0",
            "author": "John",
            "tags" : [],
            "events": [],
        }
    ) in db1.catalogues.items()
    assert (
        str(model1.uuid),
        {
            "uuid": str(model1.uuid),
            "name": "cat1",
            "author": "Jeane",
            "tags" : [],
            "events": [],
        },
    ) in db1.catalogues.items()

    assert db0.catalogues == db1.catalogues


def test_create_event():
    db0 = DB()
    model0 = EventModel(
        start="2025-01-31",
        stop="2026-01-31",
        author="John",
    )
    db0.create_event(model0)
    assert db0.events == {
        str(model0.uuid): {
            "author": "John",
            "products": [],
            "rating": None,
            "start": "2025-01-31 00:00:00",
            "stop": "2026-01-31 00:00:00",
            "tags": [],
            "uuid": str(model0.uuid),
        }
    }

    db1 = DB()
    db1.sync(db0)
    assert db0.events == db1.events

    model1 = EventModel(
        start="2027-01-31",
        stop="2028-01-31",
        author="Jeane",
    )
    db1.create_event(model1)

    assert len(db1.events) == 2
    assert (
        str(model1.uuid),
        {
            "author": "Jeane",
            "products": [],
            "rating": None,
            "start": "2027-01-31 00:00:00",
            "stop": "2028-01-31 00:00:00",
            "tags": [],
            "uuid": str(model1.uuid),
        }
    ) in db1.events.items()
    assert (
        str(model0.uuid),
        {
            "author": "John",
            "products": [],
            "rating": None,
            "start": "2025-01-31 00:00:00",
            "stop": "2026-01-31 00:00:00",
            "tags": [],
            "uuid": str(model0.uuid),
        }
    ) in db1.events.items()
    assert db0.events == db1.events


def test_add_event():
    db0 = DB()
    db1 = DB()
    db0.sync(db1)
    catalogue_model = CatalogueModel(
        name="cat",
        author="John",
    )
    catalogue = db0.create_catalogue(catalogue_model)
    event_model = EventModel(
        start="2025-01-31",
        stop="2026-01-31",
        author="John",
    )
    event = db0.create_event(event_model)
    catalogue.add_event(event)

    assert db1.catalogues == {
        str(catalogue_model.uuid): {
            "author": "John",
            "name": "cat",
            "tags": [],
            "uuid": str(catalogue_model.uuid),
            "events": [str(event_model.uuid)],
        }
    }
    assert db1.events == {
        str(event_model.uuid): {
            "author": "John",
            "products": [],
            "rating": None,
            "start": "2025-01-31 00:00:00",
            "stop": "2026-01-31 00:00:00",
            "tags": [],
            "uuid": str(event_model.uuid),
        }
    }


def test_sync():
    db0 = DB()
    db1 = DB()
    db0.sync(db1)
    db1.sync(db0)
