"""************************************"""
"""    Code By Vinzuda Manthan S.      """
"""************************************"""

import sys
import time
from utils import Utils, Fore, Style
from auth import Auth
from banking import Banking
from admin import AdminPortal

def user_dashboard(user_data):
    session = Banking(user_data)
    while True:
        Utils.display_header(f"WELCOME, {session.user['full_name'].upper()}")
        print(f"Account: {session.user['account_number']} | Balance: {Utils.format_currency(session.user['balance'])}")
        print("-" * 50)
        print("1. View Account Details")
        print("2. Deposit Money")
        print("3. Withdraw Money")
        print("4. Check Balance")
        print("5. Transaction History")
        print("6. Transfer Money")
        print("7. Apply Monthly Interest (Savings)")
        print("8. Change Password")
        print("9. Delete Account")
        print("0. Logout")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1': session.view_details()
        elif choice == '2': session.deposit()
        elif choice == '3': session.withdraw()
        elif choice == '4': 
            Utils.loader("Fetching balance")
            print(Fore.GREEN + f"Current Balance: {Utils.format_currency(session.user['balance'])}")
            input("\nPress Enter...")
        elif choice == '5': session.transaction_history()
        elif choice == '6': session.transfer()
        elif choice == '7': session.apply_interest()
        elif choice == '8': session.change_password()
        elif choice == '9': 
            if session.delete_account(): break
        elif choice == '0':
            Utils.loader("Logging out")
            break
        else:
            print(Fore.RED + "Invalid choice.")
            time.sleep(1)

def main():
    while True:
        Utils.display_header("Manthan GLOBAL BANK")
        print("1. Login to Account")
        print("2. Open New Account")
        print("3. Admin Portal")
        print("0. Exit System")
        
        choice = input("\nSelect Option: ")
        
        if choice == '1':
            user = Auth.login()
            if user:
                user_dashboard(user)
        elif choice == '2':
            Auth.register()
        elif choice == '3':
            AdminPortal().login()
        elif choice == '0':
            print(Fore.YELLOW + "Thank you for using Manthan Global Bank. Goodbye!")
            sys.exit()
        else:
            print(Fore.RED + "Invalid choice.")
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n" + Fore.YELLOW + "System forced shutdown. Data is safe.")
        sys.exit()
