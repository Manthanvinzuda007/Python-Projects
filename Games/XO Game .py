# Manthan Vinzuda 
import pygame
import sys
import random
import copy

# --- INITIALIZATION ---
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 700  # Extra space at bottom for UI
BOARD_SIZE = 600
LINE_WIDTH = 12
BOARD_ROWS = 3
BOARD_COLS = 3
SQUARE_SIZE = BOARD_SIZE // BOARD_COLS
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 15
CROSS_WIDTH = 25
SPACE = SQUARE_SIZE // 4

# Colors (Modern Palette)
BG_COLOR = (20, 24, 35)
LINE_COLOR = (44, 52, 70)
CIRCLE_COLOR = (242, 235, 211)
CROSS_COLOR = (84, 84, 84)
HIGHLIGHT_COLOR = (46, 196, 182)
TEXT_COLOR = (255, 255, 255)

# --- SCREEN SETUP ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('TIC TAC TOE PRO')
screen.fill(BG_COLOR)

# --- LOGIC ---
class Board:
    def __init__(self):
        self.squares = [[0 for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]
        self.empty_sqrs = self.squares # list of squares
        self.marked_sqrs = 0

    def final_state(self, show=False):
        '''
            @return 0 if there is no win yet
            @return 1 if player 1 wins
            @return 2 if player 2 wins
        '''
        # Vertical wins
        for col in range(BOARD_COLS):
            if self.squares[0][col] == self.squares[1][col] == self.squares[2][col] != 0:
                if show:
                    color = CIRCLE_COLOR if self.squares[0][col] == 2 else CROSS_COLOR
                    i_pos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, 20)
                    f_pos = (col * SQUARE_SIZE + SQUARE_SIZE // 2, BOARD_SIZE - 20)
                    pygame.draw.line(screen, color, i_pos, f_pos, LINE_WIDTH)
                return self.squares[0][col]

        # Horizontal wins
        for row in range(BOARD_ROWS):
            if self.squares[row][0] == self.squares[row][1] == self.squares[row][2] != 0:
                if show:
                    color = CIRCLE_COLOR if self.squares[row][0] == 2 else CROSS_COLOR
                    i_pos = (20, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    f_pos = (BOARD_SIZE - 20, row * SQUARE_SIZE + SQUARE_SIZE // 2)
                    pygame.draw.line(screen, color, i_pos, f_pos, LINE_WIDTH)
                return self.squares[row][0]

        # Descending diagonal
        if self.squares[0][0] == self.squares[1][1] == self.squares[2][2] != 0:
            if show:
                color = CIRCLE_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                pygame.draw.line(screen, color, (20, 20), (BOARD_SIZE - 20, BOARD_SIZE - 20), CROSS_WIDTH)
            return self.squares[1][1]

        # Ascending diagonal
        if self.squares[2][0] == self.squares[1][1] == self.squares[0][2] != 0:
            if show:
                color = CIRCLE_COLOR if self.squares[1][1] == 2 else CROSS_COLOR
                pygame.draw.line(screen, color, (20, BOARD_SIZE - 20), (BOARD_SIZE - 20, 20), CROSS_WIDTH)
            return self.squares[1][1]

        return 0

    def mark_sqr(self, row, col, player):
        self.squares[row][col] = player
        self.marked_sqrs += 1

    def empty_sqr(self, row, col):
        return self.squares[row][col] == 0

    def get_empty_sqrs(self):
        empty_sqrs = []
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.empty_sqr(row, col):
                    empty_sqrs.append((row, col))
        return empty_sqrs

    def isfull(self):
        return self.marked_sqrs == 9

    def isempty(self):
        return self.marked_sqrs == 0

class AI:
    def __init__(self, level=1, player=2):
        self.level = level
        self.player = player

    def rnd(self, board):
        empty_sqrs = board.get_empty_sqrs()
        idx = random.randrange(0, len(empty_sqrs))
        return empty_sqrs[idx]

    def minimax(self, board, maximizing):
        case = board.final_state()

        if case == 1:
            return 1, None
        if case == 2:
            return -1, None
        elif board.isfull():
            return 0, None

        if maximizing:
            max_eval = -100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, 1)
                eval = self.minimax(temp_board, False)[0]
                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
            return max_eval, best_move

        elif not maximizing:
            min_eval = 100
            best_move = None
            empty_sqrs = board.get_empty_sqrs()

            for (row, col) in empty_sqrs:
                temp_board = copy.deepcopy(board)
                temp_board.mark_sqr(row, col, self.player)
                eval = self.minimax(temp_board, True)[0]
                if eval < min_eval:
                    min_eval = eval
                    best_move = (row, col)
            return min_eval, best_move

    def eval(self, main_board):
        if self.level == 0:
            move = self.rnd(main_board)
        else:
            eval, move = self.minimax(main_board, False)
        return move

class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.player = 1 # 1-cross, 2-circle
        self.gamemode = 'ai' # pvp or ai
        self.running = True
        self.draw_lines()

    def draw_lines(self):
        screen.fill(BG_COLOR)
        # Vertical
        pygame.draw.line(screen, LINE_COLOR, (SQUARE_SIZE, 10), (SQUARE_SIZE, BOARD_SIZE - 10), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (WIDTH - SQUARE_SIZE, 10), (WIDTH - SQUARE_SIZE, BOARD_SIZE - 10), LINE_WIDTH)
        # Horizontal
        pygame.draw.line(screen, LINE_COLOR, (10, SQUARE_SIZE), (BOARD_SIZE - 10, SQUARE_SIZE), LINE_WIDTH)
        pygame.draw.line(screen, LINE_COLOR, (10, WIDTH - SQUARE_SIZE), (BOARD_SIZE - 10, WIDTH - SQUARE_SIZE), LINE_WIDTH)

    def draw_fig(self, row, col):
        if self.player == 1:
            # Draw Cross
            start_desc = (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE)
            end_desc = (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE)
            pygame.draw.line(screen, CROSS_COLOR, start_desc, end_desc, CROSS_WIDTH)
            start_asc = (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SQUARE_SIZE - SPACE)
            end_asc = (col * SQUARE_SIZE + SQUARE_SIZE - SPACE, row * SQUARE_SIZE + SPACE)
            pygame.draw.line(screen, CROSS_COLOR, start_asc, end_asc, CROSS_WIDTH)
        elif self.player == 2:
            # Draw Circle
            center = (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2)
            pygame.draw.circle(screen, CIRCLE_COLOR, center, CIRCLE_RADIUS, CIRCLE_WIDTH)

    def make_move(self, row, col):
        self.board.mark_sqr(row, col, self.player)
        self.draw_fig(row, col)
        self.next_turn()

    def next_turn(self):
        self.player = self.player % 2 + 1

    def change_gamemode(self):
        self.gamemode = 'ai' if self.gamemode == 'pvp' else 'pvp'

    def isover(self):
        return self.board.final_state(show=True) != 0 or self.board.isfull()

    def reset(self):
        self.__init__()

def main():
    game = Game()
    board = game.board
    ai = game.ai
    font = pygame.font.SysFont('monospace', 25, bold=True)

    while True:
        # UI at the bottom
        pygame.draw.rect(screen, BG_COLOR, (0, BOARD_SIZE, WIDTH, HEIGHT - BOARD_SIZE))
        mode_text = font.render(f"MODE: {game.gamemode.upper()}", True, TEXT_COLOR)
        reset_text = font.render("PRESS 'R' TO RESET | 'G' FOR MODE", True, HIGHLIGHT_COLOR)
        screen.blit(mode_text, (20, BOARD_SIZE + 20))
        screen.blit(reset_text, (20, BOARD_SIZE + 60))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_g:
                    game.change_gamemode()
                if event.key == pygame.K_r:
                    game.reset()
                    board = game.board
                    ai = game.ai

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                row = pos[1] // SQUARE_SIZE
                col = pos[0] // SQUARE_SIZE
                
                if row < 3 and board.empty_sqr(row, col) and game.running:
                    game.make_move(row, col)
                    if game.isover():
                        game.running = False

        # AI Turn
        if game.gamemode == 'ai' and game.player == ai.player and game.running:
            pygame.display.update() # Update to show human move first
            row, col = ai.eval(board)
            game.make_move(row, col)
            if game.isover():
                game.running = False

        pygame.display.update()

if __name__ == "__main__":
    main()
