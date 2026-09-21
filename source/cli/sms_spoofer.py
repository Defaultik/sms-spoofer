import os
import configparser
import argparse
from getpass import getpass

from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse

_PHONE_JUNK = str.maketrans("", "", "+- ")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="SMS Spoofer", description="Send SMS with any CallerID and Any content")
    parser.add_argument("-n", "--number", required=True, help="victim's phone number")
    parser.add_argument("-s", "--sender", required=True, help="sender name (callerid)")
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


def send_sms(number: str, sender: str, text: str, config: configparser.ConfigParser) -> SmsResponse:
    auth = Auth(
        api_key=config["api_credentials"]["api_key"],
        api_secret=config["api_credentials"]["api_secret"],
    )
    client = Vonage(auth=auth)
    message = SmsMessage(to=number, from_=sender, text=text, type="unicode")
    return client.sms.send(message)


def main() -> None:
    args = parse_args()
    config = load_config()
    send_sms(normalize(args.number), args.sender, args.text, config)


if __name__ == "__main__":
    main()
