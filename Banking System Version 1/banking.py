"""************************************"""
"""    Code By Vinzuda Manthan S.      """
"""************************************"""

from database import db
from utils import Utils, Fore, Style
from tabulate import tabulate
from datetime import datetime
import bcrypt

class Banking:
    """Handles core banking features for logged-in users."""

    def __init__(self, user):
        self.user = user

    def refresh_user(self):
        conn = db.get_connection()
        updated = conn.execute("SELECT * FROM users WHERE account_number = ?", 
                              (self.user['account_number'],)).fetchone()
        conn.close()
        self.user = dict(updated)

    def view_details(self):
        Utils.display_header("ACCOUNT DETAILS")
        data = [
            ["Full Name", self.user['full_name']],
            ["Account No", self.user['account_number']],
            ["IFSC", self.user['ifsc_code']],
            ["Type", self.user['account_type']],
            ["Balance", Utils.format_currency(self.user['balance'])],
            ["Status", "Active" if self.user['is_active'] else "Inactive"],
            ["Joined", self.user['created_at']]
        ]
        print(tabulate(data, tablefmt="fancy_grid"))
        input("\nPress Enter to return...")

    def deposit(self):
        Utils.display_header("DEPOSIT MONEY")
        try:
            amount = float(Utils.get_input("Enter amount to deposit", lambda x: float(x) > 0))
            conn = db.get_connection()
            cursor = conn.cursor()
            
            new_balance = self.user['balance'] + amount
            cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", 
                           (new_balance, self.user['account_number']))
            
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, balance_after)
                VALUES (?, 'Deposit', ?, ?)
            ''', (self.user['account_number'], amount, new_balance))
            
            conn.commit()
            conn.close()
            self.refresh_user()
            print(Fore.GREEN + f"Successfully deposited {Utils.format_currency(amount)}.")
            print(f"New Balance: {Utils.format_currency(self.user['balance'])}")
        except ValueError:
            print(Fore.RED + "Invalid input.")
        input("\nPress Enter to continue...")

    def withdraw(self):
        Utils.display_header("WITHDRAW MONEY")
        try:
            amount = float(Utils.get_input("Enter amount to withdraw", lambda x: float(x) > 0))
            if amount > self.user['balance']:
                print(Fore.RED + "Insufficient balance.")
            elif self.user['balance'] - amount < 500:
                print(Fore.RED + "Error: Must maintain minimum ₹500 balance.")
            else:
                conn = db.get_connection()
                cursor = conn.cursor()
                new_balance = self.user['balance'] - amount
                cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", 
                               (new_balance, self.user['account_number']))
                cursor.execute('''
                    INSERT INTO transactions (account_number, transaction_type, amount, balance_after)
                    VALUES (?, 'Withdrawal', ?, ?)
                ''', (self.user['account_number'], amount, new_balance))
                conn.commit()
                conn.close()
                self.refresh_user()
                print(Fore.GREEN + f"Success! Withdrew {Utils.format_currency(amount)}.")
        except ValueError:
            print(Fore.RED + "Invalid input.")
        input("\nPress Enter to continue...")

    def transfer(self):
        Utils.display_header("TRANSFER MONEY")
        target_acc = Utils.get_input("Enter Receiver Account Number")
        if target_acc == self.user['account_number']:
            print(Fore.RED + "Cannot transfer to yourself.")
            input("\nPress Enter...")
            return

        conn = db.get_connection()
        receiver = conn.execute("SELECT * FROM users WHERE account_number = ? AND is_active = 1", 
                                (target_acc,)).fetchone()
        
        if not receiver:
            print(Fore.RED + "Receiver account not found or inactive.")
            conn.close()
            input("\nPress Enter...")
            return

        try:
            amount = float(Utils.get_input("Enter transfer amount", lambda x: float(x) > 0))
            if self.user['balance'] - amount < 500:
                print(Fore.RED + "Transfer failed. Insufficient funds (Min ₹500 rule).")
            else:
                cursor = conn.cursor()
                # Deduct from sender
                new_sender_bal = self.user['balance'] - amount
                cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", 
                               (new_sender_bal, self.user['account_number']))
                cursor.execute('''
                    INSERT INTO transactions (account_number, transaction_type, amount, balance_after, related_account)
                    VALUES (?, 'Transfer Sent', ?, ?, ?)
                ''', (self.user['account_number'], amount, new_sender_bal, target_acc))

                # Add to receiver
                new_rec_bal = receiver['balance'] + amount
                cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", 
                               (new_rec_bal, target_acc))
                cursor.execute('''
                    INSERT INTO transactions (account_number, transaction_type, amount, balance_after, related_account)
                    VALUES (?, 'Transfer Received', ?, ?, ?)
                ''', (target_acc, amount, new_rec_bal, self.user['account_number']))

                conn.commit()
                self.refresh_user()
                print(Fore.GREEN + f"Successfully transferred {Utils.format_currency(amount)} to {target_acc}.")
        except ValueError:
            print(Fore.RED + "Invalid amount.")
        finally:
            conn.close()
        input("\nPress Enter to continue...")

    def transaction_history(self):
        page = 0
        while True:
            Utils.display_header("TRANSACTION HISTORY")
            conn = db.get_connection()
            txs = conn.execute('''
                SELECT id, timestamp, transaction_type, amount, balance_after 
                FROM transactions WHERE account_number = ? 
                ORDER BY timestamp DESC LIMIT 5 OFFSET ?
            ''', (self.user['account_number'], page * 5)).fetchall()
            conn.close()

            if not txs and page == 0:
                print("No transactions yet.")
                break
            
            headers = ["ID", "Timestamp", "Type", "Amount", "Balance"]
            rows = [[t['id'], t['timestamp'], t['transaction_type'], 
                     Utils.format_currency(t['amount']), Utils.format_currency(t['balance_after'])] for t in txs]
            
            print(tabulate(rows, headers=headers, tablefmt="simple"))
            print(f"\nPage {page + 1} | [N] Next | [P] Previous | [B] Back")
            choice = input("Choice: ").lower()
            if choice == 'n' and len(txs) == 5: page += 1
            elif choice == 'p' and page > 0: page -= 1
            elif choice == 'b': break

    def apply_interest(self):
        Utils.display_header("MONTHLY INTEREST")
        if self.user['account_type'] != "Savings":
            print(Fore.RED + "Interest only applicable for Savings accounts.")
            input("\nPress Enter...")
            return

        current_month = datetime.now().strftime("%Y-%m")
        conn = db.get_connection()
        already_paid = conn.execute('''
            SELECT id FROM transactions 
            WHERE account_number = ? AND transaction_type = 'Interest Credit' 
            AND timestamp LIKE ?
        ''', (self.user['account_number'], f"{current_month}%")).fetchone()

        if already_paid:
            print(Fore.YELLOW + "Interest already applied for this month.")
        else:
            interest = self.user['balance'] * 0.04
            new_bal = self.user['balance'] + interest
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET balance = ? WHERE account_number = ?", 
                           (new_bal, self.user['account_number']))
            cursor.execute('''
                INSERT INTO transactions (account_number, transaction_type, amount, balance_after)
                VALUES (?, 'Interest Credit', ?, ?)
            ''', (self.user['account_number'], interest, new_bal))
            conn.commit()
            self.refresh_user()
            print(Fore.GREEN + f"Interest of {Utils.format_currency(interest)} (4%) credited.")
        
        conn.close()
        input("\nPress Enter...")

    def change_password(self):
        Utils.display_header("CHANGE PASSWORD")
        old_pw = input("Current Password: ")
        if bcrypt.checkpw(old_pw.encode('utf-8'), self.user['password_hash'].encode('utf-8')):
            new_pw = Utils.get_input("New Password", Utils.validate_password, "Password too weak")
            hashed_pw = bcrypt.hashpw(new_pw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            conn = db.get_connection()
            conn.execute("UPDATE users SET password_hash = ? WHERE account_number = ?", 
                         (hashed_pw, self.user['account_number']))
            conn.commit()
            conn.close()
            print(Fore.GREEN + "Password updated successfully.")
        else:
            print(Fore.RED + "Incorrect current password.")
        input("\nPress Enter...")

    def delete_account(self):
        Utils.display_header("DELETE ACCOUNT")
        print(Fore.RED + "WARNING: This action is permanent (Soft Delete).")
        if self.user['balance'] > 0:
            print(Fore.RED + f"Cannot delete account with balance > 0. Current: {Utils.format_currency(self.user['balance'])}")
            input("\nPress Enter...")
            return False

        confirm = input("Type 'DELETE' to confirm: ")
        if confirm == 'DELETE':
            pw = input("Enter password to confirm: ")
            if bcrypt.checkpw(pw.encode('utf-8'), self.user['password_hash'].encode('utf-8')):
                conn = db.get_connection()
                conn.execute("UPDATE users SET is_active = 0 WHERE account_number = ?", (self.user['account_number'],))
                conn.commit()
                conn.close()
                print(Fore.GREEN + "Account deactivated successfully.")
                time.sleep(2)
                return True
        print(Fore.RED + "Deletion cancelled or invalid credentials.")
        input("\nPress Enter...")
        return False
