                                                                                                                                                     # Created By Manthan Vinzuda....
# This Game Created By Manthan Vinzuda I Lean Also Sudoku Logic 

import tkinter as tk
from tkinter import messagebox, ttk
import random
import time
import sqlite3
import threading
from copy import deepcopy

# --- Database Logic ---
class SudokuDB:
    def __init__(self):
        self.conn = sqlite3.connect("sudoku_records.db")
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                difficulty TEXT,
                time_seconds INTEGER,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def save_record(self, difficulty, time_seconds):
        self.cursor.execute("INSERT INTO leaderboard (difficulty, time_seconds) VALUES (?, ?)", 
                            (difficulty, time_seconds))
        self.conn.commit()

    def get_best_times(self, difficulty):
        self.cursor.execute("SELECT time_seconds FROM leaderboard WHERE difficulty = ? ORDER BY time_seconds ASC LIMIT 5", 
                            (difficulty,))
        return self.cursor.fetchall()

# --- Sudoku Logic (Solver & Generator) ---
class SudokuEngine:
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]

    def is_safe(self, board, row, col, num):
        # Check row
        for x in range(9):
            if board[row][x] == num:
                return False
        # Check col
        for x in range(9):
            if board[x][col] == num:
                return False
        # Check 3x3 box
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True

    def solve(self, board, visual=False, callback=None):
        empty = self.find_empty(board)
        if not empty:
            return True
        row, col = empty

        nums = list(range(1, 10))
        random.shuffle(nums) # Randomize for generation variety

        for i in nums:
            if self.is_safe(board, row, col, i):
                board[row][col] = i
                if callback and visual:
                    callback(row, col, i)
                    time.sleep(0.01) # Small delay for animation effect

                if self.solve(board, visual, callback):
                    return True
                
                board[row][col] = 0
                if callback and visual:
                    callback(row, col, 0)
        return False

    def find_empty(self, board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    return (i, j)
        return None

    def generate_puzzle(self, difficulty):
        # 1. Start with empty board
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        # 2. Solve it to get a full valid board
        self.solve(self.board)
        
        # 3. Remove digits based on difficulty
        # Easy: ~40 clues (remove 41)
        # Medium: ~30 clues (remove 51)
        # Hard: ~20 clues (remove 61)
        remove_count = {"Easy": 41, "Medium": 51, "Hard": 61}[difficulty]
        
        puzzle = deepcopy(self.board)
        attempts = remove_count
        while attempts > 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            while puzzle[row][col] == 0:
                row = random.randint(0, 8)
                col = random.randint(0, 8)
            
            puzzle[row][col] = 0
            attempts -= 1
            
        return puzzle, self.board

# --- UI Components ---
class SudokuUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Master Pro")
        self.root.geometry("750x850")
        self.root.configure(bg="#f0f2f5")
        
        self.db = SudokuDB()
        self.engine = SudokuEngine()
        
        # Game State
        self.difficulty = tk.StringVar(value="Medium")
        self.start_time = None
        self.elapsed_time = 0
        self.timer_running = False
        self.mistakes = 0
        self.max_mistakes = 3
        self.is_dark_mode = False
        
        self.current_puzzle = []
        self.solution = []
        self.initial_board = [] # To track pre-filled cells
        self.cells = [[None for _ in range(9)] for _ in range(9)]
        self.selected_cell = None
        
        self.setup_styles()
        self.create_widgets()
        self.new_game()

    def setup_styles(self):
        self.colors = {
            "bg": "#f0f2f5",
            "fg": "#1c1e21",
            "grid_bg": "#ffffff",
            "cell_border": "#dee2e6",
            "box_border": "#343a40",
            "selected": "#e7f3ff",
            "highlight": "#f0f7ff",
            "prefilled": "#1c1e21",
            "user_input": "#0064d2",
            "error": "#fa383e",
            "button_primary": "#0064d2",
            "button_secondary": "#e4e6eb"
        }

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.colors.update({
                "bg": "#18191a",
                "fg": "#e4e6eb",
                "grid_bg": "#242526",
                "cell_border": "#3a3b3c",
                "box_border": "#b0b3b8",
                "selected": "#263951",
                "highlight": "#1c2a3a",
                "prefilled": "#e4e6eb",
                "user_input": "#45bd62",
                "error": "#f3425f"
            })
        else:
            self.setup_styles()
        
        self.root.configure(bg=self.colors["bg"])
        self.header.configure(bg=self.colors["bg"])
        self.main_container.configure(bg=self.colors["bg"])
        self.refresh_grid_ui()

    def create_widgets(self):
        # Header
        self.header = tk.Frame(self.root, bg=self.colors["bg"], pady=20)
        self.header.pack(fill="x")
        
        title_lbl = tk.Label(self.header, text="Sudoku Master", font=("Helvetica", 28, "bold"), 
                             bg=self.colors["bg"], fg="#0064d2")
        title_lbl.pack()
        
        # Stats Bar
        self.stats_bar = tk.Frame(self.root, bg=self.colors["bg"])
        self.stats_bar.pack(pady=10)
        
        self.timer_lbl = tk.Label(self.stats_bar, text="Time: 00:00", font=("Consolas", 14), 
                                  bg=self.colors["bg"], fg=self.colors["fg"])
        self.timer_lbl.pack(side="left", padx=20)
        
        self.mistake_lbl = tk.Label(self.stats_bar, text=f"Mistakes: 0/{self.max_mistakes}", 
                                    font=("Helvetica", 12), bg=self.colors["bg"], fg=self.colors["error"])
        self.mistake_lbl.pack(side="left", padx=20)

        # Main Board Area
        self.main_container = tk.Frame(self.root, bg=self.colors["bg"])
        self.main_container.pack(expand=True)
        
        self.grid_frame = tk.Frame(self.main_container, bg=self.colors["box_border"], bd=2)
        self.grid_frame.pack(padx=20, pady=20)
        
        for r in range(9):
            for c in range(9):
                # Calculate outer box borders
                padding_x = (1, 1)
                padding_y = (1, 1)
                if c % 3 == 0 and c != 0: padding_x = (3, 1)
                if r % 3 == 0 and r != 0: padding_y = (3, 1)
                
                cell_container = tk.Frame(self.grid_frame, bg=self.colors["cell_border"])
                cell_container.grid(row=r, column=c, padx=padding_x, pady=padding_y, sticky="nsew")
                
                cell = tk.Label(cell_container, text="", font=("Helvetica", 18), width=3, height=1,
                               bg=self.colors["grid_bg"], fg=self.colors["fg"], cursor="hand2")
                cell.pack(expand=True, fill="both")
                cell.bind("<Button-1>", lambda e, r=r, c=c: self.select_cell(r, c))
                self.cells[r][c] = cell

        # Control Panel
        self.controls = tk.Frame(self.root, bg=self.colors["bg"], pady=20)
        self.controls.pack(fill="x")
        
        btn_config = {"font": ("Helvetica", 10, "bold"), "width": 10, "pady": 8}
        
        tk.Button(self.controls, text="New Game", command=self.new_game, **btn_config, bg="#0064d2", fg="white").pack(side="left", padx=5, expand=True)
        tk.Button(self.controls, text="Hint", command=self.give_hint, **btn_config).pack(side="left", padx=5, expand=True)
        tk.Button(self.controls, text="Solve", command=self.visual_solve, **btn_config).pack(side="left", padx=5, expand=True)
        tk.Button(self.controls, text="Check", command=self.check_win, **btn_config).pack(side="left", padx=5, expand=True)
        
        # Difficulty Selector
        diff_frame = tk.Frame(self.root, bg=self.colors["bg"])
        diff_frame.pack(pady=10)
        for diff in ["Easy", "Medium", "Hard"]:
            tk.Radiobutton(diff_frame, text=diff, variable=self.difficulty, value=diff, 
                           bg=self.colors["bg"], font=("Helvetica", 10)).pack(side="left", padx=10)
        
        # Theme Toggle
        tk.Button(self.root, text="Toggle Dark Mode", command=self.toggle_theme, font=("Helvetica", 8)).pack(pady=5)
        
        self.root.bind("<Key>", self.handle_keypress)

    def new_game(self):
        self.mistakes = 0
        self.elapsed_time = 0
        self.timer_running = True
        self.start_time = time.time()
        self.update_timer()
        self.update_mistake_ui()
        
        self.current_puzzle, self.solution = self.engine.generate_puzzle(self.difficulty.get())
        self.initial_board = deepcopy(self.current_puzzle)
        
        self.refresh_grid_ui()
        self.select_cell(4, 4)

    def refresh_grid_ui(self):
        for r in range(9):
            for c in range(9):
                val = self.current_puzzle[r][c]
                self.cells[r][c].config(text=str(val) if val != 0 else "", bg=self.colors["grid_bg"])
                if self.initial_board[r][c] != 0:
                    self.cells[r][c].config(fg=self.colors["prefilled"], font=("Helvetica", 18, "bold"))
                else:
                    self.cells[r][c].config(fg=self.colors["user_input"], font=("Helvetica", 18))
        self.highlight_duplicates()

    def select_cell(self, r, c):
        self.selected_cell = (r, c)
        # Reset all backgrounds
        for row in range(9):
            for col in range(9):
                self.cells[row][col].config(bg=self.colors["grid_bg"])
        
        # Highlight row and column
        for i in range(9):
            self.cells[r][i].config(bg=self.colors["highlight"])
            self.cells[i][c].config(bg=self.colors["highlight"])
            
        # Highlight 3x3 box
        sr, sc = r - r % 3, c - c % 3
        for i in range(3):
            for j in range(3):
                self.cells[sr+i][sc+j].config(bg=self.colors["highlight"])
                
        # Highlight selected
        self.cells[r][c].config(bg=self.colors["selected"])
        self.highlight_duplicates()

    def handle_keypress(self, event):
        if not self.selected_cell: return
        r, c = self.selected_cell
        
        if self.initial_board[r][c] != 0: return # Locked cell
        
        if event.char in "123456789":
            val = int(event.char)
            if self.solution[r][c] == val:
                self.current_puzzle[r][c] = val
                self.cells[r][c].config(text=str(val))
                self.highlight_duplicates()
                if self.check_win(silent=True):
                    self.game_won()
            else:
                self.mistakes += 1
                self.update_mistake_ui()
                if self.mistakes >= self.max_mistakes:
                    self.game_over()
        elif event.keysym == "BackSpace" or event.char == "0":
            self.current_puzzle[r][c] = 0
            self.cells[r][c].config(text="")
            self.highlight_duplicates()
        elif event.keysym in ["Up", "Down", "Left", "Right"]:
            dr, dc = {"Up":(-1,0), "Down":(1,0), "Left":(0,-1), "Right":(0,1)}[event.keysym]
            nr, nc = (r + dr) % 9, (c + dc) % 9
            self.select_cell(nr, nc)

    def highlight_duplicates(self):
        # Check rows, cols, and boxes for duplicates in the current puzzle
        for r in range(9):
            for c in range(9):
                val = self.current_puzzle[r][c]
                if val == 0: continue
                
                is_dup = False
                # Row
                if self.current_puzzle[r].count(val) > 1: is_dup = True
                # Col
                if [self.current_puzzle[i][c] for i in range(9)].count(val) > 1: is_dup = True
                # Box
                sr, sc = r - r % 3, c - c % 3
                box = []
                for i in range(3):
                    for j in range(3): box.append(self.current_puzzle[sr+i][sc+j])
                if box.count(val) > 1: is_dup = True
                
                if is_dup:
                    self.cells[r][c].config(fg=self.colors["error"])
                else:
                    if self.initial_board[r][c] != 0:
                        self.cells[r][c].config(fg=self.colors["prefilled"])
                    else:
                        self.cells[r][c].config(fg=self.colors["user_input"])

    def give_hint(self):
        if not self.selected_cell: return
        r, c = self.selected_cell
        if self.current_puzzle[r][c] == 0:
            self.current_puzzle[r][c] = self.solution[r][c]
            self.cells[r][c].config(text=str(self.solution[r][c]))
            self.highlight_duplicates()

    def visual_solve(self):
        self.timer_running = False
        def update_ui(r, c, val):
            self.root.after(0, lambda: self.cells[r][c].config(
                text=str(val) if val != 0 else "", 
                fg=self.colors["user_input"] if val != 0 else self.colors["fg"]
            ))
        
        # Create a worker thread for the backtracking solver to keep UI responsive
        def solve_task():
            temp_board = deepcopy(self.initial_board)
            self.engine.solve(temp_board, visual=True, callback=update_ui)
            self.current_puzzle = temp_board
            self.root.after(0, lambda: messagebox.showinfo("Solver", "Puzzle Solved!"))

        threading.Thread(target=solve_task, daemon=True).start()

    def update_timer(self):
        if self.timer_running:
            self.elapsed_time = int(time.time() - self.start_time)
            mins, secs = divmod(self.elapsed_time, 60)
            self.timer_lbl.config(text=f"Time: {mins:02d}:{secs:02d}")
            self.root.after(1000, self.update_timer)

    def update_mistake_ui(self):
        self.mistake_lbl.config(text=f"Mistakes: {self.mistakes}/{self.max_mistakes}")

    def check_win(self, silent=False):
        for r in range(9):
            for c in range(9):
                if self.current_puzzle[r][c] != self.solution[r][c]:
                    if not silent: messagebox.showwarning("Check", "The board is incomplete or has errors.")
                    return False
        if not silent: self.game_won()
        return True

    def game_won(self):
        self.timer_running = False
        self.db.save_record(self.difficulty.get(), self.elapsed_time)
        best = self.db.get_best_times(self.difficulty.get())[0][0]
        messagebox.showinfo("Victory!", f"Congratulations! You solved it in {self.elapsed_time}s.\nBest time for {self.difficulty.get()}: {best}s")
        self.new_game()

    def game_over(self):
        self.timer_running = False
        messagebox.showerror("Game Over", "You've reached the maximum number of mistakes.")
        self.new_game()

if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuUI(root)
    
    # Center Window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()
