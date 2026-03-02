
# board.py
import random
from tile import Tile

class Board:
    def __init__(self, grid_size, font, sound_mgr):
        self.grid_size = grid_size
        self.tile_size = (450 - 30) // grid_size
        self.font = font
        self.sound = sound_mgr
        self.tiles = []
        self.empty_pos = (grid_size - 1, grid_size - 1)
        self.moves = 0
        self.is_solved = False
        self.generate_board()

    def generate_board(self):
        while True:
            numbers = list(range(1, self.grid_size * self.grid_size)) + [0]
            random.shuffle(numbers)
            if self.is_solvable(numbers):
                break
        
        self.tiles = []
        idx = 0
        for r in range(self.grid_size):
            row = []
            for c in range(self.grid_size):
                num = numbers[idx]
                if num == 0: self.empty_pos = (r, c)
                row.append(Tile(num, r, c, self.tile_size, self.font))
                idx += 1
            self.tiles.append(row)
        self.moves = 0
        self.is_solved = False

    def is_solvable(self, numbers):
        inversions = 0
        nums_only = [n for n in numbers if n != 0]
        for i in range(len(nums_only)):
            for j in range(i + 1, len(nums_only)):
                if nums_only[i] > nums_only[j]:
                    inversions += 1
                    
        empty_idx = numbers.index(0)
        empty_row_from_bottom = self.grid_size - (empty_idx // self.grid_size)
        
        if self.grid_size % 2 != 0:
            return inversions % 2 == 0
        else:
            if empty_row_from_bottom % 2 == 0:
                return inversions % 2 != 0
            else:
                return inversions % 2 == 0

    def get_tile_at(self, row, col):
        return self.tiles[row][col]

    def move_tile(self, row, col):
        if self.is_solved: return
        er, ec = self.empty_pos
        # Check if adjacent
        if abs(er - row) + abs(ec - col) == 1:
            # Swap
            self.tiles[er][ec], self.tiles[row][col] = self.tiles[row][col], self.tiles[er][ec]
            self.tiles[er][ec].update_target(er, ec)
            self.tiles[row][col].update_target(row, col)
            self.empty_pos = (row, col)
            self.moves += 1
            self.sound.play('slide')
            self.check_win()

    def check_win(self):
        count = 1
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if r == self.grid_size - 1 and c == self.grid_size - 1:
                    if self.tiles[r][c].number != 0: return False
                else:
                    if self.tiles[r][c].number != count: return False
                count += 1
        self.is_solved = True
        self.sound.play('win')

    def update(self):
        for row in self.tiles:
            for tile in row:
                tile.update()

    def draw(self, surface):
        for row in self.tiles:
            for tile in row:
                tile.draw(surface)
