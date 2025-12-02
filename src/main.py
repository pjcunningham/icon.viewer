import base64
import flet as ft
from typing import Optional

from icon_viewer import IconService, IconViewerController


def main(page: ft.Page):
    page.title = "Icon Viewer"
    page.window_width = 900
    page.window_height = 600
    page.padding = 0

    service = IconService()
    controller = IconViewerController(service=service)

    # Left pane: list of sizes
    list_view = ft.ListView(expand=True, spacing=2, auto_scroll=False)

    # Right pane: image view inside a file drop target
    image = ft.Image(expand=True, fit=ft.ImageFit.CONTAIN)

    status_text = ft.Text("Drop a .ico file here or use Open...", size=12, color=ft.Colors.ON_SURFACE_VARIANT)

    def update_image_from_selection():
        data = controller.get_selected_png_bytes()
        if data:
            image.src_base64 = base64.b64encode(data).decode("ascii")
            status_text.value = controller.get_selected_label() or ""
        else:
            image.src_base64 = None
            status_text.value = "Drop a .ico file here or use Open..."
        image.update()
        status_text.update()

    def rebuild_list():
        list_view.controls.clear()
        for idx, label in enumerate(controller.get_labels()):
            def on_tap_factory(i: int):
                def _tap(_: ft.ControlEvent):
                    controller.select_index(i)
                    update_image_from_selection()
                return _tap

            tile = ft.ListTile(
                title=ft.Text(label),
                on_click=on_tap_factory(idx),
                selected=(idx == (controller.selected_index or -1)),
                dense=True,
            )
            list_view.controls.append(tile)
        list_view.update()

    def open_icon(file_path: str):
        try:
            controller.open_file(file_path)
        except Exception as ex:
            page.snack_bar = ft.SnackBar(ft.Text(f"Failed to open icon: {ex}"))
            page.snack_bar.open = True
            page.update()
            return
        rebuild_list()
        update_image_from_selection()

    # File picker (Open...)
    file_picker = ft.FilePicker(on_result=lambda e: (e.files and open_icon(e.files[0].path)))
    page.overlay.append(file_picker)

    open_btn = ft.IconButton(icon=ft.Icons.FOLDER_OPEN, tooltip="Open .ico", on_click=lambda e: file_picker.pick_files(allow_multiple=False, allowed_extensions=["ico"]))

    # Drag & Drop target for OS files (use page-level on_drop in Flet 0.28.3)
    def on_drop(e):
        if getattr(e, "files", None):
            # Pick the first .ico file among dropped
            for f in e.files:
                if getattr(f, "path", "").lower().endswith(".ico"):
                    open_icon(f.path)
                    break

    # Build right-side content (no FileDropTarget available in this Flet version)
    right_content = ft.Container(
        content=ft.Column([
            ft.Container(open_btn, alignment=ft.alignment.top_right),
            ft.Container(image, expand=True),
            ft.Container(status_text, padding=10),
        ], expand=True),
        expand=True,
    )

    # Register page-level file drop handler
    page.on_drop = on_drop

    # Layout: left list (fixed width), right takes remaining
    left_pane = ft.Container(
        content=ft.Column([
            ft.Text("Sizes", weight=ft.FontWeight.BOLD),
            ft.Divider(height=1),
            list_view,
        ], expand=True, spacing=5, scroll=ft.ScrollMode.ALWAYS),
        width=180,
        padding=10,
    )

    right_pane = ft.Container(content=right_content, expand=True, padding=10)

    page.add(
        ft.SafeArea(
            ft.Row([
                left_pane,
                ft.VerticalDivider(width=1),
                right_pane,
            ], expand=True),
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
