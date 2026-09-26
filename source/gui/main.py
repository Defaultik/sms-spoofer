import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

import flet as ft
from app import SmsSpooferApp


def main(page: ft.Page) -> None:
    SmsSpooferApp(page).run()


if __name__ == "__main__":
    ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)
