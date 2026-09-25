import re
from functools import lru_cache

from pydantic import ValidationError
from requests.exceptions import RequestException
from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse
from vonage_account import Balance, GetCountryPricingRequest, ServiceType
from vonage_number_insight import BasicInsightRequest
from vonage_number_insight.errors import NumberInsightError
from vonage_http_client.errors import AuthenticationError, HttpRequestError

from api import normalize, get_credentials

_API_KEY_RE = re.compile(r"^[0-9a-f]{8}$")


class CredentialsInvalidError(Exception):
    """The API key/secret are well-formed but Vonage rejected them — there's
    no account behind them."""


class CredentialsUnverifiableError(Exception):
    """Vonage couldn't be reached to check the credentials (network issue)."""


class NumberInvalidError(Exception):
    """Vonage Number Insight rejected the number — it isn't a valid, dialable
    phone number."""


class NumberUnverifiableError(Exception):
    """Vonage Number Insight couldn't be reached to check the number (network
    issue)."""


def is_valid_api_key(api_key: str) -> bool:
    """Vonage API keys are always an 8-character lowercase hex string."""
    return bool(_API_KEY_RE.match(api_key or ""))


def is_valid_api_secret(api_secret: str) -> bool:
    secret = api_secret or ""
    return secret == secret.strip() and len(secret) >= 6


def verify_credentials(api_key: str, api_secret: str) -> None:
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
    get_sms_price.cache_clear()


def get_country_code(number: str) -> str:
    try:
        request = BasicInsightRequest(number=normalize(number))
    except ValidationError as exc:
        raise NumberInvalidError("That doesn't look like a valid phone number.") from exc

    try:
        info = _client().number_insight.get_basic_info(request)
    except NumberInsightError as exc:
        raise NumberInvalidError("Vonage couldn't validate this number.") from exc
    except Exception as exc:
        raise NumberUnverifiableError(str(exc) or exc.__class__.__name__) from exc

    return info.country_code


def validate_number(number: str) -> None:
    get_country_code(number)


@lru_cache(maxsize=64)
def get_sms_price(country_code: str) -> tuple[float, str]:
    request = GetCountryPricingRequest(country_code=country_code, type=ServiceType.SMS)
    pricing = _client().account.get_country_pricing(request)

    return float(pricing.default_price), pricing.currency


def send_sms(number: str, sender: str, text: str) -> SmsResponse:
    message = SmsMessage(to=normalize(number), from_=sender, text=text, type="unicode")
    return _client().sms.send(message)


def get_balance() -> float:
    balance: Balance = _client().account.get_balance()
    return balance.value
