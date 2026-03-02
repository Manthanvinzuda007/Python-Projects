import pygame
import sys
import math
import random
import numpy as np

# --- CONSTANTS & COLORS ---
BLUE = (30, 144, 255)
BLACK = (20, 20, 20)
RED = (255, 50, 50)
YELLOW = (255, 215, 0)
WHITE = (255, 255, 255)
HOVER_COLOR = (70, 170, 255)

ROW_COUNT = 6
COLUMN_COUNT = 7
SQUARESIZE = 100
RADIUS = int(SQUARESIZE / 2 - 5)
WIDTH = COLUMN_COUNT * SQUARESIZE
HEIGHT = (ROW_COUNT + 1) * SQUARESIZE
SIZE = (WIDTH, HEIGHT)

PLAYER = 0
AI = 1
EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2
WINDOW_LENGTH = 4

# --- INITIALIZATION ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption("Connect 4: Ultimate Edition")
myfont = pygame.font.SysFont("monospace", 75)
smallfont = pygame.font.SysFont("monospace", 40)

# --- SOUND SETUP ---
try:
    drop_sound = pygame.mixer.Sound("drop.wav")
    win_sound = pygame.mixer.Sound("win.wav")
except:
    drop_sound = None
    win_sound = None
    print("Audio files (drop.wav, win.wav) not found. Playing without sound.")

def play_sound(sound):
    if sound:
        sound.play()

# --- BOARD LOGIC ---
def create_board():
    return np.zeros((ROW_COUNT, COLUMN_COUNT))

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def winning_move(board, piece):
    # Check horizontal
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT):
            if board[r][c] == piece and board[r][c+1] == piece and board[r][c+2] == piece and board[r][c+3] == piece:
                return True
    # Check vertical
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c] == piece and board[r+2][c] == piece and board[r+3][c] == piece:
                return True
    # Check positively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(ROW_COUNT-3):
            if board[r][c] == piece and board[r+1][c+1] == piece and board[r+2][c+2] == piece and board[r+3][c+3] == piece:
                return True
    # Check negatively sloped diagonals
    for c in range(COLUMN_COUNT-3):
        for r in range(3, ROW_COUNT):
            if board[r][c] == piece and board[r-1][c+1] == piece and board[r-2][c+2] == piece and board[r-3][c+3] == piece:
                return True

# --- AI LOGIC ---
def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score

def score_position(board, piece):
    score = 0
    # Center column preference
    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score Horizontal
    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r,:])]
        for c in range(COLUMN_COUNT-3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score Vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:,c])]
        for r in range(ROW_COUNT-3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positive diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negative diagonal
    for r in range(ROW_COUNT-3):
        for c in range(COLUMN_COUNT-3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else: # Game is over, no more valid moves
                return (None, 0)
        else: # Depth is zero
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else: # Minimizing player
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth-1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

# --- UI DRAWING ---
def draw_board(board):
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):
            pygame.draw.rect(screen, BLUE, (c*SQUARESIZE, r*SQUARESIZE+SQUARESIZE, SQUARESIZE, SQUARESIZE))
            pygame.draw.circle(screen, BLACK, (int(c*SQUARESIZE+SQUARESIZE/2), int(r*SQUARESIZE+SQUARESIZE+SQUARESIZE/2)), RADIUS)
    
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT):        
            if board[r][c] == 1:
                pygame.draw.circle(screen, RED, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
            elif board[r][c] == 2: 
                pygame.draw.circle(screen, YELLOW, (int(c*SQUARESIZE+SQUARESIZE/2), HEIGHT-int(r*SQUARESIZE+SQUARESIZE/2)), RADIUS)
    pygame.display.update()

def draw_menu():
    screen.fill(BLACK)
    title_label = myfont.render("CONNECT 4", 1, WHITE)
    screen.blit(title_label, (WIDTH//2 - title_label.get_width()//2, 100))

    mouse = pygame.mouse.get_pos()
    
    # 2 Player Button
    p2_rect = pygame.Rect(WIDTH//2 - 150, 300, 300, 60)
    if p2_rect.collidepoint(mouse):
        pygame.draw.rect(screen, HOVER_COLOR, p2_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, BLUE, p2_rect, border_radius=10)
    p2_label = smallfont.render("VS Friend", 1, WHITE)
    screen.blit(p2_label, (p2_rect.centerx - p2_label.get_width()//2, p2_rect.centery - p2_label.get_height()//2))

    # AI Button
    ai_rect = pygame.Rect(WIDTH//2 - 150, 400, 300, 60)
    if ai_rect.collidepoint(mouse):
        pygame.draw.rect(screen, HOVER_COLOR, ai_rect, border_radius=10)
    else:
        pygame.draw.rect(screen, RED, ai_rect, border_radius=10)
    ai_label = smallfont.render("VS AI", 1, WHITE)
    screen.blit(ai_label, (ai_rect.centerx - ai_label.get_width()//2, ai_rect.centery - ai_label.get_height()//2))

    pygame.display.update()
    return p2_rect, ai_rect

# --- MAIN LOOPS ---
def main_menu():
    menu = True
    while menu:
        p2_rect, ai_rect = draw_menu()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if p2_rect.collidepoint(event.pos):
                    game_loop(vs_ai=False)
                if ai_rect.collidepoint(event.pos):
                    game_loop(vs_ai=True)

def game_loop(vs_ai):
    board = create_board()
    game_over = False
    turn = random.randint(PLAYER, AI)
    
    screen.fill(BLACK)
    draw_board(board)
    pygame.display.update()

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            if event.type == pygame.MOUSEMOTION:
                pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE))
                posx = event.pos[0]
                if turn == PLAYER:
                    pygame.draw.circle(screen, RED, (posx, int(SQUARESIZE/2)), RADIUS)
                elif not vs_ai and turn == AI:
                    pygame.draw.circle(screen, YELLOW, (posx, int(SQUARESIZE/2)), RADIUS)
            pygame.display.update()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pygame.draw.rect(screen, BLACK, (0,0, WIDTH, SQUARESIZE))
                
                # Player 1 Input
                if turn == PLAYER:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, PLAYER_PIECE)
                        play_sound(drop_sound)

                        if winning_move(board, PLAYER_PIECE):
                            label = myfont.render("Player 1 wins!!", 1, RED)
                            screen.blit(label, (40,10))
                            play_sound(win_sound)
                            game_over = True

                        turn += 1
                        turn = turn % 2
                        draw_board(board)

                # Player 2 Input (If playing vs Friend)
                elif not vs_ai and turn == AI:
                    posx = event.pos[0]
                    col = int(math.floor(posx/SQUARESIZE))

                    if is_valid_location(board, col):
                        row = get_next_open_row(board, col)
                        drop_piece(board, row, col, AI_PIECE)
                        play_sound(drop_sound)

                        if winning_move(board, AI_PIECE):
                            label = myfont.render("Player 2 wins!!", 1, YELLOW)
                            screen.blit(label, (40,10))
                            play_sound(win_sound)
                            game_over = True

                        turn += 1
                        turn = turn % 2
                        draw_board(board)

        # AI Input
        if vs_ai and turn == AI and not game_over:
            col, minimax_score = minimax(board, 4, -math.inf, math.inf, True)

            if is_valid_location(board, col):
                pygame.time.wait(500) # Give the AI a slight delay so it feels natural
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)
                play_sound(drop_sound)

                if winning_move(board, AI_PIECE):
                    label = myfont.render("AI wins!!", 1, YELLOW)
                    screen.blit(label, (40,10))
                    play_sound(win_sound)
                    game_over = True

                draw_board(board)
                turn += 1
                turn = turn % 2

        if game_over:
            pygame.time.wait(3000)
            main_menu() # Go back to menu after game ends

if __name__ == "__main__":
    main_menu()
