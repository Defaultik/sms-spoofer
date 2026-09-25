################################
# Made by github.com/Defaultik #
################################

import os
import sys
import configparser
import argparse
from getpass import getpass

from pydantic import ValidationError
from requests.exceptions import RequestException
from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse
from vonage_sms.errors import SmsError
from vonage_number_insight import BasicInsightRequest
from vonage_number_insight.errors import NumberInsightError
from vonage_http_client.errors import AuthenticationError, HttpRequestError

_PHONE_JUNK = str.maketrans("", "", "+- ")


def log(prefix: str, message: str) -> None:
    print(f"[{prefix}] {message}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="SMS Spoofer", description="Send SMS with any CallerID and Any content")
    parser.add_argument("-n", "--number", required=True, help="recipient's phone number")
    parser.add_argument("-s", "--sender", required=True, help="sender name (CallerID)")
    parser.add_argument("-t", "--text", required=True, help="message content")

    return parser.parse_args()


def normalize(phone_number: str) -> str:
    return phone_number.translate(_PHONE_JUNK)


def load_config() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    if not os.path.exists("config.ini"):
        config["api_credentials"] = {
            "api_key": input("[!] Enter your Vonage API key: "),
            "api_secret": getpass("[!] Enter your Vonage API Secret: "),
        }
        with open("config.ini", "w") as config_file:
            config.write(config_file)

    config.read("config.ini")

    return config


def build_client(config: configparser.ConfigParser) -> Vonage:
    auth = Auth(
        api_key=config["api_credentials"]["api_key"],
        api_secret=config["api_credentials"]["api_secret"],
    )

    return Vonage(auth=auth)


def validate_number(client: Vonage, number: str) -> None:
    try:
        request = BasicInsightRequest(number=number)
    except ValidationError as exc:
        raise ValueError("That doesn't look like a valid phone number") from exc

    try:
        client.number_insight.get_basic_info(request)
    except NumberInsightError as exc:
        raise ValueError("Vonage couldn't validate this number") from exc
    except (HttpRequestError, RequestException) as exc:
        raise ConnectionError(str(exc) or exc.__class__.__name__) from exc


def send_sms(client: Vonage, number: str, sender: str, text: str) -> SmsResponse:
    message = SmsMessage(to=number, from_=sender, text=text, type="unicode")

    return client.sms.send(message)


def main() -> None:
    args = parse_args()
    config = load_config()
    client = build_client(config)

    number = normalize(args.number)

    try:
        validate_number(client, number)
    except ValueError as exc:
        log("-", f"Invalid number: {exc}.")
        sys.exit(1)
    except ConnectionError as exc:
        log("-", f"Couldn't reach Vonage to validate the number: {exc}.")
        sys.exit(1)

    try:
        response = send_sms(client, number, args.sender, args.text)
    except AuthenticationError:
        log("-", "Vonage rejected your API key/secret — check config.ini.")
        sys.exit(1)
    except SmsError as exc:
        log("-", f"Vonage rejected the message: {exc}")
        sys.exit(1)
    except (HttpRequestError, RequestException) as exc:
        log("-", f"Couldn't reach Vonage to send the message: {exc}.")
        sys.exit(1)

    message = response.messages[0]
    log("+", f"Message sent to {message.to}")
    if message.remaining_balance is not None:
        log("+", f"Remaining balance: {float(message.remaining_balance):.2f} EUR.")


if __name__ == "__main__":
    main()
