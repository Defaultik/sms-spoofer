import flet as ft

import api
import vonage_api
from theme import ACCENT, DANGER, AVATAR_BG, TEXT, TEXT_MUTED, SURFACE_2, SURFACE_3, BORDER, pad
from widgets import card, text_field


def build_contacts(app) -> ft.Control:
    page = app.page
    notify = app.notify
    describe_error = app.describe_error
    view_heading = app.view_heading

    name_f = text_field("Name", "John Doe", icon=ft.Icons.PERSON_ROUNDED, expand=1, autofocus=True)
    phone_f = text_field("Phone number", "+1001234567", icon=ft.Icons.PHONE_IPHONE_ROUNDED, expand=1)

    list_view = ft.ListView(spacing=6, expand=True)

    def render_contacts():
        list_view.controls.clear()
        contacts = api.load_contacts()
        if not contacts:
            list_view.controls.append(
                ft.Container(
                    ft.Text("No contacts yet — add your first one above.", color=TEXT_MUTED, size=13),
                    padding=pad(20, 0),
                    alignment=ft.Alignment.CENTER,
                )
            )
        for idx, c in enumerate(contacts):
            list_view.controls.append(contact_tile(idx, c))
        page.update()

    def contact_tile(idx: int, c: api.Contact) -> ft.Control:
        def do_delete(e):
            api.delete_contact(idx)
            render_contacts()

        tile = ft.Container(
            content=ft.Row(
                [
                    ft.CircleAvatar(content=ft.Text(c.name[:1].upper() or "?"), bgcolor=AVATAR_BG, color=ACCENT),
                    ft.Column(
                        [
                            ft.Text(c.name, color=TEXT, weight=ft.FontWeight.W_600, size=13),
                            ft.Text(c.phone_number, color=TEXT_MUTED, size=12),
                        ],
                        spacing=0,
                        expand=True,
                    ),
                    ft.IconButton(ft.Icons.DELETE_OUTLINE_ROUNDED, icon_color=DANGER, on_click=do_delete,
                                   tooltip="Remove contact"),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            bgcolor=SURFACE_2,
            border_radius=10,
            padding=pad(8, 14),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        )

        def on_hover(e):
            tile.bgcolor = SURFACE_3 if e.data else SURFACE_2
            tile.update()

        tile.on_hover = on_hover
        return tile

    add_btn = ft.IconButton(
        ft.Icons.PERSON_ADD_ROUNDED,
        icon_color="#FFFFFF",
        icon_size=16,
        bgcolor=AVATAR_BG,
        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
        tooltip="Add contact",
    )

    def do_add(e):
        phone_f.error = None
        if not name_f.value or not phone_f.value:
            notify("Enter both a name and a phone number.", ok=False)
            return

        add_btn.disabled = True
        page.update()

        def worker():
            try:
                try:
                    vonage_api.validate_number(phone_f.value)
                except vonage_api.NumberInvalidError:
                    phone_f.error = "Not a valid phone number"
                    phone_f.update()
                    notify("That doesn't look like a valid phone number.", ok=False)
                    return
                except vonage_api.NumberUnverifiableError as exc:
                    notify(f"Couldn't verify the number: {describe_error(exc)}", ok=False)
                    return

                api.add_contact(name_f.value, phone_f.value)
                name_f.value = ""
                phone_f.value = ""
                render_contacts()
                notify("Contact added.")
            finally:
                add_btn.disabled = False
                page.update()

        page.run_thread(worker)

    add_btn.on_click = do_add
    phone_f.on_submit = do_add

    render_contacts()

    return ft.Column(
        [
            view_heading("Contacts", "Saved recipients you can reuse from Multiple Send."),
            ft.Container(height=10),
            card(
                ft.Column(
                    [
                        ft.Row([name_f, phone_f, add_btn],
                                spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        ft.Divider(color=BORDER, height=1),
                        list_view,
                    ],
                    spacing=14,
                    expand=True,
                ),
                padding=pad(20, 20),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
