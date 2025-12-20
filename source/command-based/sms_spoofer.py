import os
import configparser
import argparse
from getpass import getpass

from vonage import Vonage, Auth
from vonage_sms import SmsMessage, SmsResponse


class ArgsParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="SMS Spoofer", description="Send SMS with any CallerID and Any content")

    def setup(self) -> None:
        self.parser.add_argument("-n", "--number", required=True, help="victim's phone number")
        self.parser.add_argument("-s", "--sender", required=True, help="sender name (callerid)")
        self.parser.add_argument("-t", "--text", required=True, help="message content")

    def get_args(self) -> argparse.Namespace:
        return self.parser.parse_args()


def normalize(phone_number: str) -> str:
    """
    :param phone_number: Description
    """
    return phone_number.replace("+", "").replace("-", "").replace(" ", "")


def main() -> None:
    args_parser = ArgsParser()
    args_parser.setup()
    args = args_parser.get_args()

    config = configparser.ConfigParser()
    if not os.path.exists("config.ini"):
        api_key = input("[!] Enter your Vonage API key: ")
        api_secret = getpass("[!] Enter your Vonage API Secret: ")

        config.add_section("api_credentials")

        config.set("api_credentials", "api_key", api_key)
        config.set("api_credentials", "api_secret", api_secret)

        with open("config.ini", "w") as config_file:
            config.write(config_file)

    config.read("config.ini")

    send_sms(normalize(args.number), args.sender, args.text)


def send_sms(number: str, sender: str, text: str) -> SmsResponse:
    """    
    :param number: victim's phone number
    :param sender: sender's name (callerid)
    :param text: text of the sms
    :rtype: SmsResponse
    """
    config = configparser.ConfigParser()
    config.read("config.ini")
    
    auth = Auth(
        api_key=config["api_credentials"]["api_key"], 
        api_secret=config["api_credentials"]["api_secret"]
    )

    client = Vonage(auth=auth)

    message = SmsMessage(to=number, from_=sender, text=text, type="unicode")
    response: SmsResponse = client.sms.send(message)

    return response


if __name__ == "__main__":
    main()
