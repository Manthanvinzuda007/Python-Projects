import pygame
import chess
import sys
import os
import urllib.request
import random

# --- CONFIGURATION & COLORS ---
WIDTH, HEIGHT = 640, 640
SQ_SIZE = WIDTH // 8

LIGHT_SQUARE = (238, 238, 210)  
DARK_SQUARE = (118, 150, 86)    
HIGHLIGHT_COLOR = (186, 202, 68)  
VALID_MOVE_COLOR = (0, 0, 0, 40) 
MENU_BG = (48, 46, 43) # Chess.com dark mode background
BTN_COLOR = (129, 182, 76) # Chess.com green button
BTN_HOVER = (163, 215, 104)

IMAGES = {}
SOUNDS = {}

def download_assets():
    if not os.path.exists("images"):
        os.makedirs("images")
        print("Downloading HD chess icons...")
        pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
        for piece in pieces:
            url = f"https://images.chesscomfiles.com/chess-themes/pieces/neo/150/{piece}.png"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(f"images/{piece}.png", 'wb') as out_file:
                out_file.write(response.read())

    if not os.path.exists("sounds"):
        os.makedirs("sounds")
        print("Downloading sound effects...")
        sound_files = {'move': 'move-self.mp3', 'capture': 'capture.mp3', 'game_over': 'game-end.mp3'}
        for name, filename in sound_files.items():
            url = f"https://images.chesscomfiles.com/chess-themes/sounds/_MP3_/default/{filename}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(f"sounds/{name}.mp3", 'wb') as out_file:
                out_file.write(response.read())
        print("Assets Downloaded!")

def load_assets():
    pieces = ['wp', 'wn', 'wb', 'wr', 'wq', 'wk', 'bp', 'bn', 'bb', 'br', 'bq', 'bk']
    for piece in pieces:
        IMAGES[piece] = pygame.transform.smoothscale(pygame.image.load(f"images/{piece}.png"), (SQ_SIZE, SQ_SIZE))
    SOUNDS['move'] = pygame.mixer.Sound("sounds/move.mp3")
    SOUNDS['capture'] = pygame.mixer.Sound("sounds/capture.mp3")
    SOUNDS['game_over'] = pygame.mixer.Sound("sounds/game_over.mp3")

# Initialize
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Ultimate Python Chess")

download_assets()
load_assets()
font_large = pygame.font.SysFont("Arial", 40, bold=True)
font_medium = pygame.font.SysFont("Arial", 30, bold=True)

# --- AI LOGIC ---
piece_values = {chess.PAWN: 1, chess.KNIGHT: 3, chess.BISHOP: 3, chess.ROOK: 5, chess.QUEEN: 9, chess.KING: 0}

def evaluate_board(board):
    """Simple AI evaluation: Counts material advantage for Black."""
    score = 0
    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            val = piece_values[piece.piece_type]
            if piece.color == chess.BLACK:
                score += val
            else:
                score -= val
    return score

def get_ai_move(board):
    """Finds a decent move for the AI."""
    best_move = None
    best_score = -9999
    
    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves) # Add randomness so it doesn't play the exact same way
    
    for move in legal_moves:
        board.push(move)
        score = evaluate_board(board)
        board.pop()
        
        if score > best_score:
            best_score = score
            best_move = move
            
    return best_move

# --- DRAWING FUNCTIONS ---
def draw_menu(screen):
    screen.fill(MENU_BG)
    title = font_large.render("PYTHON CHESS", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))

    mouse_pos = pygame.mouse.get_pos()
    
    # PvP Button
    btn_pvp = pygame.Rect(160, 250, 320, 60)
    color_pvp = BTN_HOVER if btn_pvp.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color_pvp, btn_pvp, border_radius=10)
    txt_pvp = font_medium.render("Play with Friend", True, (255, 255, 255))
    screen.blit(txt_pvp, txt_pvp.get_rect(center=btn_pvp.center))

    # PvAI Button
    btn_ai = pygame.Rect(160, 350, 320, 60)
    color_ai = BTN_HOVER if btn_ai.collidepoint(mouse_pos) else BTN_COLOR
    pygame.draw.rect(screen, color_ai, btn_ai, border_radius=10)
    txt_ai = font_medium.render("Play with AI", True, (255, 255, 255))
    screen.blit(txt_ai, txt_ai.get_rect(center=btn_ai.center))

    return btn_pvp, btn_ai

def draw_board(screen, board, selected_sq):
    dot_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(dot_surface, VALID_MOVE_COLOR, (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 6)
    capture_surface = pygame.Surface((SQ_SIZE, SQ_SIZE), pygame.SRCALPHA)
    pygame.draw.circle(capture_surface, VALID_MOVE_COLOR, (SQ_SIZE // 2, SQ_SIZE // 2), SQ_SIZE // 2, SQ_SIZE//10)

    for r in range(8):
        for c in range(8):
            sq_index = (7 - r) * 8 + c
            color = LIGHT_SQUARE if (r + c) % 2 == 0 else DARK_SQUARE
            rect = pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            pygame.draw.rect(screen, color, rect)
            if selected_sq == sq_index:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, rect)

    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if piece:
            r = 7 - (sq // 8)
            c = sq % 8
            img_name = f"{'w' if piece.color == chess.WHITE else 'b'}{piece.symbol().lower()}"
            screen.blit(IMAGES[img_name], pygame.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    if selected_sq is not None:
        valid_moves = [m.to_square for m in board.legal_moves if m.from_square == selected_sq]
        for move_to_sq in valid_moves:
            r = 7 - (move_to_sq // 8)
            c = move_to_sq % 8
            target_piece = board.piece_at(move_to_sq)
            if target_piece and target_piece.color != board.turn:
                 screen.blit(capture_surface, (c * SQ_SIZE, r * SQ_SIZE))
            else:
                 screen.blit(dot_surface, (c * SQ_SIZE, r * SQ_SIZE))

def draw_game_over(screen, result):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180)) 
    screen.blit(overlay, (0, 0))
    res_text = "Checkmate!" if "1-0" in result or "0-1" in result else "Draw!"
    winner_text = "White Wins!" if "1-0" in result else "Black Wins!" if "0-1" in result else ""
    line1 = font_large.render(res_text, True, (255, 255, 255))
    line2 = font_large.render(winner_text, True, (255, 255, 255))
    screen.blit(line1, line1.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
    if winner_text:
        screen.blit(line2, line2.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))

# --- MAIN LOOP ---
def main():
    board = chess.Board()
    clock = pygame.time.Clock()
    selected_sq = None
    
    # States: 'MENU', 'PVP', 'PVAI'
    state = 'MENU'
    game_over = False
    game_over_sound_played = False

    running = True
    while running:
        if state == 'MENU':
            btn_pvp, btn_ai = draw_menu(screen)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_pvp.collidepoint(event.pos):
                        state = 'PVP'
                    elif btn_ai.collidepoint(event.pos):
                        state = 'PVAI'

        else: # GAMEPLAY (PVP or PVAI)
            # --- AI TURN ---
            if state == 'PVAI' and board.turn == chess.BLACK and not game_over:
                # Add a tiny delay so the AI doesn't move instantly (feels more natural)
                pygame.time.delay(300) 
                ai_move = get_ai_move(board)
                if ai_move:
                    is_capture = board.is_capture(ai_move)
                    board.push(ai_move)
                    SOUNDS['capture'].play() if is_capture else SOUNDS['move'].play()

            # --- PLAYER TURN / EVENTS ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: # Press ESC to go back to Menu
                        state = 'MENU'
                        board.reset()
                        game_over = False
                        game_over_sound_played = False
                        
                elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                    # Prevent White from clicking if it's AI's turn
                    if state == 'PVAI' and board.turn == chess.BLACK:
                        continue 

                    if event.button == 1: 
                        x, y = pygame.mouse.get_pos()
                        c, r = x // SQ_SIZE, y // SQ_SIZE
                        clicked_sq = (7 - r) * 8 + c

                        if selected_sq is not None:
                            move = chess.Move(selected_sq, clicked_sq)
                            promo_move = chess.Move(selected_sq, clicked_sq, promotion=chess.QUEEN)
                            move_to_play = move if move in board.legal_moves else promo_move if promo_move in board.legal_moves else None

                            if move_to_play:
                                is_capture = board.is_capture(move_to_play)
                                board.push(move_to_play)
                                selected_sq = None
                                SOUNDS['capture'].play() if is_capture else SOUNDS['move'].play()
                            else:
                                clicked_piece = board.piece_at(clicked_sq)
                                selected_sq = clicked_sq if clicked_piece and clicked_piece.color == board.turn else None 
                        else:
                            clicked_piece = board.piece_at(clicked_sq)
                            selected_sq = clicked_sq if clicked_piece and clicked_piece.color == board.turn else None

            draw_board(screen, board, selected_sq)
            
            if board.is_game_over():
                game_over = True
                draw_game_over(screen, board.result())
                if not game_over_sound_played:
                    SOUNDS['game_over'].play()
                    game_over_sound_played = True

        pygame.display.flip()
        clock.tick(30) 

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
