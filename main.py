"""
Heroes vs Villains Connect Four — pygame-ce front-end.
Drop hero-blue discs against an AI playing as the League of Villains
(minimax + alpha-beta pruning). Click a column to drop; first to connect
four wins.

Run with --demo for a scripted AI-vs-AI game (deterministic seed) — used
to generate the README's GIF; see tools/capture_gui_gif.py in the parent
project.

Visual identity: a UA-navy board with a hero-blue vs villain-purple disc
palette and a gold "win" highlight — distinct from this project set's
other pygame games.
"""

import argparse
import random
import sys

import pygame

from connect_four import (
    COLS,
    EMPTY,
    HERO,
    ROWS,
    VILLAIN,
    create_board,
    drop_piece,
    get_ai_move,
    get_valid_locations,
    is_board_full,
    winning_move,
)

CELL = 90
RADIUS = CELL // 2 - 6
WIDTH = COLS * CELL
HEIGHT = (ROWS + 1) * CELL  # extra top row for the "next piece" preview

BG = (12, 20, 40)          # UA navy
BOARD_COLOR = (24, 38, 74)
EMPTY_SLOT = (10, 16, 32)
HERO_COLOR = (66, 158, 235)     # hero blue
VILLAIN_COLOR = (147, 74, 199)  # villain purple
TEXT_LIGHT = (232, 236, 245)
WIN_GOLD = (247, 197, 72)


def board_row_to_screen(row):
    """Board row 0 is the bottom; the screen draws top-down."""
    return HEIGHT - (row * CELL) - CELL // 2


def draw_board(screen, board, font, message=None):
    screen.fill(BG)
    pygame.draw.rect(screen, BOARD_COLOR, (0, CELL, WIDTH, HEIGHT - CELL))

    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            color = EMPTY_SLOT
            if piece == HERO:
                color = HERO_COLOR
            elif piece == VILLAIN:
                color = VILLAIN_COLOR
            center = (col * CELL + CELL // 2, board_row_to_screen(row))
            pygame.draw.circle(screen, color, center, RADIUS)

    if message:
        msg_surf = font.render(message, True, WIN_GOLD)
        screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH // 2, CELL // 2)))

    pygame.display.flip()


def run_demo():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Heroes vs Villains Connect Four — demo")
    font = pygame.font.SysFont("arial", 22, bold=True)

    board = create_board()
    rng = random.Random(3)
    turn = HERO
    draw_board(screen, board, font)
    pygame.event.pump()
    pygame.time.wait(400)

    game_over = False
    while not game_over:
        col = get_ai_move(board, depth=4, rng=rng)
        if col is None or col not in get_valid_locations(board):
            break
        drop_piece(board, col, turn)

        if winning_move(board, turn):
            winner = "HEROES WIN!" if turn == HERO else "VILLAINS WIN!"
            draw_board(screen, board, font, message=winner)
            game_over = True
        elif is_board_full(board):
            draw_board(screen, board, font, message="DRAW")
            game_over = True
        else:
            draw_board(screen, board, font)

        pygame.event.pump()
        pygame.time.wait(400)
        turn = VILLAIN if turn == HERO else HERO

    pygame.time.wait(1500)
    pygame.quit()


def run_interactive():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Heroes vs Villains Connect Four")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 22, bold=True)

    board = create_board()
    game_over = False
    message = None

    def restart():
        nonlocal board, game_over, message
        board = create_board()
        game_over = False
        message = None

    draw_board(screen, board, font)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_r:
                    restart()
            elif event.type == pygame.MOUSEBUTTONDOWN and not game_over:
                col = event.pos[0] // CELL
                if col in get_valid_locations(board):
                    drop_piece(board, col, HERO)
                    if winning_move(board, HERO):
                        message, game_over = "HEROES WIN! (R to restart)", True
                    elif is_board_full(board):
                        message, game_over = "DRAW (R to restart)", True
                    else:
                        ai_col = get_ai_move(board, depth=5)
                        drop_piece(board, ai_col, VILLAIN)
                        if winning_move(board, VILLAIN):
                            message, game_over = "VILLAINS WIN! (R to restart)", True
                        elif is_board_full(board):
                            message, game_over = "DRAW (R to restart)", True

        draw_board(screen, board, font, message=message)
        clock.tick(30)

    pygame.quit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run a scripted AI-vs-AI demo and exit")
    args = parser.parse_args()

    if args.demo:
        run_demo()
    else:
        run_interactive()
    sys.exit(0)


if __name__ == "__main__":
    main()
