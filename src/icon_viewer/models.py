from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class IconImage:
    """Represents a single embedded image from a .ico file."""
    width: int
    height: int
    size_bytes: int
    png_bytes: bytes

    @property
    def size(self) -> Tuple[int, int]:
        return (self.width, self.height)

    @property
    def label(self) -> str:
        return f"{self.width}x{self.height}"
