from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional

from .models import IconImage
from .service import IconService


@dataclass
class IconViewerController:
    service: IconService
    images: List[IconImage] = field(default_factory=list)
    selected_index: Optional[int] = None
    current_file: Optional[str] = None

    def open_file(self, file_path: str) -> List[str]:
        self.images = self.service.load_icon(file_path)
        self.current_file = file_path
        self.selected_index = 0 if self.images else None
        return self.get_labels()

    def get_labels(self) -> List[str]:
        return [img.label for img in self.images]

    def select_index(self, index: int) -> None:
        if not self.images:
            self.selected_index = None
            return
        if index < 0 or index >= len(self.images):
            raise IndexError("Selected index out of range")
        self.selected_index = index

    def get_selected(self) -> Optional[IconImage]:
        if self.selected_index is None:
            return None
        return self.images[self.selected_index]

    def get_selected_png_bytes(self) -> Optional[bytes]:
        sel = self.get_selected()
        return sel.png_bytes if sel else None

    def get_selected_label(self) -> Optional[str]:
        sel = self.get_selected()
        return sel.label if sel else None
