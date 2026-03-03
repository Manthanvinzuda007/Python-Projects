# By - Manthan Vinzuda 
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import bcrypt
import random
import datetime
import csv
import os
import qrcode
from PIL import Image, ImageTk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import io

# --- Database Layer ---
class Database:
    def __init__(self):
        self.conn = sqlite3.connect('banking_system_pro.db')
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        # Users Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                dob TEXT,
                phone TEXT,
                email TEXT UNIQUE,
                address TEXT,
                password_hash TEXT NOT NULL,
                account_number TEXT UNIQUE,
                ifsc_code TEXT,
                account_type TEXT,
                balance REAL DEFAULT 0.0,
                is_active INTEGER DEFAULT 1,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Transactions Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_number TEXT,
                type TEXT,
                amount REAL,
                balance_after REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # QR Tokens Table (For Single Use Security)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS qr_tokens (
                token TEXT PRIMARY KEY,
                account_number TEXT,
                type TEXT,
                amount REAL,
                is_used INTEGER DEFAULT 0,
                expiry TIMESTAMP
            )
        ''')
        
        # Default Admin
        self.cursor.execute("SELECT * FROM users WHERE email = 'admin@bank.com'")
        if not self.cursor.fetchone():
            hashed = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            self.cursor.execute('''
                INSERT INTO users (full_name, email, password_hash, account_number, is_admin, balance)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', ("System Admin", "admin@bank.com", hashed, "ADMIN001", 1, 0.0))
            
        self.conn.commit()

    def query(self, sql, params=()):
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def execute(self, sql, params=()):
        try:
            self.cursor.execute(sql, params)
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"DB Error: {e}")
            return False

# --- UI Theme ---
COLORS = {
    "primary": "#0f172a",   # Dark Slate
    "secondary": "#334155", 
    "accent": "#3b82f6",    # Blue
    "bg": "#f8fafc",        
    "white": "#ffffff",
    "text": "#1e293b",
    "danger": "#ef4444",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "light_border": "#e2e8f0"
}

class BankingApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Nexus Pro Banking - Next Gen")
        self.geometry("1200x800")
        self.configure(bg=COLORS["bg"])
        
        self.db = Database()
        self.current_user = None
        self.active_token = None
        
        self.container = tk.Frame(self, bg=COLORS["bg"])
        self.container.pack(fill="both", expand=True)
        
        self.show_login_screen()

    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # --- Auth Screens ---
    def show_login_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.container, bg=COLORS["white"], padx=50, pady=50, highlightthickness=1, highlightbackground=COLORS["light_border"])
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(frame, text="N E X U S", font=("Inter", 28, "bold"), fg=COLORS["primary"], bg="white").pack()
        tk.Label(frame, text="Digital Banking Solution", font=("Inter", 10), fg="#64748b", bg="white").pack(pady=(0, 30))
        
        tk.Label(frame, text="Email Address", bg="white", font=("Inter", 9, "bold")).pack(anchor="w")
        e_mail = tk.Entry(frame, width=35, font=("Inter", 11), bd=0, highlightbackground=COLORS["light_border"], highlightthickness=1)
        e_mail.pack(pady=(5, 15), ipady=8)
        
        tk.Label(frame, text="Password", bg="white", font=("Inter", 9, "bold")).pack(anchor="w")
        e_pass = tk.Entry(frame, width=35, font=("Inter", 11), bd=0, highlightbackground=COLORS["light_border"], highlightthickness=1, show="*")
        e_pass.pack(pady=(5, 25), ipady=8)
        
        def do_login():
            user_data = self.db.query("SELECT * FROM users WHERE email = ? AND is_active = 1", (e_mail.get(),))
            if user_data and bcrypt.checkpw(e_pass.get().encode('utf-8'), user_data[0][6]):
                u = user_data[0]
                self.current_user = {
                    "id": u[0], "name": u[1], "email": u[4], 
                    "acc_no": u[7], "type": u[9], "balance": u[10], "is_admin": u[12]
                }
                self.show_dashboard()
            else:
                messagebox.showerror("Error", "Invalid login details or frozen account.")

        tk.Button(frame, text="Sign In", bg=COLORS["accent"], fg="white", font=("Inter", 11, "bold"), 
                  command=do_login, bd=0, cursor="hand2", width=30).pack(ipady=8)
        
        tk.Button(frame, text="Don't have an account? Register", fg=COLORS["accent"], bg="white", bd=0, 
                  command=self.show_registration, font=("Inter", 9)).pack(pady=10)

    def show_registration(self):
        self.clear_screen()
        main_reg = tk.Frame(self.container, bg=COLORS["bg"])
        main_reg.pack(fill="both", expand=True)
        
        inner = tk.Frame(main_reg, bg="white", padx=40, pady=30, highlightthickness=1, highlightbackground=COLORS["light_border"])
        inner.place(relx=0.5, rely=0.5, anchor="center")
        
        tk.Label(inner, text="Create Account", font=("Inter", 20, "bold"), bg="white").grid(row=0, columnspan=2, pady=20)
        
        labels = ["Full Name", "Email", "Phone", "Initial Deposit", "Password"]
        entries = {}
        for i, text in enumerate(labels):
            tk.Label(inner, text=text, bg="white", font=("Inter", 9)).grid(row=i+1, column=0, sticky="w", pady=5)
            e = tk.Entry(inner, width=30, font=("Inter", 10), bd=1, highlightthickness=0)
            if text == "Password": e.config(show="*")
            e.grid(row=i+1, column=1, pady=5, padx=10, ipady=3)
            entries[text] = e

        def register():
            try:
                name, email, phone, dep, pwd = [entries[k].get() for k in labels]
                if float(dep) < 1000: return messagebox.showwarning("Min Balance", "Minimum ₹1000 required")
                
                acc_no = f"NEX{random.randint(100000, 999999)}"
                hashed = bcrypt.hashpw(pwd.encode('utf-8'), bcrypt.gensalt())
                
                if self.db.execute("INSERT INTO users (full_name, email, phone, balance, password_hash, account_number, account_type) VALUES (?,?,?,?,?,?,?)",
                                   (name, email, phone, float(dep), hashed, acc_no, "Savings")):
                    self.db.execute("INSERT INTO transactions (account_number, type, amount, balance_after) VALUES (?,?,?,?)",
                                    (acc_no, "Initial", float(dep), float(dep)))
                    messagebox.showinfo("Success", f"Account Created!\nAcc No: {acc_no}")
                    self.show_login_screen()
            except: messagebox.showerror("Error", "Invalid inputs")

        tk.Button(inner, text="Register Now", bg=COLORS["success"], fg="white", font=("Inter", 10, "bold"), width=25, command=register, bd=0).grid(row=7, columnspan=2, pady=20, ipady=8)
        tk.Button(inner, text="Back to Login", command=self.show_login_screen, bg="white", bd=0, fg=COLORS["secondary"]).grid(row=8, columnspan=2)

    # --- Main Dashboard ---
    def show_dashboard(self):
        self.clear_screen()
        
        sidebar = tk.Frame(self.container, bg=COLORS["primary"], width=240)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        tk.Label(sidebar, text="NEXUS PRO", font=("Inter", 18, "bold"), fg="white", bg=COLORS["primary"], pady=30).pack()
        
        btns = [
            ("Dashboard", self.render_home),
            ("QR Transactions", self.show_qr_portal),
            ("Deposit Cash", self.show_deposit),
            ("Withdraw Cash", self.show_withdraw),
            ("Statements", self.export_csv),
            ("Logout", self.show_login_screen)
        ]
        
        for text, cmd in btns:
            bg_c = COLORS["primary"]
            if text == "Logout": bg_c = COLORS["danger"]
            tk.Button(sidebar, text=text, font=("Inter", 10), bg=bg_c, fg="white", bd=0, anchor="w", 
                      padx=30, pady=15, cursor="hand2", command=cmd).pack(fill="x")
        
        self.main_content = tk.Frame(self.container, bg=COLORS["bg"], padx=40, pady=30)
        self.main_content.pack(side="right", fill="both", expand=True)
        self.render_home()

    def render_home(self):
        u = self.db.query("SELECT balance FROM users WHERE id=?", (self.current_user["id"],))[0]
        self.current_user["balance"] = u[0]
        
        for w in self.main_content.winfo_children(): w.destroy()
        
        tk.Label(self.main_content, text=f"Welcome back, {self.current_user['name']}", font=("Inter", 22, "bold"), bg=COLORS["bg"], fg=COLORS["primary"]).pack(anchor="w")
        
        # Balance Card
        card = tk.Frame(self.main_content, bg=COLORS["accent"], padx=35, pady=35)
        card.pack(fill="x", pady=25)
        tk.Label(card, text="TOTAL ACCOUNT BALANCE", font=("Inter", 9, "bold"), bg=COLORS["accent"], fg="white").pack(anchor="w")
        tk.Label(card, text=f"₹ {self.current_user['balance']:,.2f}", font=("Inter", 34, "bold"), bg=COLORS["accent"], fg="white").pack(anchor="w", pady=5)
        tk.Label(card, text=f"Account No: {self.current_user['acc_no']} | IFSC: NEXS0001234", font=("Inter", 9), bg=COLORS["accent"], fg="white").pack(anchor="w", pady=(10,0))
        
        bottom = tk.Frame(self.main_content, bg=COLORS["bg"])
        bottom.pack(fill="both", expand=True)
        
        hist = tk.LabelFrame(bottom, text="Recent Transactions", bg="white", font=("Inter", 10, "bold"), padx=15, pady=15, highlightthickness=1, highlightbackground=COLORS["light_border"])
        hist.pack(side="left", fill="both", expand=True)
        
        tree = ttk.Treeview(hist, columns=("1","2","3"), show="headings", height=10)
        tree.heading("1", text="Type")
        tree.heading("2", text="Amount")
        tree.heading("3", text="Date & Time")
        tree.column("1", width=120); tree.column("2", width=120); tree.column("3", width=180)
        
        txs = self.db.query("SELECT type, amount, timestamp FROM transactions WHERE account_number=? ORDER BY id DESC LIMIT 10", (self.current_user["acc_no"],))
        for t in txs: tree.insert("", "end", values=t)
        tree.pack(fill="both", expand=True)

    # --- PROFESSIONAL QR PORTAL ---
    def show_qr_portal(self):
        for w in self.main_content.winfo_children(): w.destroy()
        
        tk.Label(self.main_content, text="Secure QR Portal", font=("Inter", 22, "bold"), bg=COLORS["bg"], fg=COLORS["primary"]).pack(anchor="w")
        tk.Label(self.main_content, text="Dynamic QR codes for instant mobile deposits and withdrawals.", bg=COLORS["bg"], fg="#64748b", font=("Inter", 10)).pack(anchor="w", pady=(2, 25))
        
        container = tk.Frame(self.main_content, bg="white", padx=40, pady=40, highlightthickness=1, highlightbackground=COLORS["light_border"])
        container.pack(fill="both", expand=True)
        
        # Left Side: Controls
        left = tk.Frame(container, bg="white")
        left.pack(side="left", fill="both", expand=True)
        
        tk.Label(left, text="Transaction Type", bg="white", font=("Inter", 10, "bold")).pack(anchor="w")
        q_type = ttk.Combobox(left, values=["QR Deposit", "QR Withdraw"], state="readonly", font=("Inter", 11))
        q_type.set("QR Deposit")
        q_type.pack(fill="x", pady=(8, 20), ipady=5)
        
        tk.Label(left, text="Amount to Transfer (₹)", bg="white", font=("Inter", 10, "bold")).pack(anchor="w")
        q_amt = tk.Entry(left, font=("Inter", 14), bd=0, highlightthickness=1, highlightbackground=COLORS["light_border"])
        q_amt.pack(fill="x", pady=(8, 30), ipady=10)
        
        # Right Side: Professional QR Frame
        right = tk.Frame(container, bg="white", padx=20)
        right.pack(side="right", fill="both")
        
        # This frame looks like a professional QR Stand
        qr_card = tk.Frame(right, bg="white", padx=2, pady=2, highlightthickness=2, highlightbackground=COLORS["primary"])
        qr_card.pack()
        
        # Header inside QR card
        tk.Label(qr_card, text="NEXUS PAY", font=("Inter", 10, "bold"), bg=COLORS["primary"], fg="white", pady=8).pack(fill="x")
        
        self.qr_display = tk.Label(qr_card, text="Generate QR\nto begin", bg="white", width=25, height=12, fg="#94a3b8", font=("Inter", 10))
        self.qr_display.pack(padx=20, pady=20)
        
        # Footer inside QR card
        self.qr_footer = tk.Label(qr_card, text="Secure Transaction", font=("Inter", 8), bg="#f8fafc", fg="#64748b", pady=10)
        self.qr_footer.pack(fill="x")

        def generate_professional_qr():
            try:
                amt = float(q_amt.get())
                if amt <= 0: raise ValueError
                if q_type.get() == "QR Withdraw" and amt > self.current_user["balance"]:
                    return messagebox.showerror("Low Balance", "You do not have enough funds.")
                
                token = f"TXN-{random.randint(1000, 9999)}-{self.current_user['acc_no']}-{amt}"
                self.db.execute("INSERT INTO qr_tokens (token, account_number, type, amount) VALUES (?,?,?,?)",
                                (token, self.current_user["acc_no"], q_type.get(), amt))
                
                # Generate Styled QR (Using Brand Colors)
                qr = qrcode.QRCode(version=1, box_size=10, border=1)
                qr.add_data(token)
                qr.make(fit=True)
                # COLORS["primary"] is the dark slate used in bank theme
                img = qr.make_image(fill_color=COLORS["primary"], back_color="white")
                
                img_tk = ImageTk.PhotoImage(img.resize((240, 240), Image.Resampling.LANCZOS))
                self.qr_display.config(image=img_tk, text="")
                self.qr_display.image = img_tk
                
                self.qr_footer.config(text=f"Scan to {q_type.get()} ₹{amt:,.2f}", fg=COLORS["primary"], font=("Inter", 9, "bold"))
                
                sim_btn.config(state="normal", text=f"Scan & Confirm ₹{amt}", bg=COLORS["success"])
                self.active_token = token
                
            except ValueError: messagebox.showerror("Error", "Please enter a valid amount.")

        tk.Button(left, text="Create Secure QR", bg=COLORS["primary"], fg="white", font=("Inter", 11, "bold"), 
                  command=generate_professional_qr, bd=0, cursor="hand2").pack(fill="x", ipady=12)
        
        sim_btn = tk.Button(left, text="Waiting for Input...", bg="#94a3b8", fg="white", font=("Inter", 11, "bold"), 
                           state="disabled", command=lambda: self.simulate_mobile_scan(sim_btn), bd=0, cursor="hand2")
        sim_btn.pack(fill="x", pady=(15, 0), ipady=12)
        
        tk.Label(left, text="* Single-use QR. Code expires after one scan.", fg=COLORS["danger"], bg="white", font=("Inter", 8), pady=15).pack()

    def simulate_mobile_scan(self, btn):
        data = self.db.query("SELECT * FROM qr_tokens WHERE token=? AND is_used=0", (self.active_token,))
        if not data:
            messagebox.showerror("QR Expired", "Aa QR Code ek var vaprai gayo che k expire thai gayo che.")
            return
        
        token_info = data[0]
        acc_no, t_type, amt = token_info[1], token_info[2], token_info[3]
        
        current_bal = self.db.query("SELECT balance FROM users WHERE account_number=?", (acc_no,))[0][0]
        new_bal = (current_bal + amt) if t_type == "QR Deposit" else (current_bal - amt)
            
        # Update
        self.db.execute("UPDATE users SET balance = ? WHERE account_number = ?", (new_bal, acc_no))
        self.db.execute("INSERT INTO transactions (account_number, type, amount, balance_after) VALUES (?,?,?,?)",
                        (acc_no, t_type, amt, new_bal))
        self.db.execute("UPDATE qr_tokens SET is_used = 1 WHERE token = ?", (self.active_token,))
        
        messagebox.showinfo("Transaction Success", f"Mobile Scan Completed!\n{t_type}: ₹{amt}\nNew Balance: ₹{new_bal:,.2f}")
        
        self.qr_display.config(image="", text="TOKEN EXPIRED")
        self.qr_footer.config(text="Transaction Completed", fg=COLORS["success"])
        btn.config(state="disabled", text="Successfully Processed", bg="#94a3b8")
        self.render_home()

    # --- Standard Features ---
    def show_deposit(self):
        amt = self.ask_val("Cash Deposit", "Enter amount to deposit:")
        if amt:
            try:
                a = float(amt)
                new = self.current_user["balance"] + a
                self.db.execute("UPDATE users SET balance=? WHERE id=?", (new, self.current_user["id"]))
                self.db.execute("INSERT INTO transactions (account_number, type, amount, balance_after) VALUES (?,?,?,?)",
                                (self.current_user["acc_no"], "Deposit", a, new))
                messagebox.showinfo("Success", f"Deposited ₹{a}")
                self.render_home()
            except: pass

    def show_withdraw(self):
        amt = self.ask_val("Cash Withdrawal", "Enter amount to withdraw:")
        if amt:
            try:
                a = float(amt)
                if a > self.current_user["balance"]: return messagebox.showerror("Error", "Low Balance")
                new = self.current_user["balance"] - a
                self.db.execute("UPDATE users SET balance=? WHERE id=?", (new, self.current_user["id"]))
                self.db.execute("INSERT INTO transactions (account_number, type, amount, balance_after) VALUES (?,?,?,?)",
                                (self.current_user["acc_no"], "Withdrawal", a, new))
                messagebox.showinfo("Success", f"Withdrawn ₹{a}")
                self.render_home()
            except: pass

    def ask_val(self, title, msg):
        dialog = tk.Toplevel(self)
        dialog.title(title)
        dialog.geometry("350x200")
        dialog.configure(bg="white")
        tk.Label(dialog, text=msg, bg="white", font=("Inter", 10), pady=20).pack()
        e = tk.Entry(dialog, font=("Inter", 12), highlightthickness=1, highlightbackground=COLORS["light_border"], bd=0)
        e.pack(pady=5, padx=30, fill="x", ipady=5)
        e.focus_set()
        res = tk.StringVar()
        def ok(): 
            res.set(e.get())
            dialog.destroy()
        tk.Button(dialog, text="Confirm Transaction", bg=COLORS["primary"], fg="white", font=("Inter", 10, "bold"), command=ok, bd=0).pack(pady=25, padx=30, fill="x", ipady=8)
        self.wait_window(dialog)
        return res.get()

    def export_csv(self):
        data = self.db.query("SELECT type, amount, balance_after, timestamp FROM transactions WHERE account_number=?", (self.current_user["acc_no"],))
        path = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=f"Statement_{self.current_user['acc_no']}")
        if path:
            with open(path, 'w', newline='') as f:
                w = csv.writer(f)
                w.writerow(["Type", "Amount", "Balance After", "Timestamp"])
                w.writerows(data)
            messagebox.showinfo("Success", "Statement exported successfully!")

if __name__ == "__main__":
    app = BankingApp()
    app.mainloop()
                                                                                                                                # Created By Manthan Vinzuda....

