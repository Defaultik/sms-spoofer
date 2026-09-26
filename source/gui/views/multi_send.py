import flet as ft

import api
import vonage_api
from theme import ACCENT, SURFACE_2, BORDER, TEXT, TEXT_MUTED, pad
from widgets import (
    card, section_title, labeled, text_field, sender_id_field,
    primary_button, set_button_loading, cost_indicator,
)
from formatting import sms_segments, format_cost


def build_multi_send(app) -> ft.Control:
    page = app.page
    notify = app.notify
    describe_error = app.describe_error
    view_heading = app.view_heading
    refresh_balance = app.refresh_balance

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
                    api.record_send(n, sender.value, message.value)
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
            refresh_balance(delay=1)

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
