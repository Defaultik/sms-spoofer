"""
sms-spoofer GUI — a Flet (https://flet.dev) desktop front-end that replaces
the old interactive CLI menu (source/menu). All Vonage / storage logic lives
in api.py; this module is UI only.

Run with: python source/gui/main.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import flet as ft
import api

# Palette

BG = "#0D0E13"
SURFACE = "#161822"
SURFACE_2 = "#1D1F2C"
BORDER = "#2A2D3D"
ACCENT = "#7C5CFF"
TEXT = "#F2F2F7"
TEXT_MUTED = "#8B8FA3"
SUCCESS = "#33D17A"
DANGER = "#FF5C7A"
AVATAR_BG = "#2A2050"
VERSION_LABEL = "#3F4358"  # dark gray, deliberately low-contrast on the rail

RADIUS = 14


def read_version() -> str:
    """Project version from the repo-root pyproject.toml (v2.0.0 style)."""
    pyproject = os.path.join(os.path.dirname(__file__), "..", "..", "pyproject.toml")
    try:
        with open(pyproject, encoding="utf-8") as f:
            for line in f:
                if line.startswith("version"):
                    return line.split("=", 1)[1].strip().strip("\"'")
    except OSError:
        pass
    return ""


# Style

def border_all(color: str, width: float = 1) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def border_bottom(color: str, width: float = 1) -> ft.Border:
    return ft.Border(bottom=ft.BorderSide(width, color))


def pad(v: float = 0, h: float = 0) -> ft.Padding:
    return ft.Padding(left=h, right=h, top=v, bottom=v)


# Controls

def card(content: ft.Control, width=None, height=None, expand=None, padding=20) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=SURFACE,
        border=border_all(BORDER),
        border_radius=RADIUS,
        padding=padding,
        width=width,
        height=height,
        expand=expand,
        animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
    )


def section_title(text: str, subtitle: str = "") -> ft.Column:
    controls = [ft.Text(text, size=20, weight=ft.FontWeight.W_600, color=TEXT)]
    if subtitle:
        controls.append(ft.Text(subtitle, size=13, color=TEXT_MUTED))
    return ft.Column(controls, spacing=2, tight=True)


def field_caption(text: str) -> ft.Text:
    return ft.Text(text, size=13, weight=ft.FontWeight.W_600, color=TEXT_MUTED)


def labeled(caption: str, field: ft.Control, expand: bool = False) -> ft.Column:
    return ft.Column(
        [field_caption(caption), field],
        spacing=6,
        tight=not expand,
        expand=expand,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
    )


def text_field(label, hint="", password=False, multiline=False, lines=1,
                max_length=None, icon=None, expand=None, value="") -> ft.TextField:
    field = ft.TextField(
        label=None if multiline else label,
        hint_text=hint,
        value=value,
        password=password,
        can_reveal_password=False,
        multiline=multiline,
        max_length=max_length,
        prefix_icon=icon,
        expand=expand,
        border={
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                border_radius=10, side=ft.BorderSide(1, BORDER)),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                border_radius=10, side=ft.BorderSide(1, ACCENT)),
            ft.ControlState.ERROR: ft.OutlineInputBorder(
                border_radius=10, side=ft.BorderSide(1, DANGER)),
        },
        bgcolor=SURFACE_2,
        color=TEXT,
        text_size=13,
        label_style=ft.TextStyle(color=TEXT_MUTED, size=13),
        hint_style=ft.TextStyle(color=TEXT_MUTED, size=13),
        cursor_color=ACCENT,
        text_vertical_align=-1 if multiline else None,
        fit_parent_size=multiline,
    )
    if password:
        def toggle_reveal(e: ft.ControlEvent) -> None:
            field.password = not field.password
            reveal_btn.icon = ft.Icons.VISIBILITY_ROUNDED if field.password else ft.Icons.VISIBILITY_OFF_ROUNDED
            field.update()

        reveal_btn = ft.IconButton(
            icon=ft.Icons.VISIBILITY_ROUNDED,
            icon_size=16,
            icon_color=TEXT_MUTED,
            on_click=toggle_reveal,
            width=24,
            height=24,
            style=ft.ButtonStyle(padding=0),
        )
        field.suffix = reveal_btn
    if multiline and not expand:
        field.height = 46 + lines * 22
    elif not multiline and not expand:
        field.height = 56
    return field


def sender_id_field() -> ft.TextField:
    """Sender ID field with the 11-char limit shown inline as a live counter
    (instead of Flet's default below-the-field counter)."""
    field = text_field("Sender ID", "e.g. YourBrand", max_length=11, icon=ft.Icons.BADGE_ROUNDED)
    field.counter = ""
    counter_text = ft.Text("0/11", size=11, color=TEXT_MUTED)
    field.suffix = counter_text

    def on_change(e):
        counter_text.value = f"{len(field.value or '')}/11"
        field.update()

    field.on_change = on_change
    return field


def primary_button(text, icon=None, on_click=None, expand=None) -> ft.FilledButton:
    return ft.FilledButton(
        content=text,
        icon=icon,
        on_click=on_click,
        expand=expand,
        style=ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: ACCENT, ft.ControlState.DISABLED: SURFACE_2},
            color={ft.ControlState.DEFAULT: "#FFFFFF", ft.ControlState.DISABLED: TEXT_MUTED},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=pad(16, 18),
            animation_duration=150,
        ),
    )


# App

def main(page: ft.Page) -> None:
    page.title = "SMS Spoofer - github.com/Defaultik"
    page.window.icon = "icon.ico"
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ACCENT, use_material3=True)
    page.window.bgcolor = BG

    def size_window(width: int, height: int, min_width: int, min_height: int) -> None:
        page.window.width = width
        page.window.height = height
        page.window.min_width = min_width
        page.window.min_height = min_height
        page.run_task(page.window.center)

    def set_app_window() -> None:
        size_window(980, 660, 880, 600)

    def set_onboarding_window() -> None:
        size_window(480, 460, 480, 460)

    view_title = ft.Text("Single Send", size=18, weight=ft.FontWeight.W_600, color=TEXT)
    balance_text = ft.Text("···", size=13, weight=ft.FontWeight.W_600, color=TEXT)
    balance_ring = ft.ProgressRing(width=14, height=14, stroke_width=2, color=ACCENT, visible=False)

    # Notifications

    def notify(message: str, ok: bool = True) -> None:
        page.show_dialog(
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

    def describe_error(exc: Exception) -> str:
        return str(exc) or exc.__class__.__name__

    def validated_credentials(
        key_field: ft.TextField, secret_field: ft.TextField
    ) -> tuple[str, str] | None:
        """Shared validation for the onboarding and settings credential forms:
        clears field errors, checks the entered key/secret, and returns the
        cleaned pair — or None (after showing a message) if anything is wrong."""
        key_field.error = None
        secret_field.error = None
        key = (key_field.value or "").strip()
        secret = (secret_field.value or "").strip()
        if not key or not secret:
            notify("API key and secret can't be empty.", ok=False)
            return None
        if not api.is_valid_api_key(key):
            key_field.error = "Should be an 8-character key (0-9, a-f)"
            key_field.update()
            notify("That doesn't look like a valid Vonage API key.", ok=False)
            return None
        if not api.is_valid_api_secret(secret):
            secret_field.error = "That looks too short for a Vonage API secret"
            secret_field.update()
            notify("That doesn't look like a valid Vonage API secret.", ok=False)
            return None
        return key, secret

    # Balance

    def refresh_balance(e=None) -> None:
        balance_ring.visible = True
        page.update()

        def worker():
            try:
                value = api.get_balance()
                balance_text.value = f"{value:.2f} EUR"
            except Exception:
                balance_text.value = "— EUR"
            balance_ring.visible = False
            page.update()

        page.run_thread(worker)

    # Single Send

    def build_single_send() -> ft.Control:
        number = text_field("Recipient number", "+1001234567", icon=ft.Icons.PHONE_IPHONE_ROUNDED)
        sender = sender_id_field()
        message = text_field("Text", "Type your text…", multiline=True, lines=6)
        send_btn = primary_button("Send", icon=ft.Icons.SEND_ROUNDED)

        def do_send(e):
            number.error = None
            if not number.value or not sender.value or not message.value:
                notify("Fill in number, sender and message first.", ok=False)
                return
            if not api.is_valid_phone(number.value):
                number.error = "Not a valid phone number"
                number.update()
                notify("That doesn't look like a valid phone number.", ok=False)
                return

            send_btn.disabled = True
            send_btn.content = "Sending…"
            page.update()

            def worker():
                try:
                    api.send_sms(number.value, sender.value, message.value)
                    notify("Message sent successfully.")
                    message.value = ""
                except Exception as exc:
                    notify(f"Send failed: {describe_error(exc)}", ok=False)
                finally:
                    send_btn.disabled = False
                    send_btn.content = "Send"
                    page.update()
                    refresh_balance()

            page.run_thread(worker)

        send_btn.on_click = do_send

        return ft.Column(
            [
                section_title("Single Send", "Send one message to one recipient."),
                ft.Container(height=10),
                card(
                    ft.Column(
                        [
                            number,
                            ft.Row([sender], spacing=12),
                            labeled("Text", message),
                            ft.Row([send_btn], alignment=ft.MainAxisAlignment.START),
                        ],
                        spacing=16,
                    ),
                ),
            ],
            spacing=0,
        )

    # Multiple Send

    def build_multi_send() -> ft.Control:
        contacts = api.load_contacts()
        checkboxes: list[ft.Checkbox] = []

        def contact_row(c: api.Contact) -> ft.Control:
            cb = ft.Checkbox(label=f"{c.name}  ·  {c.phone_number}", value=False,
                              active_color=ACCENT, label_style=ft.TextStyle(color=TEXT, size=13))
            checkboxes.append(cb)
            return cb

        select_all = ft.Checkbox(label="Select all contacts", value=False, active_color=ACCENT,
                                    label_style=ft.TextStyle(color=TEXT, weight=ft.FontWeight.W_600))

        def toggle_all(e):
            for cb in checkboxes:
                cb.value = select_all.value
            page.update()

        select_all.on_change = toggle_all

        contacts_list = ft.ListView(
            [contact_row(c) for c in contacts],
            spacing=4,
            expand=True,
        )

        manual = text_field("Extra numbers (one per line)", "+1001234567\n+1009876543",
                             multiline=True, lines=3)
        sender = sender_id_field()
        # fills whatever vertical space is left in the (fixed-height) Compose
        # card, which also pins the send button to the bottom of it
        message = text_field("Message", "Type your text…", multiline=True, expand=True)
        send_btn = primary_button("Send to all", icon=ft.Icons.SEND_AND_ARCHIVE_ROUNDED)

        def manual_lines() -> list[str]:
            return [line.strip() for line in (manual.value or "").splitlines() if line.strip()]

        def collect_numbers() -> list[str]:
            numbers = [c.phone_number for c, cb in zip(contacts, checkboxes) if cb.value]
            numbers.extend(manual_lines())
            return numbers

        def do_send(e):
            manual.error = None

            invalid = [line for line in manual_lines() if not api.is_valid_phone(line)]
            if invalid:
                manual.error = "Invalid number(s): " + ", ".join(invalid)
                manual.update()
                notify("Extra numbers contains an invalid phone number.", ok=False)
                return

            numbers = collect_numbers()
            if not numbers:
                notify("Select at least one contact or add a number.", ok=False)
                return
            if not sender.value or not message.value:
                notify("Fill in sender and message first.", ok=False)
                return

            send_btn.disabled = True
            send_btn.content = "Sending…"
            page.update()

            def worker():
                failed = 0
                for n in numbers:
                    try:
                        api.send_sms(n, sender.value, message.value)
                    except Exception:
                        failed += 1
                if failed:
                    notify(f"Sent {len(numbers) - failed}/{len(numbers)} — {failed} failed.", ok=False)
                else:
                    notify(f"Sent to all {len(numbers)} recipients.")
                send_btn.disabled = False
                send_btn.content = "Send to all"
                page.update()
                refresh_balance()

            page.run_thread(worker)

        send_btn.on_click = do_send

        left = card(
            ft.Column(
                [section_title("Recipients"), select_all, ft.Divider(color=BORDER, height=1), contacts_list],
                spacing=10,
                expand=True,
            ),
            width=300,
            expand=True,
            padding=pad(20, 20),
        )
        right = card(
            ft.Column(
                [
                    section_title("Compose"),
                    labeled("Extra numbers (one per line)", manual),
                    sender,
                    labeled("Message", message, expand=True),
                    send_btn,
                ],
                spacing=14,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                expand=True,
            ),
            expand=True,
            padding=pad(20, 20),
        )

        return ft.Column(
            [
                section_title("Multiple Send", "Send the same message to several recipients at once."),
                ft.Container(height=10),
                ft.Row([left, right], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            ],
            spacing=0,
            expand=True,
        )

    # Contacts

    def build_contacts() -> ft.Control:
        name_f = text_field("Name", "Jane Doe", icon=ft.Icons.PERSON_ROUNDED, expand=1)
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

            return ft.Container(
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
            )

        def do_add(e):
            phone_f.error = None
            if not name_f.value or not phone_f.value:
                notify("Enter both a name and a phone number.", ok=False)
                return
            if not api.is_valid_phone(phone_f.value):
                phone_f.error = "Not a valid phone number"
                phone_f.update()
                notify("That doesn't look like a valid phone number.", ok=False)
                return
            api.add_contact(name_f.value, phone_f.value)
            name_f.value = ""
            phone_f.value = ""
            render_contacts()
            page.update()

        render_contacts()

        return ft.Column(
            [
                section_title("Contacts", "Saved recipients you can reuse from Multiple Send."),
                ft.Container(height=10),
                card(
                    ft.Column(
                        [
                            ft.Row([name_f, phone_f, ft.IconButton(
                                        ft.Icons.PERSON_ADD_ROUNDED,
                                        icon_color="#FFFFFF",
                                        icon_size=16,
                                        bgcolor=AVATAR_BG,
                                        style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
                                        on_click=do_add,
                                        tooltip="Add contact",
                                    )],
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

    # Settings

    def build_settings() -> ft.Control:
        creds = api.get_credentials()
        key_f = text_field("Vonage API key", icon=ft.Icons.KEY_ROUNDED, value=creds[0] if creds else "")
        secret_f = text_field("Vonage API secret", icon=ft.Icons.LOCK_ROUNDED, password=True,
                               value=creds[1] if creds else "")
        save_btn = primary_button("Save credentials", icon=ft.Icons.SAVE_ROUNDED)

        def do_save(e):
            creds = validated_credentials(key_f, secret_f)
            if creds is None:
                return
            key, secret = creds

            save_btn.disabled = True
            save_btn.content = "Verifying…"
            page.update()

            def worker():
                try:
                    api.verify_credentials(key, secret)
                except api.CredentialsInvalidError:
                    secret_f.error = "No Vonage account found for this key and secret"
                    secret_f.update()
                    notify("Vonage rejected those credentials — no such account.", ok=False)
                except api.CredentialsUnverifiableError as exc:
                    notify(f"Couldn't reach Vonage to verify credentials: {describe_error(exc)}", ok=False)
                else:
                    api.save_credentials(key, secret)
                    notify("Credentials updated.")
                    refresh_balance()
                finally:
                    save_btn.disabled = False
                    save_btn.content = "Save credentials"
                    page.update()

            page.run_thread(worker)

        save_btn.on_click = do_save

        return ft.Column(
            [
                section_title("Settings", "Update the Vonage API credentials used to send messages."),
                ft.Container(height=10),
                card(
                    ft.Column(
                        [key_f, secret_f, ft.Row([save_btn], alignment=ft.MainAxisAlignment.START)],
                        spacing=16,
                    ),
                    width=460,
                ),
            ],
            spacing=0,
        )

    # Layout

    views = [
        ("Single Send", ft.Icons.SEND_ROUNDED, build_single_send),
        ("Multiple Send", ft.Icons.SEND_AND_ARCHIVE_ROUNDED, build_multi_send),
        ("Contacts", ft.Icons.CONTACTS_ROUNDED, build_contacts),
        ("Settings", ft.Icons.SETTINGS_ROUNDED, build_settings),
    ]

    content = ft.AnimatedSwitcher(
        content=ft.Container(),
        transition=ft.AnimatedSwitcherTransition.FADE,
        duration=220,
        switch_in_curve=ft.AnimationCurve.EASE_OUT,
        switch_out_curve=ft.AnimationCurve.EASE_IN,
        expand=True,
    )

    def show_view(index: int) -> None:
        title, _, builder = views[index]
        view_title.value = title
        content.content = ft.Container(
            builder(),
            padding=ft.Padding(left=24, top=24, right=24, bottom=32),
            expand=True,
        )
        page.update()

    version = read_version()

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
            for label, icon, _ in views
        ],
        on_change=lambda e: show_view(e.control.selected_index),
    )

    rail_children = [rail]
    if version:
        rail_children.append(
            ft.Container(
                content=ft.Text(f"v{version}", size=11, color=VERSION_LABEL),
                alignment=ft.Alignment.CENTER,
                padding=ft.Padding(left=0, right=0, top=8, bottom=16),
            )
        )
    rail_pane = ft.Container(
        content=ft.Column(rail_children, spacing=0, expand=True,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        bgcolor=SURFACE,
    )

    header = ft.Container(
        content=ft.Row(
            [
                view_title,
                ft.Row(
                    [
                        ft.Icon(ft.Icons.ACCOUNT_BALANCE_WALLET_ROUNDED, size=16, color=ACCENT),
                        balance_text,
                        balance_ring,
                        ft.IconButton(ft.Icons.REFRESH_ROUNDED, icon_size=16, icon_color=TEXT_MUTED,
                                       on_click=refresh_balance, tooltip="Refresh balance"),
                    ],
                    spacing=8,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        ),
        padding=pad(16, 24),
        border=border_bottom(BORDER),
    )

    app_shell = ft.Row(
        [rail_pane, ft.VerticalDivider(width=1, color=BORDER), ft.Column([header, content], spacing=0, expand=True)],
        spacing=0,
        expand=True,
    )

    # Login Panel
    def show_onboarding() -> None:
        key_f = text_field("Vonage API key", icon=ft.Icons.KEY_ROUNDED)
        secret_f = text_field("Vonage API secret", icon=ft.Icons.LOCK_ROUNDED, password=True)
        start_btn = primary_button("Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)

        def do_start(e):
            creds = validated_credentials(key_f, secret_f)
            if creds is None:
                return
            key, secret = creds

            start_btn.disabled = True
            start_btn.content = "Verifying…"
            page.update()

            def worker():
                try:
                    api.verify_credentials(key, secret)
                except api.CredentialsInvalidError:
                    secret_f.error = "No Vonage account found for this key and secret"
                    secret_f.update()
                    notify("Vonage rejected those credentials — no such account.", ok=False)
                    start_btn.disabled = False
                    start_btn.content = "Continue"
                    page.update()
                except api.CredentialsUnverifiableError as exc:
                    notify(f"Couldn't reach Vonage to verify credentials: {describe_error(exc)}", ok=False)
                    start_btn.disabled = False
                    start_btn.content = "Continue"
                    page.update()
                else:
                    api.save_credentials(key, secret)
                    set_app_window()
                    page.controls.clear()
                    page.add(app_shell)
                    show_view(0)
                    refresh_balance()

            page.run_thread(worker)

        start_btn.on_click = do_start

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

        set_onboarding_window()
        page.controls.clear()
        page.add(
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
        page.update()

    api.ensure_data_dir()
    if api.credentials_exist():
        set_app_window()
        page.add(app_shell)
        show_view(0)
        refresh_balance()
    else:
        show_onboarding()


if __name__ == "__main__":
    ft.run(main)
