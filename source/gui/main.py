import sys
import os
import math

sys.path.insert(0, os.path.dirname(__file__))

import flet as ft
import api
import vonage_api

# Palette

BG = "#0D0E13"
SURFACE = "#161822"
SURFACE_2 = "#1D1F2C"
SURFACE_3 = "#232635"
BORDER = "#2A2D3D"
ACCENT = "#7C5CFF"
ACCENT_HOVER = "#8E71FF"
TEXT = "#F2F2F7"
TEXT_MUTED = "#8B8FA3"
SUCCESS = "#33D17A"
WARNING = "#F5A623"
DANGER = "#FF5C7A"
AVATAR_BG = "#2A2050"
VERSION_LABEL = "#3F4358"

RADIUS = 14


def read_version() -> str:
    pyproject = os.path.join(os.path.dirname(__file__), "..", "..", "pyproject.toml")
    try:
        with open(pyproject, encoding="utf-8") as f:
            for line in f:
                if line.startswith("version"):
                    return line.split("=", 1)[1].strip().strip("\"'")
    except OSError:
        pass

    return ""


def sms_segments(text: str) -> int:
    """Number of SMS parts for `text`. Messages are sent as unicode (UCS-2):
    70 chars in a single part, 67 per part once concatenated."""
    units = len(text.encode("utf-16-le")) // 2  # UCS-2 code units (emoji = 2)
    if not units:
        return 0
    return 1 if units <= 70 else math.ceil(units / 67)


def format_cost(total: float | None, currency: str, segments: int, recipients: int = 1) -> str:
    detail = f"{segments} part" + ("s" if segments != 1 else "")
    if recipients > 1:
        detail += f" × {recipients} numbers"
    if total is None:
        return detail
    return f"≈ {total:.4f} {currency} · {detail}"


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
                max_length=None, icon=None, expand=None, value="",
                autofocus=False, on_submit=None) -> ft.TextField:
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
        autofocus=autofocus,
        on_submit=on_submit,
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
    field = text_field("Sender ID", "e.g. YourBrand", max_length=11, icon=ft.Icons.BADGE_ROUNDED)
    field.counter = ""
    counter_text = ft.Text("0/11", size=11, color=TEXT_MUTED)
    field.suffix = counter_text

    def on_change(e):
        count = len(field.value or "")
        counter_text.value = f"{count}/11"
        counter_text.color = WARNING if count >= 11 else TEXT_MUTED
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
            bgcolor={
                ft.ControlState.DEFAULT: ACCENT,
                ft.ControlState.HOVERED: ACCENT_HOVER,
                ft.ControlState.DISABLED: SURFACE_2,
            },
            color={ft.ControlState.DEFAULT: "#FFFFFF", ft.ControlState.DISABLED: TEXT_MUTED},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=pad(16, 18),
            animation_duration=150,
        ),
    )


def set_button_loading(button: ft.FilledButton, loading: bool, label: str, icon=None) -> None:
    button.disabled = loading
    if loading:
        button.icon = None
        button.content = ft.Row(
            [
                ft.ProgressRing(width=15, height=15, stroke_width=2, color="#FFFFFF"),
                ft.Text(label, color="#FFFFFF", weight=ft.FontWeight.W_600),
            ],
            spacing=10,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER,
        )
    else:
        button.icon = icon
        button.content = label


def cost_indicator() -> tuple[ft.Row, ft.Text]:
    text = ft.Text("", size=12, color=TEXT_MUTED)
    row = ft.Row(
        [ft.Icon(ft.Icons.SELL_ROUNDED, size=15, color=TEXT_MUTED), text],
        spacing=6,
        tight=True,
        visible=False,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )
    return row, text


# App
def main(page: ft.Page) -> None:
    page.title = "SMS Spoofer - github.com/Defaultik"
    page.window.icon = "icon.ico"
    page.bgcolor = BG
    page.padding = 0
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ACCENT, use_material3=True)
    page.window.bgcolor = BG
    page.window.visible = False

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

    balance_controls: dict[str, ft.Control | str | None] = {"text": None, "button": None, "value": "···"}

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
        key_field.error = None
        secret_field.error = None

        key = (key_field.value or "").strip()
        secret = (secret_field.value or "").strip()

        if not key or not secret:
            notify("API key and secret can't be empty.", ok=False)
            return None
        
        if not vonage_api.is_valid_api_key(key):
            key_field.error = "Should be an 8-character key (0-9, a-f)"
            key_field.update()
            notify("That doesn't look like a valid Vonage API key.", ok=False)
            return None
        
        if not vonage_api.is_valid_api_secret(secret):
            secret_field.error = "That looks too short for a Vonage API secret"
            secret_field.update()
            notify("That doesn't look like a valid Vonage API secret.", ok=False)
            return None
        
        return key, secret

    # Balance
    def refresh_balance(e=None) -> None:
        text = balance_controls["text"]
        button = balance_controls["button"]
        if text is None or button is None:
            return

        button.icon = ft.ProgressRing(width=16, height=16, stroke_width=2, color=TEXT_MUTED)
        page.update()

        def worker():
            try:
                value = vonage_api.get_balance()
                display = f"{value:.2f} EUR"
            except Exception:
                display = "— EUR"

            balance_controls["value"] = display
            text.value = display
            button.icon = ft.Icons.REFRESH_ROUNDED
            page.update()

        page.run_thread(worker)

    def build_balance_row() -> ft.Row:
        text = ft.Text(balance_controls["value"], size=13, weight=ft.FontWeight.W_600, color=TEXT)
        refresh_btn = ft.IconButton(ft.Icons.REFRESH_ROUNDED, icon_size=16, icon_color=TEXT_MUTED,
                                     on_click=refresh_balance, tooltip="Refresh balance")
        balance_controls["text"] = text
        balance_controls["button"] = refresh_btn
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

    def view_heading(title: str, subtitle: str = "") -> ft.Control:
        return ft.Row(
            [section_title(title, subtitle), build_balance_row()],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.START,
        )

    # Single Send
    def build_single_send() -> ft.Control:
        number = text_field("Recipient number", "+1001234567", icon=ft.Icons.PHONE_IPHONE_ROUNDED,
                            autofocus=True)
        sender = sender_id_field()
        message = text_field("Text", "Type your text…", multiline=True, lines=6)
        send_btn = primary_button("Send", icon=ft.Icons.SEND_ROUNDED)

        cost_row, cost_text = cost_indicator()
        est = {"price": None, "currency": "", "number": ""}

        def render_estimate():
            segments = sms_segments(message.value or "")
            if segments == 0:
                cost_row.visible = False
            else:
                price = est["price"]
                total = price * segments if price is not None else None
                cost_text.value = format_cost(total, est["currency"], segments)
                cost_row.visible = True
            cost_row.update()

        def price_number(e=None):
            num = (number.value or "").strip()
            if num == est["number"] and est["price"] is not None:
                return
            est.update(number=num, price=None, currency="")
            render_estimate()
            if not num:
                return

            def worker():
                try:
                    price, currency = vonage_api.get_sms_price(vonage_api.get_country_code(num))
                    est.update(price=price, currency=currency)
                except Exception:
                    est.update(price=None, currency="")
                render_estimate()

            page.run_thread(worker)

        message.on_change = lambda e: render_estimate()
        number.on_blur = price_number

        def reset_send_btn():
            set_button_loading(send_btn, False, "Send", icon=ft.Icons.SEND_ROUNDED)

        def do_send(e):
            number.error = None
            if not number.value or not sender.value or not message.value:
                notify("Fill in number, sender and message first.", ok=False)
                return

            set_button_loading(send_btn, True, "Checking…")
            page.update()

            def worker():
                try:
                    vonage_api.validate_number(number.value)
                except vonage_api.NumberInvalidError:
                    number.error = "Not a valid phone number"
                    number.update()
                    notify("That doesn't look like a valid phone number.", ok=False)
                    reset_send_btn()
                    page.update()
                    return
                except vonage_api.NumberUnverifiableError as exc:
                    notify(f"Couldn't verify the number: {describe_error(exc)}", ok=False)
                    reset_send_btn()
                    page.update()
                    return

                set_button_loading(send_btn, True, "Sending…")
                page.update()
                try:
                    vonage_api.send_sms(number.value, sender.value, message.value)
                    notify("Message sent successfully.")
                    message.value = ""
                except Exception as exc:
                    notify(f"Send failed: {describe_error(exc)}", ok=False)
                finally:
                    reset_send_btn()
                    page.update()
                    refresh_balance()

            page.run_thread(worker)

        send_btn.on_click = do_send

        return ft.Column(
            [
                view_heading("Single Send", "Send one message to one recipient."),
                ft.Container(height=10),
                card(
                    ft.Column(
                        [
                            number,
                            ft.Row([sender], spacing=12),
                            labeled("Text", message),
                            ft.Row(
                                [send_btn, cost_row],
                                spacing=16,
                                alignment=ft.MainAxisAlignment.START,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            ),
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
                              active_color=ACCENT, label_style=ft.TextStyle(color=TEXT, size=13),
                              on_change=lambda e: recompute_recipient_prices())
            checkboxes.append(cb)
            return cb

        select_all = ft.Checkbox(label="Select all contacts", value=False, active_color=ACCENT,
                                    label_style=ft.TextStyle(color=TEXT, weight=ft.FontWeight.W_600))

        def toggle_all(e):
            for cb in checkboxes:
                cb.value = select_all.value
            page.update()
            recompute_recipient_prices()

        select_all.on_change = toggle_all
        select_all.disabled = not contacts

        if contacts:
            recipients_body = ft.ListView(
                [contact_row(c) for c in contacts],
                spacing=4,
                expand=True,
            )
        else:
            recipients_body = ft.Container(
                content=ft.Text(
                    "No saved contacts yet.\nAdd some in Contacts, or use Extra numbers.",
                    color=TEXT_MUTED, size=13, text_align=ft.TextAlign.CENTER,
                ),
                alignment=ft.Alignment.CENTER,
                expand=True,
                padding=pad(24, 12),
            )

        manual = text_field("Extra numbers (one per line)", "+1001234567\n+1009876543",
                             multiline=True, lines=3)
        sender = sender_id_field()
        message = text_field("Message", "Type your text…", multiline=True, expand=True)
        send_btn = primary_button("Send to all", icon=ft.Icons.SEND_AND_ARCHIVE_ROUNDED)

        progress_text = ft.Text("", size=12, color=TEXT_MUTED)
        progress_bar = ft.ProgressBar(value=0, color=ACCENT, bgcolor=SURFACE_2)
        progress_area = ft.Column([progress_text, progress_bar], spacing=6, visible=False)

        def manual_lines() -> list[str]:
            return [line.strip() for line in (manual.value or "").splitlines() if line.strip()]

        def collect_numbers() -> list[str]:
            numbers = [c.phone_number for c, cb in zip(contacts, checkboxes) if cb.value]
            numbers.extend(manual_lines())
            return numbers

        cost_row, cost_text = cost_indicator()
        est = {"unit_sum": None, "currency": "", "count": 0, "seq": 0}

        def render_estimate():
            segments = sms_segments(message.value or "")
            count = est["count"]
            if count == 0 or segments == 0:
                cost_row.visible = False
            else:
                unit_sum = est["unit_sum"]
                total = unit_sum * segments if unit_sum is not None else None
                cost_text.value = format_cost(total, est["currency"], segments, recipients=count)
                cost_row.visible = True
            cost_row.update()

        def recompute_recipient_prices(e=None):
            numbers = collect_numbers()
            est["count"] = len(numbers)
            est["seq"] += 1
            seq = est["seq"]
            if not numbers:
                est["unit_sum"] = None
                render_estimate()
                return
            render_estimate()

            def worker():
                unit_sum, currency, ok = 0.0, est["currency"], True
                for n in numbers:
                    try:
                        price, currency = vonage_api.get_sms_price(vonage_api.get_country_code(n))
                        unit_sum += price
                    except Exception:
                        ok = False
                        break
                if seq != est["seq"]:
                    return  # a newer change superseded this run
                est["unit_sum"] = unit_sum if ok else None
                est["currency"] = currency
                render_estimate()

            page.run_thread(worker)

        message.on_change = lambda e: render_estimate()
        manual.on_blur = recompute_recipient_prices

        def reset_send_btn():
            progress_area.visible = False
            set_button_loading(send_btn, False, "Send to all",
                               icon=ft.Icons.SEND_AND_ARCHIVE_ROUNDED)

        def do_send(e):
            manual.error = None

            numbers = collect_numbers()
            if not numbers:
                notify("Select at least one contact or add a number.", ok=False)
                return

            if not sender.value or not message.value:
                notify("Fill in sender and message first.", ok=False)
                return

            set_button_loading(send_btn, True, "Checking…")
            progress_area.visible = True
            progress_bar.value = None  # indeterminate while validating
            progress_text.value = "Checking numbers…"
            page.update()

            def worker():
                invalid = []
                for n in manual_lines():
                    try:
                        vonage_api.validate_number(n)
                    except vonage_api.NumberInvalidError:
                        invalid.append(n)
                    except vonage_api.NumberUnverifiableError as exc:
                        notify(f"Couldn't verify numbers: {describe_error(exc)}", ok=False)
                        reset_send_btn()
                        page.update()
                        return

                if invalid:
                    manual.error = "Invalid number(s): " + ", ".join(invalid)
                    manual.update()
                    notify("Extra numbers contains an invalid phone number.", ok=False)
                    reset_send_btn()
                    page.update()
                    return

                total = len(numbers)
                progress_bar.value = 0
                progress_text.value = f"Sending 0 of {total}…"
                page.update()

                failed = 0
                for i, n in enumerate(numbers, start=1):
                    try:
                        vonage_api.send_sms(n, sender.value, message.value)
                    except Exception:
                        failed += 1
                    progress_bar.value = i / total
                    progress_text.value = f"Sending {i} of {total}…"
                    page.update()

                if failed:
                    notify(f"Sent {total - failed}/{total} — {failed} failed.", ok=False)
                else:
                    notify(f"Sent to all {total} recipients.")

                reset_send_btn()
                page.update()
                refresh_balance()

            page.run_thread(worker)

        send_btn.on_click = do_send

        left = card(
            ft.Column(
                [section_title("Recipients"), select_all, ft.Divider(color=BORDER, height=1), recipients_body],
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
                    cost_row,
                    progress_area,
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
                view_heading("Multiple Send", "Send the same message to several recipients at once."),
                ft.Container(height=10),
                ft.Row([left, right], spacing=16, vertical_alignment=ft.CrossAxisAlignment.START, expand=True),
            ],
            spacing=0,
            expand=True,
        )

    # Contacts
    def build_contacts() -> ft.Control:
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

            set_button_loading(save_btn, True, "Verifying…")
            page.update()

            def worker():
                try:
                    vonage_api.verify_credentials(key, secret)
                except vonage_api.CredentialsInvalidError:
                    secret_f.error = "No Vonage account found for this key and secret"
                    secret_f.update()
                    notify("Vonage rejected those credentials — no such account.", ok=False)
                except vonage_api.CredentialsUnverifiableError as exc:
                    notify(f"Couldn't reach Vonage to verify credentials: {describe_error(exc)}", ok=False)
                else:
                    api.save_credentials(key, secret)
                    notify("Credentials updated.")
                    refresh_balance()
                finally:
                    set_button_loading(save_btn, False, "Save credentials", icon=ft.Icons.SAVE_ROUNDED)
                    page.update()

            page.run_thread(worker)

        save_btn.on_click = do_save
        secret_f.on_submit = do_save

        return ft.Column(
            [
                view_heading("Settings", "Update the Vonage API credentials used to send messages."),
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
        content.content = ft.Container(
            builder(),
            padding=ft.Padding(left=24, top=24, right=24, bottom=32),
            expand=True,
        )
        page.update()

    version = read_version()

    update_icon = ft.Icon(ft.Icons.CIRCLE, size=13, visible=False)

    def apply_update_status(latest: str | None) -> None:
        if not latest:
            return
        if api.is_outdated(version, latest):
            update_icon.icon = ft.Icons.ARROW_CIRCLE_UP_ROUNDED
            update_icon.color = WARNING
            update_icon.tooltip = (
                f"Version v{latest} is available\n"
                "   Update with git pull"
            )
        else:
            update_icon.icon = ft.Icons.CHECK_CIRCLE_ROUNDED
            update_icon.color = SUCCESS
            update_icon.tooltip = "You're on the latest version."
        update_icon.visible = True
        page.update()

    def start_update_check() -> None:
        if not version:
            return
        
        page.run_thread(lambda: apply_update_status(api.fetch_latest_version()))

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
                content=ft.Row(
                    [update_icon, ft.Text(f"v{version}", size=11, color=VERSION_LABEL)],
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

    app_shell = ft.Row(
        [rail_pane, ft.VerticalDivider(width=1, color=BORDER), content],
        spacing=0,
        expand=True,
    )

    # Login Panel
    def show_onboarding() -> None:
        key_f = text_field("Vonage API key", icon=ft.Icons.KEY_ROUNDED, autofocus=True)
        secret_f = text_field("Vonage API secret", icon=ft.Icons.LOCK_ROUNDED, password=True)
        start_btn = primary_button("Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)

        def do_start(e):
            creds = validated_credentials(key_f, secret_f)
            if creds is None:
                return
            key, secret = creds

            set_button_loading(start_btn, True, "Verifying…")
            page.update()

            def worker():
                try:
                    vonage_api.verify_credentials(key, secret)
                except vonage_api.CredentialsInvalidError:
                    secret_f.error = "No Vonage account found for this key and secret"
                    secret_f.update()
                    notify("Vonage rejected those credentials — no such account.", ok=False)
                    set_button_loading(start_btn, False, "Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)
                    page.update()
                except vonage_api.CredentialsUnverifiableError as exc:
                    notify(f"Couldn't reach Vonage to verify credentials: {describe_error(exc)}", ok=False)
                    set_button_loading(start_btn, False, "Continue", icon=ft.Icons.ARROW_FORWARD_ROUNDED)
                    page.update()
                else:
                    api.save_credentials(key, secret)
                    set_app_window()
                    page.controls.clear()
                    page.add(app_shell)
                    show_view(0)
                    refresh_balance()
                    start_update_check()

            page.run_thread(worker)

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

    async def reveal() -> None:
        await page.window.wait_until_ready_to_show()
        await page.window.center()

        page.window.visible = True
        
        await page.window.to_front()
        page.update()

    api.ensure_data_dir()
    if api.credentials_exist():
        set_app_window()
        page.add(app_shell)
        show_view(0)
        refresh_balance()
        start_update_check()
    else:
        show_onboarding()

    page.run_task(reveal)


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)
