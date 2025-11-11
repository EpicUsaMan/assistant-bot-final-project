# src/models/group.py
import re
from dataclasses import dataclass

DEFAULT_GROUP_ID = "personal"
_GROUP_ID_RE = re.compile(r"^[a-z0-9_-]{1,32}$")


def normalize_group_id(group_id: str) -> str:
    gid = group_id.strip().lower()
    if not gid:
        raise ValueError("Group id cannot be empty.")
    if not _GROUP_ID_RE.match(gid):
        raise ValueError(
            "Invalid group id. Allowed: [a-z0-9_-], length 1..32."
        )
    return gid


@dataclass
class Group:
    """
    Contact group descriptor.

    Attributes:
        id: normalized group identifier (unique key)
        title: human-readable name (defaults to id)
    """
    id: str
    title: str | None = None

    def __post_init__(self) -> None:
        self.id = normalize_group_id(self.id)
        if self.title is None:
            self.title = self.id

    @property
    def display_name(self) -> str:
        return self.title or self.id