import pytest

from src.models.tags import Tags
from src.utils.validators import is_valid_tag, normalize_tag, split_tags_string


def test_split_tags_string_basic():
    assert split_tags_string("ai, ML ,  python") == ["ai", "ML", "python"]
    assert split_tags_string("") == []


def test_normalize_and_validate_one():
    assert normalize_tag("  ML ") == "ml"
    assert is_valid_tag("ml") is True
    assert is_valid_tag("bad tag") is False  # space
    assert is_valid_tag("a" * 33) is False  # >32


def test_tags_init_and_replace():
    t = Tags(["AI", " ml ", "ai"])
    assert t.as_list() == ["ai", "ml"]  # lower + dedup

    t.replace(["python", "python"])
    assert t.as_list() == ["python"]


def test_tags_add_remove_clear():
    t = Tags()
    t.add("ML")
    t.add("ml")  # duplicate
    assert t.as_list() == ["ml"]

    t.remove("ML")
    assert t.as_list() == []

    t.add("ok_tag-1")
    t.clear()
    assert t.as_list() == []


def test_tags_reject_invalid():
    t = Tags()
    with pytest.raises(ValueError):
        t.add("bad tag")
    with pytest.raises(ValueError):
        t.add("a" * 33)
