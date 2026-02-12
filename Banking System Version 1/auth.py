import bcrypt
import random
import string
from database import db
from utils import Utils, Fore

class Auth:
    """Handles User Registration and Login."""

    @staticmethod
    def generate_account_number():
        """Generates a unique 12-digit account number."""
        while True:
            acc_num = "".join([str(random.randint(0, 9)) for _ in range(12)])
            conn = db.get_connection()
            user = conn.execute("SELECT id FROM users WHERE account_number = ?", (acc_num,)).fetchone()
            conn.close()
            if not user:
                return acc_num

    @staticmethod
    def register():
        Utils.display_header("OPEN NEW ACCOUNT")
        
        name = Utils.get_input("Full Name")
        dob = Utils.get_input("DOB (DD/MM/YYYY)", Utils.validate_dob, "Format: DD/MM/YYYY")
        phone = Utils.get_input("Mobile Number (10 digits)", Utils.validate_phone, "Must be 10 digits")
        email = Utils.get_input("Email", Utils.validate_email, "Invalid email format")
        address = Utils.get_input("Address")
        
        password = Utils.get_input("Password (min 8 chars, 1 num, 1 sym)", 
                                   Utils.validate_password, 
                                   "Password too weak")
        
        print("\nAccount Types: 1. Savings  2. Current")
        acc_type_choice = Utils.get_input("Select Type (1/2)", lambda x: x in ['1', '2'])
        acc_type = "Savings" if acc_type_choice == '1' else "Current"
        
        try:
            deposit = float(Utils.get_input("Initial Deposit (Min ₹1000)", 
                                           lambda x: x.isdigit() and float(x) >= 1000))
        except ValueError:
            print(Fore.RED + "Invalid amount.")
            return

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        acc_num = Auth.generate_account_number()
        ifsc = "GMNB0001234"

        try:
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (full_name, dob, phone, email, address, password_hash, 
                                  account_number, ifsc_code, account_type, balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, dob, phone, email, address, hashed_pw, acc_num, ifsc, acc_type, deposit))
            
            # First transaction
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, balance_after)
                VALUES (?, 'Initial Deposit', ?, ?)
            ''', (acc_num, deposit, deposit))
            
            conn.commit()
            Utils.loader("Creating your account")
            print(Fore.GREEN + f"\nSuccess! Account Created.")
            print(Fore.CYAN + f"Account Number: {acc_num}")
            print(Fore.CYAN + f"IFSC: {ifsc}")
            input("\nPress Enter to continue...")
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
        finally:
            conn.close()

    @staticmethod
    def login():
        Utils.display_header("LOGIN TO BANKING")
        acc_num = Utils.get_input("Account Number")
        password = input(Fore.WHITE + "Password: ").strip()

        conn = db.get_connection()
        user = conn.execute("SELECT * FROM users WHERE account_number = ?", (acc_num,)).fetchone()

        if not user:
            print(Fore.RED + "Account not found.")
            time.sleep(1.5)
            return None

        if user['is_active'] == 0:
            print(Fore.RED + "Account has been deleted.")
            time.sleep(1.5)
            return None

        if user['is_frozen'] == 1:
            print(Fore.RED + "Account is frozen. Contact Admin.")
            time.sleep(1.5)
            return None

        if user['failed_attempts'] >= 3:
            print(Fore.RED + "Account locked due to 3 failed attempts.")
            time.sleep(1.5)
            return None

        if bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Reset failed attempts
            conn.execute("UPDATE users SET failed_attempts = 0 WHERE account_number = ?", (acc_num,))
            conn.commit()
            conn.close()
            Utils.loader("Authenticating")
            return dict(user)
        else:
            attempts = user['failed_attempts'] + 1
            conn.execute("UPDATE users SET failed_attempts = ? WHERE account_number = ?", (attempts, acc_num))
            conn.commit()
            conn.close()
            print(Fore.RED + f"Invalid Password. Attempts left: {3 - attempts}")
            time.sleep(1.5)
            return None
