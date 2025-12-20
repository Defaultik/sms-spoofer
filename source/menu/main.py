import configparser
import os
import csv
from api import send_sms, get_balance


BANNER = r"""
   ___ __  __ ___     ___ ___  ___   ___  ___ ___ ___  
  / __|  \/  / __|   / __| _ \/ _ \ / _ \| __| __| _ \ 
  \__ \ |\/| \__ \   \__ \  _/ (_) | (_) | _|| _||   / 
  |___/_|  |_|___/   |___/_|  \___/ \___/|_| |___|_|_\ 
"""


def print_options(*args) -> None:
    for num, name in enumerate(args):
        print(f"[{num + 1}]", name)


def normalize(num: str) -> str:
    return num.replace("+", "").replace("-", "").replace(" ", "")


def load_config(path: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    config.read(path)

    return config


def init() -> None:
    os.makedirs("data", exist_ok=True)
    
    contacts_path = "data/contacts.csv"
    config_path = "data/config.ini"

    if not os.path.exists(contacts_path):
        with open(contacts_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=("name", "phone_number"))
            w.writeheader()

    if not os.path.exists(config_path):
        api_key = input("Enter your Vonage API key: ")
        api_secret = input("Enter your Vonage API Secret: ")

        config = configparser.ConfigParser()
        config["api_credentials"] = {"api_key": api_key, "api_secret": api_secret}
        with open(config_path, "w") as f:
            config.write(f)

    config = load_config(config_path)
    main()


def main() -> None:
    try:
        display_menu()
    except KeyboardInterrupt:
        pass

    print("\n\nThank you for using!\nfrom https://github.com/Defaultik with <3")


def display_menu() -> None:
    while True:
        print("=" * 56)
        print(BANNER)
        print(f"{' ' * 10}Your remaining balance is {get_balance()}")
        print("=" * 56)

        print_options("Single", "Multiple", "Contacts", "API Credentials", "Exit")
        selected_option = input("Enter number of the task: ")
        print("=" * 56)

        match selected_option:
            case "1":
                dial_number()
            case "2":
                dial_multi()
            case "3":
                open_contacts()
            case "4":
                update_api()
            case "5":
                break
            case _:
                print("ERROR: Invalid option, try again")


def dial_number() -> None:
    number = normalize(input("Victim number: "))
    sender = input("Sender name: ")
    text = input("Text: ")

    send_sms(number, sender, text)
    print("\nMessage sent successfully!")


def dial_multi() -> None:
    print_options("All contacts", "Manual", "Back")
    choice = input("Enter number of the task: ")
    print("=" * 56)

    numbers = []
    if choice == "1":
        with open("data/contacts.csv") as f:
            numbers = [r["phone_number"] for r in csv.DictReader(f)]
    elif choice == "2":
        for i in range(int(input("How many numbers: "))):
            numbers.append(normalize(input(f"Victim #{i + 1}: ")))
    else:
        return

    sender = input("Sender name: ")
    text = input("Text: ")
    for n in numbers:
        send_sms(n, sender, text)


def open_contacts() -> None:
    with open("data/contacts.csv") as f:
        reader = csv.DictReader(f)
        for num, row in enumerate(reader):
            print(f"[{num + 1}]", row["name"])

    print("\n[*] Create a new contact")
    print("[X] Back")

    task = input("\nEnter number of the task: ")
    print("=" * 56)

    if task == "*":
        new_contact()
    else:
        try:
            with open("data/contacts.csv") as f:
                rows = list(csv.DictReader(f))

            num = rows[int(task) - 1]["phone_number"]
            send_sms(num, input("Sender name: "), input("Text: "))
        except (ValueError, IndexError):
            print("ERROR: Invalid option")
            
    return


def new_contact() -> None:
    name = input("\nContact name: ")
    number = normalize(input("Contact number: "))
        
    with open("data/contacts.csv", "a", newline="") as f:
        csv.DictWriter(f, fieldnames=("name", "phone_number")).writerow(
            {"name": name, "phone_number": number}
        )


def update_api() -> None:
    config_path = "data/config.ini"
    config = load_config(config_path)

    sure = input("Are you sure you want to change API Credentials (Y/N): ")
    if sure.lower() == "y":
        config.set("api_credentials", "api_key", input("Enter new API key: "))
        config.set("api_credentials", "api_secret", input("Enter new API secret: "))

        with open("data/config.ini", "w") as f:
            config.write(f)
        

if __name__ == "__main__":
    init()
    