import os
import math
from datetime import datetime


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


def format_timestamp(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return iso
