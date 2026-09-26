import flet as ft

import api
import vonage_api
from theme import ACCENT, TEXT, TEXT_MUTED, SURFACE_2, SURFACE_3, pad
from widgets import card
from formatting import format_timestamp


def build_history(app) -> ft.Control:
    page = app.page
    notify = app.notify
    describe_error = app.describe_error
    view_heading = app.view_heading
    refresh_balance = app.refresh_balance

    list_view = ft.ListView(spacing=6, expand=True)

    def render_history():
        list_view.controls.clear()
        entries = api.load_history()
        if not entries:
            list_view.controls.append(
                ft.Container(
                    content=ft.Text(
                        "No messages sent yet.\nMessages you send will show up here.",
                        color=TEXT_MUTED, size=13, text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.Alignment.CENTER,
                    expand=True,
                    padding=pad(24, 12),
                )
            )
        else:
            for entry in entries:
                list_view.controls.append(history_tile(entry))
        page.update()

    def history_tile(entry: api.HistoryEntry) -> ft.Control:
        resend_btn = ft.IconButton(ft.Icons.REPLAY_ROUNDED, icon_color=ACCENT,
                                    tooltip="Send this message again")

        def do_resend(e):
            resend_btn.disabled = True
            resend_btn.update()

            def worker():
                try:
                    vonage_api.send_sms(entry.recipient, entry.sender_id, entry.text)
                    api.record_send(entry.recipient, entry.sender_id, entry.text)
                    notify("Message sent again.")
                    render_history()
                except Exception as exc:
                    notify(f"Send failed: {describe_error(exc)}", ok=False)
                    resend_btn.disabled = False
                    resend_btn.update()
                finally:
                    refresh_balance(delay=1)

            page.run_thread(worker)

        resend_btn.on_click = do_resend

        tile = ft.Container(
            content=ft.Row(
                [
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    ft.Icon(ft.Icons.BADGE_ROUNDED, size=14, color=ACCENT),
                                    ft.Text(entry.sender_id, color=TEXT,
                                            weight=ft.FontWeight.W_600, size=13),
                                    ft.Icon(ft.Icons.ARROW_RIGHT_ALT_ROUNDED, size=16, color=TEXT_MUTED),
                                    ft.Text(entry.recipient, color=TEXT_MUTED, size=12),
                                ],
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
                            ft.Text(entry.text, color=TEXT, size=12, max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS),
                            ft.Text(format_timestamp(entry.sent_at), color=TEXT_MUTED, size=11),
                        ],
                        spacing=4,
                        expand=True,
                    ),
                    resend_btn,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            bgcolor=SURFACE_2,
            border_radius=10,
            padding=pad(10, 14),
            animate=ft.Animation(120, ft.AnimationCurve.EASE_OUT),
        )

        def on_hover(e):
            tile.bgcolor = SURFACE_3 if e.data else SURFACE_2
            tile.update()

        tile.on_hover = on_hover
        return tile

    render_history()

    return ft.Column(
        [
            view_heading("History", "Messages you've sent, most recent first."),
            ft.Container(height=10),
            card(
                ft.Column([list_view], spacing=14, expand=True),
                padding=pad(20, 20),
                expand=True,
            ),
        ],
        spacing=0,
        expand=True,
    )
