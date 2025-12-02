from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from typing import List, Dict, Tuple
from PIL import Image

from .models import IconImage


@dataclass
class IconService:
    """Service to load and parse Windows .ico files into individual images.

    Strategy for compatibility across Pillow versions:
    - Try to iterate frames via `n_frames` / `seek` to collect real frames and map by size.
    - Use `im.info.get("sizes")` if present to know target sizes embedded in the ICO.
    - If some sizes are missing as frames (common in some builds), synthesize them by
      resizing the largest available frame with high-quality resampling.
    """

    def load_icon(self, file_path: str) -> List[IconImage]:
        with Image.open(file_path) as im:
            if im.format != "ICO":
                raise ValueError("Provided file is not an ICO: " + file_path)

            # Collect actual frames if available
            frames_by_size: Dict[Tuple[int, int], Image.Image] = {}
            largest_frame: Image.Image | None = None

            try:
                frame_count = getattr(im, "n_frames", 1)
            except Exception:
                frame_count = 1

            for i in range(max(1, frame_count)):
                try:
                    im.seek(i)
                except EOFError:
                    break
                fr = im.copy().convert("RGBA")
                frames_by_size[fr.size] = fr
                if (largest_frame is None) or (fr.size[0] * fr.size[1] > largest_frame.size[0] * largest_frame.size[1]):
                    largest_frame = fr

            if largest_frame is None:
                # Fallback to current image
                largest_frame = im.copy().convert("RGBA")
                frames_by_size[largest_frame.size] = largest_frame

            # Determine target sizes: use ICO declared sizes if present; otherwise use collected sizes
            target_sizes = im.info.get("sizes") or list(frames_by_size.keys())
            # Deduplicate and sort ascending
            target_sizes = sorted(set(target_sizes), key=lambda s: (s[0] * s[1], s[0], s[1]))

            # Prepare PNG bytes per size, using real frame when available, otherwise resize largest
            images: List[IconImage] = []

            # Pillow 10+: Image.Resampling.LANCZOS; older: Image.LANCZOS
            try:
                resample = Image.Resampling.LANCZOS  # type: ignore[attr-defined]
            except Exception:
                resample = Image.LANCZOS  # type: ignore[attr-defined]

            for size in target_sizes:
                if size in frames_by_size:
                    out_img = frames_by_size[size]
                else:
                    # Synthesize from largest frame
                    out_img = largest_frame.resize(size, resample=resample)
                buf = BytesIO()
                out_img.save(buf, format="PNG")
                data = buf.getvalue()
                images.append(IconImage(width=size[0], height=size[1], size_bytes=len(data), png_bytes=data))

            # Ensure final sort from smallest to largest
            images.sort(key=lambda ii: (ii.width * ii.height, ii.width, ii.height))
            return images
