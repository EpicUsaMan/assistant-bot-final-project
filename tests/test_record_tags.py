import pytest

from src.models.record import Record


def test_record_tags_crud():
    r = Record("John Doe")
    assert r.tags_list() == []

    # add
    r.add_tag("ML")
    r.add_tag("ml")
    assert r.tags_list() == ["ml"]

    # remove
    r.remove_tag("ML")
    assert r.tags_list() == []

    # set_tags
    r.set_tags("ai, python")
    assert r.tags_list() == ["ai", "python"]

    # clear
    r.clear_tags()
    assert r.tags_list() == []


def test_record_tags_validation():
    r = Record("John Doe")
    with pytest.raises(ValueError):
        r.add_tag("bad tag")
    with pytest.raises(ValueError):
        r.add_tag("a" * 33)
