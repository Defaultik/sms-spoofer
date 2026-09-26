import flet as ft

import api
import vonage_api
from widgets import card, text_field, primary_button, set_button_loading


def build_settings(app) -> ft.Control:
    page = app.page
    notify = app.notify
    describe_error = app.describe_error
    view_heading = app.view_heading
    refresh_balance = app.refresh_balance
    validated_credentials = app.validated_credentials

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
