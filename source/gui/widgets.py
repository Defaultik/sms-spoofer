import flet as ft

from theme import (
    SURFACE, SURFACE_2, BORDER, ACCENT, ACCENT_HOVER, RADIUS,
    TEXT, TEXT_MUTED, WARNING, DANGER, border_all, pad,
)


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
