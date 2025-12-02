from pathlib import Path
import io
from PIL import Image

from icon_viewer.controller import IconViewerController
from icon_viewer.service import IconService


def make_sample_ico(tmp_path: Path, sizes=((16, 16), (32, 32))):
    base_size = max(sizes, key=lambda s: s[0] * s[1])
    base_img = Image.new("RGBA", base_size, (0, 0, 255, 200))
    ico_path = tmp_path / "controller_sample.ico"
    base_img.save(ico_path, format="ICO", sizes=list(sizes))
    return ico_path


def test_controller_open_and_select(tmp_path: Path):
    ico_path = make_sample_ico(tmp_path)

    controller = IconViewerController(service=IconService())
    labels = controller.open_file(str(ico_path))

    # Labels are sorted from small to large, first selected
    assert labels == ["16x16", "32x32"]
    assert controller.get_selected_label() == "16x16"

    # Selecting second image updates selection and provides png bytes
    controller.select_index(1)
    assert controller.get_selected_label() == "32x32"
    data = controller.get_selected_png_bytes()
    assert isinstance(data, (bytes, bytearray)) and len(data) > 0

    # Out-of-range selection should raise
    try:
        controller.select_index(5)
        assert False, "Expected IndexError"
    except IndexError:
        pass
