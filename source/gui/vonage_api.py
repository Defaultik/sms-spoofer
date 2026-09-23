import re
from functools import lru_cache

from requests.exceptions import RequestException
from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse
from vonage_account import Balance
from vonage_http_client.errors import AuthenticationError, HttpRequestError

from api import normalize, get_credentials

_API_KEY_RE = re.compile(r"^[0-9a-f]{8}$")


class CredentialsInvalidError(Exception):
    """The API key/secret are well-formed but Vonage rejected them — there's
    no account behind them."""


class CredentialsUnverifiableError(Exception):
    """Vonage couldn't be reached to check the credentials (network issue)."""


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
