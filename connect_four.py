"""
Connect Four core logic — a "Connect Four with AI" backlog item reskinned
as UA Heroes vs the League of Villains. The rules and the minimax AI are
completely standard Connect Four; only the piece labels differ (HERO /
VILLAIN instead of 1 / 2), kept entirely separate from the pygame
front-end so the game rules and the AI are unit tested without a display.
"""

import math
import random

ROWS = 6
COLS = 7
EMPTY = 0
HERO = 1
VILLAIN = 2

WINDOW_LENGTH = 4


def create_board():
    return [[EMPTY] * COLS for _ in range(ROWS)]


def is_valid_location(board, col):
    return 0 <= col < COLS and board[ROWS - 1][col] == EMPTY


def get_valid_locations(board):
    return [col for col in range(COLS) if is_valid_location(board, col)]


def get_next_open_row(board, col):
    for row in range(ROWS):
        if board[row][col] == EMPTY:
            return row
    return None


def drop_piece(board, col, piece):
    """Drops `piece` into `col`, letting gravity pick the row. Returns the
    row it landed on, or None if the column is full."""
    row = get_next_open_row(board, col)
    if row is None:
        return None
    board[row][col] = piece
    return row


def is_board_full(board):
    return len(get_valid_locations(board)) == 0


def _all_windows(board):
    """Yields every length-4 window on the board: horizontal, vertical,
    and both diagonal directions."""
    for row in range(ROWS):
        for col in range(COLS - 3):
            yield [board[row][col + i] for i in range(4)]
    for col in range(COLS):
        for row in range(ROWS - 3):
            yield [board[row + i][col] for i in range(4)]
    for row in range(ROWS - 3):
        for col in range(COLS - 3):
            yield [board[row + i][col + i] for i in range(4)]
    for row in range(3, ROWS):
        for col in range(COLS - 3):
            yield [board[row - i][col + i] for i in range(4)]


def winning_move(board, piece):
    return any(window.count(piece) == 4 for window in _all_windows(board))


def _score_window(window, piece):
    opponent = VILLAIN if piece == HERO else HERO
    score = 0
    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2
    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= 4
    return score


def score_position(board, piece):
    """Heuristic board evaluation for `piece`: center-column preference
    (more ways to build four from the middle) plus every window's score."""
    score = 0
    center_col = [board[row][COLS // 2] for row in range(ROWS)]
    score += center_col.count(piece) * 3
    for window in _all_windows(board):
        score += _score_window(window, piece)
    return score


def is_terminal_node(board):
    return winning_move(board, HERO) or winning_move(board, VILLAIN) or is_board_full(board)


def minimax(board, depth, alpha, beta, maximizing_player, rng=None):
    """Standard alpha-beta minimax. The maximizing player is always
    VILLAIN (the AI); HERO (the human/player side) minimizes. Returns
    (best_column, score).

    Move selection uses strict `>`/`<` only — never treats an
    alpha-beta-pruned branch's returned bound as tied with the current
    best. A pruned branch's value is only a bound, not necessarily its
    true minimax value (that's the entire point of pruning: search
    stopped early because the branch is provably no better), so treating
    a bound as a genuine tie can make the AI pick a branch that only
    *looked* as good as the real best move on paper."""
    valid_locations = get_valid_locations(board)
    terminal = is_terminal_node(board)

    if depth == 0 or terminal:
        if terminal:
            if winning_move(board, VILLAIN):
                return None, 1_000_000_000
            elif winning_move(board, HERO):
                return None, -1_000_000_000
            else:
                return None, 0
        return None, score_position(board, VILLAIN)

    if maximizing_player:
        value = -math.inf
        best_col = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board[row][col] = VILLAIN
            _, new_score = minimax(board, depth - 1, alpha, beta, False, rng)
            board[row][col] = EMPTY
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    else:
        value = math.inf
        best_col = valid_locations[0]
        for col in valid_locations:
            row = get_next_open_row(board, col)
            board[row][col] = HERO
            _, new_score = minimax(board, depth - 1, alpha, beta, True, rng)
            board[row][col] = EMPTY
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


def get_ai_move(board, depth=4, rng=None):
    """Picks the AI's move. On a completely empty board there's no
    meaningful search to do yet (every opening is symmetric) — a real
    Connect Four opponent should still vary its opening rather than
    always play identically, so that one case picks randomly among the
    strongest (center-weighted) columns instead of going through
    minimax."""
    rng = rng or random
    if all(cell == EMPTY for row in board for cell in row):
        center = COLS // 2
        opening_choices = [center] * 3 + [center - 1, center + 1]
        return rng.choice([c for c in opening_choices if is_valid_location(board, c)])
    col, _score = minimax(board, depth, -math.inf, math.inf, True, rng)
    return col
