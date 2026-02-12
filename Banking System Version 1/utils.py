"""************************************"""
"""    Code By Vinzuda Manthan S.      """
"""************************************"""

import os
import re
import time
import sys
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

class Utils:
    """Utility class for validation, UI effects, and formatting."""

    @staticmethod
    def clear_screen():
        os.system('cls' if os.name == 'nt' else 'clear')

    @staticmethod
    def loader(message="Processing", duration=1.5):
        print(Fore.CYAN + message, end="")
        for _ in range(3):
            time.sleep(duration / 3)
            print(".", end="", flush=True)
        print("\n")

    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone):
        return phone.isdigit() and len(phone) == 10

    @staticmethod
    def validate_dob(dob):
        try:
            datetime.strptime(dob, "%d/%m/%Y")
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_password(password):
        """Min 8 chars, 1 number, 1 symbol."""
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(not char.isalnum() for char in password):
            return False
        return True

    @staticmethod
    def format_currency(amount):
        return f"₹{amount:,.2f}"

    @staticmethod
    def display_header(title):
        Utils.clear_screen()
        print(Fore.YELLOW + "=" * 50)
        print(Fore.WHITE + Style.BRIGHT + title.center(50))
        print(Fore.YELLOW + "=" * 50 + "\n")

    @staticmethod
    def get_input(prompt, validator=None, error_msg="Invalid input. Please try again."):
        while True:
            val = input(Fore.WHITE + f"{prompt}: ").strip()
            if not val:
                print(Fore.RED + "Field cannot be empty.")
                continue
            if validator and not validator(val):
                print(Fore.RED + error_msg)
                continue
            return val
