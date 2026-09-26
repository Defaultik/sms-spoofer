import time

import flet as ft

import api
import vonage_api
from theme import (
    BG, SURFACE, SURFACE_2, BORDER, ACCENT, TEXT, TEXT_MUTED,
    SUCCESS, WARNING, DANGER, VERSION_LABEL, pad,
)
from widgets import card, section_title, text_field, primary_button, set_button_loading
from formatting import read_version
from views import single_send, multi_send, contacts, history, settings


class SmsSpooferApp:
    def __init__(self, page: ft.Page) -> None:
        self.page = page
        self.balance_controls: dict[str, ft.Control | str | None] = {
            "text": None, "button": None, "value": "···"
        }

        self._configure_page()

        self.version = read_version()
        self.update_icon = ft.Icon(ft.Icons.CIRCLE, size=13, visible=False)

        self.content = ft.AnimatedSwitcher(
            content=ft.Container(),
            transition=ft.AnimatedSwitcherTransition.FADE,
            duration=220,
            switch_in_curve=ft.AnimationCurve.EASE_OUT,
            switch_out_curve=ft.AnimationCurve.EASE_IN,
            expand=True,
        )

        self.views = [
            ("Single Send", ft.Icons.SEND_ROUNDED, single_send.build_single_send),
            ("Multiple Send", ft.Icons.SEND_AND_ARCHIVE_ROUNDED, multi_send.build_multi_send),
            ("Contacts", ft.Icons.CONTACTS_ROUNDED, contacts.build_contacts),
            ("History", ft.Icons.HISTORY_ROUNDED, history.build_history),
            ("Settings", ft.Icons.SETTINGS_ROUNDED, settings.build_settings),
        ]

        self.app_shell = self._build_shell()

    def _configure_page(self) -> None:
        page = self.page
        page.title = "SMS Spoofer - github.com/Defaultik"
        page.window.icon = "icon.ico"
        page.bgcolor = BG
        page.padding = 0
        page.theme_mode = ft.ThemeMode.DARK
        page.theme = ft.Theme(color_scheme_seed=ACCENT, use_material3=True)
        page.window.bgcolor = BG
        page.window.visible = False

    def _size_window(self, width: int, height: int, min_width: int, min_height: int) -> None:
        self.page.window.width = width
        self.page.window.height = height
        self.page.window.min_width = min_width
        self.page.window.min_height = min_height
        self.page.run_task(self.page.window.center)

    def _set_app_window(self) -> None:
        self._size_window(980, 660, 880, 600)

    def _set_onboarding_window(self) -> None:
        self._size_window(480, 460, 480, 460)

    # Notifications
    def notify(self, message: str, ok: bool = True) -> None:
        self.page.show_dialog(
            ft.SnackBar(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED if ok else ft.Icons.ERROR_ROUNDED,
                                 color=SUCCESS if ok else DANGER, size=18),
                        ft.Text(message, color=TEXT),
                    ],
                    spacing=10,
                ),
                bgcolor=SURFACE_2,
                duration=3200,
            )
        )

    def describe_error(self, exc: Exception) -> str:
        return str(exc) or exc.__class__.__name__

    def validated_credentials(
        self, key_field: ft.TextField, secret_field: ft.TextField
    ) -> tuple[str, str] | None:
        key_field.error = None
        secret_field.error = None

        key = (key_field.value or "").strip()
        secret = (secret_field.value or "").strip()

        if not key or not secret:
            self.notify("API key and secret can't be empty.", ok=False)
            return None

        if not vonage_api.is_valid_api_key(key):
            key_field.error = "Should be an 8-character key (0-9, a-f)"
            key_field.update()
            self.notify("That doesn't look like a valid Vonage API key.", ok=False)
            return None

        if not vonage_api.is_valid_api_secret(secret):
            secret_field.error = "That looks too short for a Vonage API secret"
            secret_field.update()
            self.notify("That doesn't look like a valid Vonage API secret.", ok=False)
            return None

        return key, secret

    # Balance
    def refresh_balance(self, e=None, delay: float = 0) -> None:
        text = self.balance_controls["text"]
        button = self.balance_controls["button"]
        if text is None or button is None:
            return

        button.icon = ft.ProgressRing(width=16, height=16, stroke_width=2, color=TEXT_MUTED)
        self.page.update()

        def worker():
            if delay:
                time.sleep(delay)  # let Vonage settle the charge before re-reading
            try:
                value = vonage_api.get_balance()
                display = f"{value:.2f} EUR"
            except Exception:
                display = "— EUR"

            self.balance_controls["value"] = display
            text.value = display
            button.icon = ft.Icons.REFRESH_ROUNDED
            self.page.update()

        self.page.run_thread(worker)

    def _build_balance_row(self) -> ft.Row:
        text = ft.Text(self.balance_controls["value"], size=13, weight=ft.FontWeight.W_600, color=TEXT)
        refresh_btn = ft.IconButton(ft.Icons.REFRESH_ROUNDED, icon_size=16, icon_color=TEXT_MUTED,
                                     on_click=self.refresh_balance, tooltip="Refresh balance")
        self.balance_controls["text"] = text
        self.balance_controls["button"] = refresh_btn
        return ft.Row(
            [
                ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=16, color=ACCENT),
                text,
                refresh_btn,
            ],
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            tight=True,
        )

    def view_heading(self, title: str, subtitle: str = "") -> ft.Control:
        return ft.Row(
            [section_title(title, subtitle), self._build_balance_row()],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    # Navigation
    def show_view(self, index: int) -> None:
        builder = self.views[index][2]
        self.content.content = ft.Container(
            builder(self),
            padding=ft.Padding(left=24, top=24, right=24, bottom=32),
            expand=True,
        )
        self.page.update()

    # Update check
    def _apply_update_status(self, latest: str | None) -> None:
        if not latest:
            return
        if api.is_outdated(self.version, latest):
            self.update_icon.icon = ft.Icons.ARROW_CIRCLE_UP_ROUNDED
            self.update_icon.color = WARNING
            self.update_icon.tooltip = (
                f"Version v{latest} is available\n"
                "   Update with git pull"
            )
        else:
            self.update_icon.icon = ft.Icons.CHECK_CIRCLE_ROUNDED
            self.update_icon.color = SUCCESS
            self.update_icon.tooltip = "You're on the latest version."
        self.update_icon.visible = True
        self.page.update()

    def start_update_check(self) -> None:
        if not self.version:
            return

        self.page.run_thread(lambda: self._apply_update_status(api.fetch_latest_version()))

    def _build_shell(self) -> ft.Row:
        rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=88,
            min_extended_width=180,
            bgcolor=SURFACE,
            indicator_color=ft.Colors.with_opacity(0.16, ACCENT),
            expand=True,
            destinations=[
                ft.NavigationRailDestination(icon=icon, selected_icon=icon, label=label)
                for label, icon, _ in self.views
            ],
            on_change=lambda e: self.show_view(e.control.selected_index),
        )

        rail_children = [rail]
        if self.version:
            rail_children.append(
                ft.Container(
                    content=ft.Row(
                        [self.update_icon, ft.Text(f"v{self.version}", size=11, color=VERSION_LABEL)],
                        spacing=5,
                        alignment=ft.MainAxisAlignment.CENTER,
                        tight=True,
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=ft.Padding(left=0, right=0, top=8, bottom=16),
                )
            )
        rail_pane = ft.Container(
            content=ft.Column(rail_children, spacing=0, expand=True,
                              horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=SURFACE,
        )

        return ft.Row(
            [rail_pane, ft.VerticalDivider(width=1, color=BORDER), self.content],
            spacing=0,
            expand=True,
        )

    # Login Panel
    def show_onboarding(self) -> None:
        key_f = text_field("Vonage API key", icon=ft.Icons.KEY_ROUNDED, autofocus=True)
        secret_f = text_field("Vonage API secret", icon=ft.Icons.LOCK_ROUNDED, password=True)
        start_btn = primary_button("Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)

        def do_start(e):
            creds = self.validated_credentials(key_f, secret_f)
            if creds is None:
                return
            key, secret = creds

            set_button_loading(start_btn, True, "Verifying…")
            self.page.update()

            def worker():
                try:
                    vonage_api.verify_credentials(key, secret)
                except vonage_api.CredentialsInvalidError:
                    secret_f.error = "No Vonage account found for this key and secret"
                    secret_f.update()
                    self.notify("Vonage rejected those credentials — no such account.", ok=False)
                    set_button_loading(start_btn, False, "Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)
                    self.page.update()
                except vonage_api.CredentialsUnverifiableError as exc:
                    self.notify(f"Couldn't reach Vonage to verify credentials: {self.describe_error(exc)}", ok=False)
                    set_button_loading(start_btn, False, "Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)
                    self.page.update()
                else:
                    api.save_credentials(key, secret)
                    self._set_app_window()
                    self.page.controls.clear()
                    self.page.add(self.app_shell)
                    self.show_view(0)
                    self.refresh_balance()
                    self.start_update_check()

            self.page.run_thread(worker)

        start_btn.on_click = do_start
        secret_f.on_submit = do_start

        footer = ft.Text(
            spans=[
                ft.TextSpan("made by ", ft.TextStyle(color=TEXT_MUTED, size=12)),
                ft.TextSpan(
                    "github.com/Defaultik",
                    ft.TextStyle(color=TEXT_MUTED, size=12),
                    url="https://github.com/Defaultik",
                ),
            ],
            text_align=ft.TextAlign.CENTER,
        )

        self._set_onboarding_window()
        self.page.controls.clear()
        self.page.add(
            ft.Column(
                [
                    ft.Container(
                        content=card(
                            ft.Column(
                                [
                                    ft.Container(
                                        content=ft.Icon(ft.Icons.SMS_ROUNDED, color=ACCENT, size=36),
                                        alignment=ft.Alignment.CENTER_LEFT,
                                    ),
                                    ft.Column(
                                        [
                                            ft.Text("Welcome to SMS Spoofer", size=22,
                                                     weight=ft.FontWeight.W_600, color=TEXT),
                                            ft.Text("Enter your Vonage API credentials to get started.",
                                                     size=13, color=TEXT_MUTED),
                                        ],
                                        spacing=4,
                                        tight=True,
                                    ),
                                    ft.Column([key_f, secret_f], spacing=8, tight=True,
                                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH),
                                    start_btn,
                                ],
                                spacing=14,
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                            ),
                            width=420,
                        ),
                        alignment=ft.Alignment.CENTER,
                        padding=pad(32, 0),
                        expand=True,
                    ),
                    ft.Container(content=footer, alignment=ft.Alignment.CENTER, padding=pad(0, 0)),
                    ft.Container(height=16),
                ],
                spacing=0,
                expand=True,
            )
        )
        self.page.update()

    async def _reveal(self) -> None:
        await self.page.window.wait_until_ready_to_show()
        await self.page.window.center()

        self.page.window.visible = True

        await self.page.window.to_front()
        self.page.update()

    def run(self) -> None:
        api.ensure_data_dir()
        if api.credentials_exist():
            self._set_app_window()
            self.page.add(self.app_shell)
            self.show_view(0)
            self.refresh_balance()
            self.start_update_check()
        else:
            self.show_onboarding()

        self.page.run_task(self._reveal)
