import random
import unittest

from connect_four import (
    COLS,
    EMPTY,
    HERO,
    ROWS,
    VILLAIN,
    create_board,
    drop_piece,
    get_ai_move,
    get_next_open_row,
    get_valid_locations,
    is_board_full,
    is_valid_location,
    winning_move,
)


class TestBoardMechanics(unittest.TestCase):
    def test_new_board_is_empty(self):
        board = create_board()
        self.assertEqual(len(board), ROWS)
        self.assertEqual(len(board[0]), COLS)
        self.assertTrue(all(cell == EMPTY for row in board for cell in row))

    def test_drop_piece_lands_on_the_floor_first(self):
        board = create_board()
        row = drop_piece(board, 3, HERO)
        self.assertEqual(row, 0)
        self.assertEqual(board[0][3], HERO)

    def test_drop_piece_stacks_on_top_of_previous_piece(self):
        board = create_board()
        drop_piece(board, 3, HERO)
        row = drop_piece(board, 3, VILLAIN)
        self.assertEqual(row, 1)
        self.assertEqual(board[1][3], VILLAIN)

    def test_drop_piece_on_full_column_returns_none(self):
        board = create_board()
        for _ in range(ROWS):
            drop_piece(board, 0, HERO)
        self.assertFalse(is_valid_location(board, 0))
        self.assertIsNone(drop_piece(board, 0, VILLAIN))

    def test_get_valid_locations_excludes_full_columns(self):
        board = create_board()
        for _ in range(ROWS):
            drop_piece(board, 2, HERO)
        self.assertNotIn(2, get_valid_locations(board))
        self.assertEqual(len(get_valid_locations(board)), COLS - 1)

    def test_is_board_full(self):
        board = create_board()
        self.assertFalse(is_board_full(board))
        for col in range(COLS):
            for _ in range(ROWS):
                drop_piece(board, col, HERO)
        self.assertTrue(is_board_full(board))


class TestWinDetection(unittest.TestCase):
    def test_horizontal_win(self):
        board = create_board()
        for col in range(4):
            drop_piece(board, col, HERO)
        self.assertTrue(winning_move(board, HERO))
        self.assertFalse(winning_move(board, VILLAIN))

    def test_vertical_win(self):
        board = create_board()
        for _ in range(4):
            drop_piece(board, 5, VILLAIN)
        self.assertTrue(winning_move(board, VILLAIN))

    def test_positive_diagonal_win(self):
        board = create_board()
        # Build a staircase so HERO pieces land on the /-diagonal.
        drop_piece(board, 0, HERO)
        drop_piece(board, 1, VILLAIN)
        drop_piece(board, 1, HERO)
        drop_piece(board, 2, VILLAIN)
        drop_piece(board, 2, VILLAIN)
        drop_piece(board, 2, HERO)
        drop_piece(board, 3, VILLAIN)
        drop_piece(board, 3, VILLAIN)
        drop_piece(board, 3, VILLAIN)
        drop_piece(board, 3, HERO)
        self.assertTrue(winning_move(board, HERO))

    def test_negative_diagonal_win(self):
        board = create_board()
        drop_piece(board, 3, HERO)
        drop_piece(board, 2, VILLAIN)
        drop_piece(board, 2, HERO)
        drop_piece(board, 1, VILLAIN)
        drop_piece(board, 1, VILLAIN)
        drop_piece(board, 1, HERO)
        drop_piece(board, 0, VILLAIN)
        drop_piece(board, 0, VILLAIN)
        drop_piece(board, 0, VILLAIN)
        drop_piece(board, 0, HERO)
        self.assertTrue(winning_move(board, HERO))

    def test_no_false_positive_on_empty_board(self):
        board = create_board()
        self.assertFalse(winning_move(board, HERO))
        self.assertFalse(winning_move(board, VILLAIN))


class TestAI(unittest.TestCase):
    def test_ai_takes_an_immediate_winning_move(self):
        board = create_board()
        # VILLAIN has 3 in a row (columns 0-2); column 3 wins immediately.
        for col in range(3):
            drop_piece(board, col, VILLAIN)
        move = get_ai_move(board, depth=3, rng=random.Random(1))
        self.assertEqual(move, 3)

    def test_ai_blocks_an_immediate_opponent_win(self):
        board = create_board()
        # HERO has 3 in a row (columns 0-2); HERO wins at column 3 unless blocked.
        for col in range(3):
            drop_piece(board, col, HERO)
        move = get_ai_move(board, depth=3, rng=random.Random(1))
        self.assertEqual(move, 3)

    def test_ai_prefers_winning_now_over_blocking_an_unrelated_threat(self):
        board = create_board()
        # VILLAIN can win immediately at column 3. HERO separately has a
        # vertical 3-stack building in column 6 — a real future threat,
        # but irrelevant once VILLAIN wins outright this turn.
        for col in range(3):
            drop_piece(board, col, VILLAIN)
        for _ in range(3):
            drop_piece(board, 6, HERO)
        move = get_ai_move(board, depth=3, rng=random.Random(1))
        self.assertEqual(move, 3)

    def test_ai_returns_a_valid_column_on_a_near_empty_board(self):
        board = create_board()
        move = get_ai_move(board, depth=2, rng=random.Random(1))
        self.assertIn(move, get_valid_locations(board))


if __name__ == "__main__":
    unittest.main()
