
import tkinter as tk
from tkinter import messagebox
import random

class SudokuLogic:
    """Perfect Logic for Generating and Solving Sudoku"""
    def __init__(self):
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = [[0 for _ in range(9)] for _ in range(9)]

    def is_valid(self, board, row, col, num):
        # Check row and column
        for x in range(9):
            if board[row][x] == num or board[x][col] == num:
                return False
        # Check 3x3 box
        start_row, start_col = row - row % 3, col - col % 3
        for i in range(3):
            for j in range(3):
                if board[i + start_row][j + start_col] == num:
                    return False
        return True

    def solve(self, board):
        """Backtracking algorithm to solve the board"""
        for row in range(9):
            for col in range(9):
                if board[row][col] == 0:
                    numbers = list(range(1, 10))
                    random.shuffle(numbers) # Shuffle for random generation
                    for num in numbers:
                        if self.is_valid(board, row, col, num):
                            board[row][col] = num
                            if self.solve(board):
                                return True
                            board[row][col] = 0
                    return False
        return True

    def generate_puzzle(self, difficulty):
        """Generates a new puzzle based on difficulty"""
        self.board = [[0 for _ in range(9)] for _ in range(9)]
        self.solve(self.board) # Fill a complete valid board
        
        # Save the solution
        self.solution = [row[:] for row in self.board]
        
        # Determine how many cells to remove
        if difficulty == "Easy":
            cells_to_remove = 30
        elif difficulty == "Medium":
            cells_to_remove = 45
        else: # Hard
            cells_to_remove = 55
            
        # Remove numbers to create the puzzle
        count = cells_to_remove
        while count > 0:
            row = random.randint(0, 8)
            col = random.randint(0, 8)
            if self.board[row][col] != 0:
                self.board[row][col] = 0
                count -= 1

class SudokuUI(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.logic = SudokuLogic()
        self.puzzle = [[0]*9 for _ in range(9)]
        self.original = [[0]*9 for _ in range(9)]
        self.row, self.col = -1, -1
        
        self.parent.title("Premium Sudoku")
        self.pack(fill=tk.BOTH, expand=1)
        
        self.setup_ui()
        self.start_new_game("Medium") # Default start

    def setup_ui(self):
        """Neat and Clean UI Setup"""
        # Top Frame for Buttons
        top_frame = tk.Frame(self, bg="#f0f0f0", pady=10)
        top_frame.pack(fill=tk.X, side=tk.TOP)

        btn_easy = tk.Button(top_frame, text="Easy", font=("Arial", 10, "bold"), bg="#d4edda", command=lambda: self.start_new_game("Easy"))
        btn_easy.pack(side=tk.LEFT, padx=10)
        
        btn_medium = tk.Button(top_frame, text="Medium", font=("Arial", 10, "bold"), bg="#fff3cd", command=lambda: self.start_new_game("Medium"))
        btn_medium.pack(side=tk.LEFT, padx=10)
        
        btn_hard = tk.Button(top_frame, text="Hard", font=("Arial", 10, "bold"), bg="#f8d7da", command=lambda: self.start_new_game("Hard"))
        btn_hard.pack(side=tk.LEFT, padx=10)
        
        btn_solve = tk.Button(top_frame, text="Auto-Solve", font=("Arial", 10, "bold"), bg="#cce5ff", command=self.auto_solve)
        btn_solve.pack(side=tk.RIGHT, padx=10)

        # Main Canvas for Grid
        self.canvas = tk.Canvas(self, width=450, height=450, bg="white")
        self.canvas.pack(fill=tk.BOTH, side=tk.TOP, pady=10)
        
        self.canvas.bind("<Button-1>", self.cell_clicked)
        self.canvas.bind("<Key>", self.key_pressed)

    def start_new_game(self, difficulty):
        self.logic.generate_puzzle(difficulty)
        self.original = [row[:] for row in self.logic.board]
        self.puzzle = [row[:] for row in self.logic.board]
        self.row, self.col = -1, -1
        self.draw_board()
        self.canvas.focus_set()

    def draw_board(self):
        self.canvas.delete("all")
        self.draw_grid()
        self.draw_numbers()

    def draw_grid(self):
        for i in range(10):
            color = "#333333" if i % 3 == 0 else "#cccccc"
            width = 3 if i % 3 == 0 else 1
            self.canvas.create_line(i * 50, 0, i * 50, 450, fill=color, width=width)
            self.canvas.create_line(0, i * 50, 450, i * 50, fill=color, width=width)

    def draw_numbers(self):
        self.canvas.delete("numbers")
        for i in range(9):
            for j in range(9):
                val = self.puzzle[i][j]
                if val != 0:
                    x, y = j * 50 + 25, i * 50 + 25
                    color = "black" if self.original[i][j] != 0 else "#0056b3"
                    self.canvas.create_text(x, y, text=val, tags="numbers", fill=color, font=("Helvetica", 18, "bold"))

    def draw_cursor(self):
        self.canvas.delete("cursor")
        if self.row >= 0 and self.col >= 0:
            x0, y0 = self.col * 50 + 2, self.row * 50 + 2
            self.canvas.create_rectangle(x0, y0, x0 + 46, y0 + 46, outline="#ff6b6b", width=3, tags="cursor")

    def cell_clicked(self, event):
        x, y = event.x, event.y
        if 0 <= x < 450 and 0 <= y < 450:
            self.col, self.row = x // 50, y // 50
            self.draw_cursor()

    def key_pressed(self, event):
        if self.row >= 0 and self.col >= 0 and self.original[self.row][self.col] == 0:
            if event.char in "123456789":
                num = int(event.char)
                # Check validity against current puzzle state
                temp_val = self.puzzle[self.row][self.col]
                self.puzzle[self.row][self.col] = 0 # Temp remove to check validity
                
                if self.logic.is_valid(self.puzzle, self.row, self.col, num):
                    self.puzzle[self.row][self.col] = num
                    self.draw_board()
                    self.draw_cursor()
                    self.check_win()
                else:
                    self.puzzle[self.row][self.col] = temp_val # Restore
                    messagebox.showwarning("Oops!", f"Tame {num} ahiya na muki shako! (Invalid Move)")
            
            elif event.keysym in ["BackSpace", "Delete"]:
                self.puzzle[self.row][self.col] = 0
                self.draw_board()
                self.draw_cursor()

    def auto_solve(self):
        """Solves the puzzle for the user"""
        self.puzzle = [row[:] for row in self.logic.solution]
        self.draw_board()
        messagebox.showinfo("Solved", "Computer e game solve kari didhi chhe! (Computer has solved the game!)")

    def check_win(self):
        for r in range(9):
            for c in range(9):
                if self.puzzle[r][c] == 0:
                    return
        messagebox.showinfo("Superb!", "Congratulations! Tame game jiti gaya! (You won!)")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("450x520")
    root.resizable(False, False)
    root.configure(bg="#f0f0f0")
    app = SudokuUI(root)
    root.mainloop()
