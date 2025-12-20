import os
import configparser

from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse
from vonage_account import Balance


def send_sms(number: str, sender: str, text: str) -> SmsResponse:
    config = configparser.ConfigParser()
    config.read(os.path.join("data", "config.ini"))

    # Transmits user data to send sms
    auth = Auth(
        api_key=config["api_credentials"]["api_key"], 
        api_secret=config["api_credentials"]["api_secret"]
    )

    client = Vonage(auth=auth)

    message = SmsMessage(to=number, from_=sender, text=text, type="unicode")
    response: SmsResponse = client.sms.send(message)
    
    return response


def get_balance() -> str:
    config = configparser.ConfigParser()
    config.read(os.path.join("data", "config.ini"))

    auth = Auth(
        api_key=config["api_credentials"]["api_key"], 
        api_secret=config["api_credentials"]["api_secret"]
    )

    client = Vonage(auth=auth)
    balance: Balance = client.account.get_balance()

    return (f"{balance.value:0.2f} EUR")