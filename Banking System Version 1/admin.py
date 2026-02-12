from database import db
from utils import Utils, Fore, Style
from tabulate import tabulate

class AdminPortal:
    """Handles admin specific functionalities."""

    def __init__(self):
        self.admin_id = "admin"
        self.admin_pass = "admin123"

    def login(self):
        Utils.display_header("ADMIN LOGIN")
        aid = input("Admin ID: ")
        apw = input("Password: ")
        if aid == self.admin_id and apw == self.admin_pass:
            Utils.loader("Accessing Secure Vault")
            self.menu()
        else:
            print(Fore.RED + "Access Denied.")
            time.sleep(1)

    def menu(self):
        while True:
            Utils.display_header("ADMIN CONTROL PANEL")
            print("1. View All Accounts")
            print("2. Search Account")
            print("3. Toggle Freeze Status")
            print("4. Delete Account (Admin)")
            print("5. Bank Statistics")
            print("6. All Transactions")
            print("0. Logout")
            
            choice = input("\nChoice: ")
            if choice == '1': self.view_all()
            elif choice == '2': self.search()
            elif choice == '3': self.toggle_freeze()
            elif choice == '4': self.admin_delete()
            elif choice == '5': self.stats()
            elif choice == '6': self.all_txs()
            elif choice == '0': break

    def view_all(self):
        conn = db.get_connection()
        users = conn.execute("SELECT account_number, full_name, balance, is_active, is_frozen FROM users").fetchall()
        conn.close()
        headers = ["Acc Num", "Name", "Balance", "Active", "Frozen"]
        rows = [[u[0], u[1], Utils.format_currency(u[2]), bool(u[3]), bool(u[4])] for u in users]
        print(tabulate(rows, headers=headers, tablefmt="grid"))
        input("\nPress Enter...")

    def search(self):
        query = input("Enter Account Number or Email to search: ")
        conn = db.get_connection()
        user = conn.execute("SELECT * FROM users WHERE account_number = ? OR email = ?", (query, query)).fetchone()
        conn.close()
        if user:
            print(tabulate([dict(user).items()], tablefmt="fancy_grid"))
        else:
            print(Fore.RED + "User not found.")
        input("\nPress Enter...")

    def toggle_freeze(self):
        acc = input("Enter Account Number: ")
        conn = db.get_connection()
        user = conn.execute("SELECT is_frozen FROM users WHERE account_number = ?", (acc,)).fetchone()
        if user:
            new_status = 0 if user['is_frozen'] else 1
            conn.execute("UPDATE users SET is_frozen = ? WHERE account_number = ?", (new_status, acc))
            conn.commit()
            print(Fore.GREEN + f"Status updated to {'Frozen' if new_status else 'Unfrozen'}.")
        else:
            print(Fore.RED + "Account not found.")
        conn.close()
        input("\nPress Enter...")

    def admin_delete(self):
        acc = input("Enter Account Number to SOFT DELETE: ")
        conn = db.get_connection()
        conn.execute("UPDATE users SET is_active = 0 WHERE account_number = ?", (acc,))
        conn.commit()
        conn.close()
        print(Fore.GREEN + "Account deactivated.")
        input("\nPress Enter...")

    def stats(self):
        conn = db.get_connection()
        total_bal = conn.execute("SELECT SUM(balance) FROM users WHERE is_active = 1").fetchone()[0] or 0
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_txs = conn.execute("SELECT COUNT(*) FROM transactions").fetchone()[0]
        conn.close()
        
        print(Fore.CYAN + f"Total Bank Liquidity: {Utils.format_currency(total_bal)}")
        print(f"Total Registered Users: {total_users}")
        print(f"Total Transactions Logged: {total_txs}")
        input("\nPress Enter...")

    def all_txs(self):
        conn = db.get_connection()
        txs = conn.execute("SELECT * FROM transactions ORDER BY timestamp DESC LIMIT 20").fetchall()
        conn.close()
        print(tabulate(txs, headers="keys", tablefmt="simple"))
        input("\nPress Enter...")
