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
    # Hide the image by default to avoid Flet showing the placeholder message
    image = ft.Image(expand=True, fit=ft.ImageFit.CONTAIN, visible=False)

    status_text = ft.Text("Drop a .ico file here or use Open...", size=12, color=ft.Colors.ON_SURFACE_VARIANT, text_align=ft.TextAlign.CENTER)

    def update_image_from_selection():
        data = controller.get_selected_png_bytes()
        if data:
            image.src_base64 = base64.b64encode(data).decode("ascii")
            image.visible = True
            status_text.visible = False
        else:
            image.src_base64 = None
            image.visible = False
            status_text.value = "Drop a .ico file here or use Open..."
            status_text.visible = True
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

    # Drag & Drop target for OS files — use FileDropTarget in Flet 0.28.3
    def on_drop(e):
        if getattr(e, "files", None):
            for f in e.files:
                if getattr(f, "path", "").lower().endswith(".ico"):
                    open_icon(f.path)
                    break

    def on_drag_enter(e):
        status_text.value = "Release to open .ico file..."
        status_text.visible = True
        image.visible = False
        status_text.update()
        image.update()

    def on_drag_leave(e):
        update_image_from_selection()

    # Build right-side content wrapped into a FileDropTarget
    right_content = ft.Container(
        content=ft.Column([
            ft.Container(open_btn, alignment=ft.alignment.top_right),
            ft.Container(
                content=ft.Stack(
                    controls=[
                        ft.Container(image, alignment=ft.alignment.center),
                        ft.Container(status_text, alignment=ft.alignment.center, padding=10),
                    ],
                    expand=True,
                    alignment=ft.alignment.center,
                ),
                expand=True,
            ),
        ], expand=True),
        expand=True,
    )

    # Use control-level FileDropTarget if available in this Flet version; otherwise fall back to page-level handlers
    if hasattr(ft, "FileDropTarget"):
        right_content = ft.FileDropTarget(
            content=right_content,
            on_drop=on_drop,
            on_drag_enter=on_drag_enter,
            on_drag_leave=on_drag_leave,
        )
        # Clear page-level handlers to avoid duplicate events
        try:
            page.on_drop = None
            # Not all versions support these, so guard with try/except
            page.on_drag_enter = None  # type: ignore[attr-defined]
            page.on_drag_leave = None  # type: ignore[attr-defined]
        except Exception:
            pass
    else:
        # Fallback: register page-level handlers
        page.on_drop = on_drop
        try:
            page.on_drag_enter = on_drag_enter  # type: ignore[attr-defined]
            page.on_drag_leave = on_drag_leave  # type: ignore[attr-defined]
        except Exception:
            # Older Flet might not support drag enter/leave on page; ignore
            pass

    # Layout: left list (fixed width), right takes remaining
    left_pane = ft.Container(
        content=ft.Column([
            ft.Text("Sizes", weight=ft.FontWeight.BOLD),
            ft.Divider(height=1),
            list_view,
        ], expand=True, spacing=5, scroll=ft.ScrollMode.ALWAYS, alignment=ft.MainAxisAlignment.START),
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
            ], expand=True, vertical_alignment=ft.CrossAxisAlignment.START),
            expand=True,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)
