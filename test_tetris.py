import unittest
from term_tetris import Game, Piece, BOARD_WIDTH, BOARD_HEIGHT

class TestTetrisGame(unittest.TestCase):
    def test_initial_state(self):
        game = Game()
        self.assertEqual(game.score, 0)
        self.assertEqual(game.level, 1)
        self.assertFalse(game.game_over)
        self.assertIsNotNone(game.current_piece)

    def test_piece_movement(self):
        game = Game()
        initial_x = game.current_piece.x
        initial_y = game.current_piece.y

        # Move right
        game.move_piece(1, 0)
        self.assertEqual(game.current_piece.x, initial_x + 1)
        self.assertEqual(game.current_piece.y, initial_y)

        # Move left
        game.move_piece(-1, 0)
        self.assertEqual(game.current_piece.x, initial_x)
        self.assertEqual(game.current_piece.y, initial_y)

        # Move down
        game.move_piece(0, 1)
        self.assertEqual(game.current_piece.x, initial_x)
        self.assertEqual(game.current_piece.y, initial_y + 1)

    def test_collision(self):
        game = Game()

        # Force a piece to the bottom
        while game.move_piece(0, 1):
            pass

        # Try to move down again, should fail
        self.assertFalse(game.move_piece(0, 1))

        # Test out of bounds left
        while game.move_piece(-1, 0):
            pass
        self.assertFalse(game.move_piece(-1, 0))

        # Test out of bounds right
        while game.move_piece(1, 0):
            pass
        self.assertFalse(game.move_piece(1, 0))

    def test_line_clear(self):
        game = Game()

        # Fill the bottom row with 'I' shapes or any block to simulate a full row
        for x in range(BOARD_WIDTH):
            game.board[BOARD_HEIGHT - 1][x] = 'I'

        # The game's line clear is triggered when a piece locks, so let's call it manually
        game._clear_lines()

        self.assertEqual(game.lines_cleared, 1)
        self.assertGreater(game.score, 0)

        # Bottom line should now be empty (or None)
        for x in range(BOARD_WIDTH):
            self.assertIsNone(game.board[BOARD_HEIGHT - 1][x])

if __name__ == '__main__':
    unittest.main()
