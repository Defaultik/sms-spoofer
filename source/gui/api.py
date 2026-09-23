"""
Application layer for the GUI: credentials/config storage, contacts storage,
phone helpers and the update check. Vonage service access lives in
source/gui/vonage_api.py. No UI code lives here — source/gui/main.py is the
only module that imports Flet.
"""

import os
import csv
import configparser
from dataclasses import dataclass

import requests
from requests.exceptions import RequestException

DATA_DIR = "data"
CONFIG_PATH = os.path.join(DATA_DIR, "config.ini")
CONTACTS_PATH = os.path.join(DATA_DIR, "contacts.csv")
CONTACTS_FIELDS = ("name", "phone_number")

_PHONE_JUNK = str.maketrans("", "", "+- ")

# Update check — the repo ships via `git clone` of the main branch, and the
# version lives in the repo-root pyproject.toml, so "latest" is just that same
# field read straight off main.
GITHUB_PYPROJECT_URL = (
    "https://raw.githubusercontent.com/Defaultik/sms-spoofer/main/pyproject.toml"
)
UPDATE_CHECK_TIMEOUT = 6  # seconds


def normalize(phone_number: str) -> str:
    return phone_number.translate(_PHONE_JUNK)


def is_valid_phone(phone_number: str) -> bool:
    digits = normalize(phone_number)
    return digits.isdigit() and 7 <= len(digits) <= 15


def _parse_version(version: str) -> tuple[int, ...]:
    try:
        return tuple(int(part) for part in version.strip().split("."))
    except ValueError:
        return ()


def _version_from_pyproject(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("version"):
            return line.split("=", 1)[1].strip().strip("\"'")
        
    return ""


def fetch_latest_version() -> str | None:
    try:
        response = requests.get(GITHUB_PYPROJECT_URL, timeout=UPDATE_CHECK_TIMEOUT)
        response.raise_for_status()
    except RequestException:
        return None
    
    return _version_from_pyproject(response.text) or None


def is_outdated(current: str, latest: str) -> bool:
    current_parts, latest_parts = _parse_version(current), _parse_version(latest)
    if current_parts and latest_parts:
        return latest_parts > current_parts
    
    return latest != current


def ensure_data_dir() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CONTACTS_PATH):
        with open(CONTACTS_PATH, "w", newline="") as f:
            csv.DictWriter(f, fieldnames=CONTACTS_FIELDS).writeheader()


def credentials_exist() -> bool:
    if not os.path.exists(CONFIG_PATH):
        return False
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config.has_option("api_credentials", "api_key") and config.has_option(
        "api_credentials", "api_secret"
    )


def get_credentials() -> tuple[str, str] | None:
    if not credentials_exist():
        return None
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return (
        config["api_credentials"]["api_key"],
        config["api_credentials"]["api_secret"],
    )


def save_credentials(api_key: str, api_secret: str) -> None:
    ensure_data_dir()
    config = configparser.ConfigParser()
    config["api_credentials"] = {"api_key": api_key, "api_secret": api_secret}
    with open(CONFIG_PATH, "w") as f:
        config.write(f)

    from vonage_api import reset_client_cache
    reset_client_cache()


@dataclass
class Contact:
    name: str
    phone_number: str


def load_contacts() -> list[Contact]:
    ensure_data_dir()
    with open(CONTACTS_PATH, newline="") as f:
        return [Contact(**row) for row in csv.DictReader(f)]


def save_contacts(contacts: list[Contact]) -> None:
    ensure_data_dir()
    with open(CONTACTS_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CONTACTS_FIELDS)
        writer.writeheader()
        for c in contacts:
            writer.writerow({"name": c.name, "phone_number": c.phone_number})


def add_contact(name: str, phone_number: str) -> None:
    contacts = load_contacts()
    contacts.append(Contact(name=name, phone_number=normalize(phone_number)))
    save_contacts(contacts)


def delete_contact(index: int) -> None:
    contacts = load_contacts()
    del contacts[index]
    save_contacts(contacts)
