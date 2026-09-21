import os
import configparser
from functools import lru_cache

from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse
from vonage_account import Balance

CONFIG_PATH = os.path.join("data", "config.ini")


@lru_cache(maxsize=1)
def _get_client(config_path: str) -> Vonage:
    config = configparser.ConfigParser()
    config.read(config_path)

    auth = Auth(
        api_key=config["api_credentials"]["api_key"],
        api_secret=config["api_credentials"]["api_secret"]
    )

    return Vonage(auth=auth)


def reset_client_cache() -> None:
    _get_client.cache_clear()


def send_sms(number: str, sender: str, text: str) -> SmsResponse:
    client = _get_client(CONFIG_PATH)

    message = SmsMessage(to=number, from_=sender, text=text, type="unicode")
    response: SmsResponse = client.sms.send(message)

    return response


def get_balance() -> str:
    client = _get_client(CONFIG_PATH)
    balance: Balance = client.account.get_balance()

    return (f"{balance.value:0.2f} EUR")