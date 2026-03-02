                                                                                                                                                     # Created By Manthan Vinzuda....
import tkinter as tk
from tkinter import messagebox
import math

class ScientificCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Scientific Calculator")
        self.root.geometry("400x600")
        self.root.resizable(False, False)
        
        # Color Palette
        self.bg_color = "#2c3e50"
        self.display_bg = "#ecf0f1"
        self.btn_color = "#34495e"
        self.btn_text = "#ffffff"
        self.accent_color = "#e67e22"
        self.equal_color = "#27ae60"

        self.root.configure(bg=self.bg_color)

        # Expression storage
        self.expression = ""
        self.input_text = tk.StringVar()

        self._create_widgets()

    def _create_widgets(self):
        """Creates the display and buttons."""
        # Display Screen
        display_frame = tk.Frame(self.root, bg=self.bg_color, pady=20)
        display_frame.pack(expand=True, fill="both")

        display_entry = tk.Entry(
            display_frame, 
            textvariable=self.input_text, 
            font=("Arial", 24, "bold"), 
            bg=self.display_bg, 
            fg="#2c3e50", 
            bd=10, 
            insertwidth=4, 
            justify='right'
        )
        display_entry.pack(expand=True, fill="both", padx=10)

        # Buttons Frame
        buttons_frame = tk.Frame(self.root, bg=self.bg_color)
        buttons_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Button definitions (Text, Row, Col, Command_Type)
        # Command Types: 'num' (append), 'func' (math function), 'eval' (calculate), 'clear' (reset)
        btns = [
            ('C', 0, 0, 'clear'), ('DEL', 0, 1, 'del'), ('(', 0, 2, 'num'), (')', 0, 3, 'num'),
            ('sin', 1, 0, 'func'), ('cos', 1, 1, 'func'), ('tan', 1, 2, 'func'), ('/', 1, 3, 'num'),
            ('log', 2, 0, 'func'), ('ln', 2, 1, 'func'), ('sqrt', 2, 2, 'func'), ('*', 2, 3, 'num'),
            ('7', 3, 0, 'num'), ('8', 3, 1, 'num'), ('9', 3, 2, 'num'), ('-', 3, 3, 'num'),
            ('4', 4, 0, 'num'), ('5', 4, 1, 'num'), ('6', 4, 2, 'num'), ('+', 4, 3, 'num'),
            ('1', 5, 0, 'num'), ('2', 5, 1, 'num'), ('3', 5, 2, 'num'), ('^', 5, 3, 'num'),
            ('pi', 6, 0, 'num'), ('0', 6, 1, 'num'), ('.', 6, 2, 'num'), ('=', 6, 3, 'eval'),
        ]

        for (text, row, col, cmd_type) in btns:
            action = lambda x=text, t=cmd_type: self._on_button_click(x, t)
            
            # Styling logic
            b_color = self.btn_color
            if text == '=': b_color = self.equal_color
            elif text in ['C', 'DEL']: b_color = self.accent_color
            
            button = tk.Button(
                buttons_frame, text=text, width=5, height=2, 
                font=("Arial", 14, "bold"), bg=b_color, fg=self.btn_text,
                command=action, relief="flat", activebackground="#95a5a6"
            )
            button.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

        # Configure grid weights
        for i in range(7):
            buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(4):
            buttons_frame.grid_columnconfigure(i, weight=1)

    def _on_button_click(self, char, type):
        if type == 'num':
            if char == 'pi':
                self.expression += str(math.pi)
            elif char == '^':
                self.expression += '**'
            else:
                self.expression += str(char)
            self.input_text.set(self.expression)

        elif type == 'clear':
            self.expression = ""
            self.input_text.set("")

        elif type == 'del':
            self.expression = self.expression[:-1]
            self.input_text.set(self.expression)

        elif type == 'func':
            # Wrap current expression in a function
            if self.expression == "":
                # If empty, just set the function name as a hint or wait for input
                pass 
            
            try:
                val = float(eval(self.expression)) if self.expression else 0
                if char == 'sin': res = math.sin(math.radians(val))
                elif char == 'cos': res = math.cos(math.radians(val))
                elif char == 'tan': res = math.tan(math.radians(val))
                elif char == 'log': res = math.log10(val)
                elif char == 'ln': res = math.log(val)
                elif char == 'sqrt': res = math.sqrt(val)
                
                self.expression = str(res)
                self.input_text.set(self.expression)
            except Exception as e:
                messagebox.showerror("Error", "Invalid Input for function")
                self.expression = ""
                self.input_text.set("")

        elif type == 'eval':
            try:
                # Basic string evaluation using eval() safely for math
                # Note: In a production app, use a proper parser for security.
                result = str(eval(self.expression))
                self.input_text.set(result)
                self.expression = result
            except ZeroDivisionError:
                messagebox.showerror("Error", "Cannot divide by zero")
                self.expression = ""
                self.input_text.set("")
            except Exception:
                messagebox.showerror("Error", "Invalid Expression")
                self.expression = ""
                self.input_text.set("")

if __name__ == "__main__":
    root = tk.Tk()
    calc = ScientificCalculator(root)
    root.mainloop()
