import flet as ft

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


def border_all(color: str, width: float = 1) -> ft.Border:
    side = ft.BorderSide(width, color)
    return ft.Border(top=side, right=side, bottom=side, left=side)


def pad(v: float = 0, h: float = 0) -> ft.Padding:
    return ft.Padding(left=h, right=h, top=v, bottom=v)
