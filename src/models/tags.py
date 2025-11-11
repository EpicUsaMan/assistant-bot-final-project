from __future__ import annotations

from typing import Iterable, List

from src.utils.validators import is_valid_tag, normalize_tag

from .field import Field


class Tags(Field):
    """Domain field holding a normalized, unique list of tags (lowercase)."""

    def __init__(self, value: Iterable[str] | str | None = None) -> None:
        super().__init__([])
        self.value: List[str] = []
        if value:
            self.replace(value)

    def _normalize_many(self, tags: Iterable[str]) -> List[str]:
        out, seen = [], set()
        for t in tags:
            n = normalize_tag(t)
            if not n or n in seen:
                continue
            if not is_valid_tag(n):
                raise ValueError(f"Invalid tag: '{t}'")
            seen.add(n)
            out.append(n)
        return out

    # public API
    def replace(self, tags: Iterable[str]) -> None:
        self.value = self._normalize_many(tags)

    def add(self, tag: str) -> None:
        n = normalize_tag(tag)
        if not n or not is_valid_tag(n):
            raise ValueError(f"Invalid tag: '{tag}'")
        if n not in self.value:
            self.value.append(n)

    def remove(self, tag: str) -> None:
        n = normalize_tag(tag)
        if n in self.value:
            self.value.remove(n)

    def clear(self) -> None:
        self.value = []

    def as_list(self) -> List[str]:
        return list(self.value)
