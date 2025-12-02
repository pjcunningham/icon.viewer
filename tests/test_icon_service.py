from pathlib import Path
import io
import pytest
from PIL import Image

from icon_viewer.service import IconService


def make_sample_ico(tmp_path: Path, sizes=((16, 16), (32, 32), (48, 48), (64, 64))):
    # Create base image (largest) and let Pillow embed other sizes
    base_size = max(sizes, key=lambda s: s[0] * s[1])
    base_img = Image.new("RGBA", base_size, (255, 0, 0, 128))
    ico_path = tmp_path / "sample.ico"
    base_img.save(ico_path, format="ICO", sizes=list(sizes))
    return ico_path


def test_load_icon_extracts_all_sizes_sorted(tmp_path: Path):
    ico_path = make_sample_ico(tmp_path, sizes=((64, 64), (16, 16), (32, 32)))
    svc = IconService()

    images = svc.load_icon(str(ico_path))

    # Should be sorted from smallest to largest
    labels = [f"{im.width}x{im.height}" for im in images]
    assert labels == ["16x16", "32x32", "64x64"]

    # PNG bytes should be valid and each image should open
    for im in images:
        assert im.size_bytes == len(im.png_bytes) > 0
        with Image.open(io.BytesIO(im.png_bytes)) as opened:
            assert opened.size == (im.width, im.height)
            assert opened.mode in ("RGBA", "RGB", "P")


def test_non_ico_raises(tmp_path: Path):
    # Create a PNG file and ensure service rejects it
    png_path = tmp_path / "not_ico.png"
    Image.new("RGBA", (32, 32), (0, 255, 0, 255)).save(png_path, format="PNG")

    svc = IconService()
    with pytest.raises(ValueError):
        svc.load_icon(str(png_path))
