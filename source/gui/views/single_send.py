import flet as ft

import api
import vonage_api
from widgets import card, labeled, text_field, sender_id_field, primary_button, set_button_loading, cost_indicator
from formatting import sms_segments, format_cost


def build_single_send(app) -> ft.Control:
    page = app.page
    notify = app.notify
    describe_error = app.describe_error
    view_heading = app.view_heading
    refresh_balance = app.refresh_balance

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
                api.record_send(number.value, sender.value, message.value)
                notify("Message sent successfully.")
                message.value = ""
            except Exception as exc:
                notify(f"Send failed: {describe_error(exc)}", ok=False)
            finally:
                reset_send_btn()
                page.update()
                refresh_balance(delay=1)

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
