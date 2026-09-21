"""
Backend layer for the GUI: Vonage API access, credentials storage and
contacts storage. No UI code lives here — source/gui/main.py is the only
module that imports Flet.
"""

import os
import re
import csv
import configparser
from functools import lru_cache
from dataclasses import dataclass

from requests.exceptions import RequestException
from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse
from vonage_account import Balance
from vonage_http_client.errors import AuthenticationError, HttpRequestError

DATA_DIR = "data"
CONFIG_PATH = os.path.join(DATA_DIR, "config.ini")
CONTACTS_PATH = os.path.join(DATA_DIR, "contacts.csv")
CONTACTS_FIELDS = ("name", "phone_number")

_PHONE_JUNK = str.maketrans("", "", "+- ")
_API_KEY_RE = re.compile(r"^[0-9a-f]{8}$")


class CredentialsInvalidError(Exception):
    """The API key/secret are well-formed but Vonage rejected them — there's
    no account behind them."""


class CredentialsUnverifiableError(Exception):
    """Vonage couldn't be reached to check the credentials (network issue)."""


def normalize(phone_number: str) -> str:
    return phone_number.translate(_PHONE_JUNK)


def is_valid_phone(phone_number: str) -> bool:
    digits = normalize(phone_number)
    return digits.isdigit() and 7 <= len(digits) <= 15


def is_valid_api_key(api_key: str) -> bool:
    """Vonage API keys are always an 8-character lowercase hex string."""
    return bool(_API_KEY_RE.match(api_key or ""))


def is_valid_api_secret(api_secret: str) -> bool:
    """Secrets vary in format across accounts, so this only rules out the
    obviously wrong (empty, whitespace, way too short)."""
    secret = api_secret or ""
    return secret == secret.strip() and len(secret) >= 6


def verify_credentials(api_key: str, api_secret: str) -> None:
    """Calls the Vonage Account API to confirm this key/secret pair actually
    belongs to a real account. Raises CredentialsInvalidError if Vonage
    rejects them, or CredentialsUnverifiableError if Vonage couldn't be
    reached at all; returns normally if they're good.

    Deliberately bypasses the cached client from _get_client() — this is
    used to check credentials before they're saved, and shouldn't poison the
    cache with a client built from values that may still change.
    """
    client = Vonage(auth=Auth(api_key=api_key, api_secret=api_secret))
    try:
        client.account.get_balance()
    except AuthenticationError as exc:
        raise CredentialsInvalidError(
            "No Vonage account found for that API key and secret."
        ) from exc
    except (HttpRequestError, RequestException) as exc:
        raise CredentialsUnverifiableError(str(exc) or exc.__class__.__name__) from exc


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
    reset_client_cache()


@lru_cache(maxsize=1)
def _get_client(api_key: str, api_secret: str) -> Vonage:
    return Vonage(auth=Auth(api_key=api_key, api_secret=api_secret))


def _client() -> Vonage:
    creds = get_credentials()
    if creds is None:
        raise RuntimeError("API credentials are not configured yet.")
    return _get_client(*creds)


def reset_client_cache() -> None:
    _get_client.cache_clear()


def send_sms(number: str, sender: str, text: str) -> SmsResponse:
    message = SmsMessage(to=normalize(number), from_=sender, text=text, type="unicode")
    return _client().sms.send(message)


def get_balance() -> float:
    balance: Balance = _client().account.get_balance()
    return balance.value


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
