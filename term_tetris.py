import curses
import time
import random
import json
import os

# Constants
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
BLOCK_CHAR = "██"
EMPTY_CHAR = "  "

# Tetromino shapes
# Keys: Shape name, Values: list of rotations (each rotation is a list of coordinates relative to center)
SHAPES = {
    'I': [ [(0, -1), (0, 0), (0, 1), (0, 2)], [(-1, 0), (0, 0), (1, 0), (2, 0)] ],
    'O': [ [(0, 0), (0, 1), (1, 0), (1, 1)] ],
    'T': [ [(0, -1), (0, 0), (0, 1), (-1, 0)], [(-1, 0), (0, 0), (1, 0), (0, 1)], [(0, -1), (0, 0), (0, 1), (1, 0)], [(-1, 0), (0, 0), (1, 0), (0, -1)] ],
    'S': [ [(0, 0), (0, 1), (-1, -1), (-1, 0)], [(-1, 0), (0, 0), (0, 1), (1, 1)] ],
    'Z': [ [(-1, 0), (-1, 1), (0, -1), (0, 0)], [(0, 1), (1, 1), (-1, 0), (0, 0)] ],
    'J': [ [(-1, -1), (0, -1), (0, 0), (0, 1)], [(-1, 1), (-1, 0), (0, 0), (1, 0)], [(1, 1), (0, 1), (0, 0), (0, -1)], [(1, -1), (1, 0), (0, 0), (-1, 0)] ],
    'L': [ [(1, -1), (0, -1), (0, 0), (0, 1)], [(-1, -1), (-1, 0), (0, 0), (1, 0)], [(-1, 1), (0, 1), (0, 0), (0, -1)], [(1, 1), (1, 0), (0, 0), (-1, 0)] ]
}

COLORS = {
    'I': 1, # Cyan
    'O': 2, # Yellow
    'T': 3, # Magenta
    'S': 4, # Green
    'Z': 5, # Red
    'J': 6, # Blue
    'L': 7  # White
}

class Piece:
    def __init__(self, shape_name):
        self.shape_name = shape_name
        self.rotations = SHAPES[shape_name]
        self.rotation_index = 0
        self.x = BOARD_WIDTH // 2
        self.y = 1  # Start slightly down or adjust as needed

    @property
    def blocks(self):
        return self.rotations[self.rotation_index]

    def rotate(self):
        self.rotation_index = (self.rotation_index + 1) % len(self.rotations)

    def undo_rotate(self):
        self.rotation_index = (self.rotation_index - 1) % len(self.rotations)


class Game:
    def __init__(self):
        self.board = [[None for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]
        self.current_piece = self._new_piece()
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.game_over = False

    def _new_piece(self):
        shape_name = random.choice(list(SHAPES.keys()))
        piece = Piece(shape_name)
        if self._check_collision(piece, piece.x, piece.y):
            self.game_over = True
        return piece

    def _check_collision(self, piece, dx, dy):
        for bx, by in piece.blocks:
            nx = dx + bx
            ny = dy + by
            if nx < 0 or nx >= BOARD_WIDTH or ny >= BOARD_HEIGHT:
                return True
            if ny >= 0 and self.board[ny][nx] is not None:
                return True
        return False

    def move_piece(self, dx, dy):
        if not self._check_collision(self.current_piece, self.current_piece.x + dx, self.current_piece.y + dy):
            self.current_piece.x += dx
            self.current_piece.y += dy
            return True
        return False

    def rotate_piece(self):
        self.current_piece.rotate()
        if self._check_collision(self.current_piece, self.current_piece.x, self.current_piece.y):
            self.current_piece.undo_rotate()
            return False
        return True

    def lock_piece(self):
        for bx, by in self.current_piece.blocks:
            px = self.current_piece.x + bx
            py = self.current_piece.y + by
            if py >= 0:
                self.board[py][px] = self.current_piece.shape_name
        self._clear_lines()
        self.current_piece = self._new_piece()

    def drop_piece(self):
        if not self.move_piece(0, 1):
            self.lock_piece()
            return False
        return True

    def _clear_lines(self):
        lines_to_clear = []
        for y in range(BOARD_HEIGHT):
            if all(self.board[y][x] is not None for x in range(BOARD_WIDTH)):
                lines_to_clear.append(y)

        for y in lines_to_clear:
            del self.board[y]
            self.board.insert(0, [None for _ in range(BOARD_WIDTH)])

        num_lines = len(lines_to_clear)
        if num_lines > 0:
            self.lines_cleared += num_lines
            # Simple scoring
            self.score += (num_lines ** 2) * 100 * self.level
            self.level = (self.lines_cleared // 10) + 1


def load_high_scores():
    try:
        if os.path.exists('.tetris_high_scores.json'):
            with open('.tetris_high_scores.json', 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_high_score(score):
    scores = load_high_scores()
    scores.append(score)
    scores.sort(reverse=True)
    scores = scores[:5] # Keep top 5
    try:
        with open('.tetris_high_scores.json', 'w') as f:
            json.dump(scores, f)
    except Exception:
        pass


def draw_board(stdscr, game):
    # Draw border
    for y in range(BOARD_HEIGHT + 2):
        stdscr.addstr(y, 0, "│")
        stdscr.addstr(y, BOARD_WIDTH * 2 + 1, "│")
    for x in range(BOARD_WIDTH * 2 + 2):
        stdscr.addstr(BOARD_HEIGHT + 1, x, "─")
        stdscr.addstr(0, x, "─")
    stdscr.addstr(0, 0, "┌")
    stdscr.addstr(0, BOARD_WIDTH * 2 + 1, "┐")
    stdscr.addstr(BOARD_HEIGHT + 1, 0, "└")
    stdscr.addstr(BOARD_HEIGHT + 1, BOARD_WIDTH * 2 + 1, "┘")

    # Draw locked blocks
    for y in range(BOARD_HEIGHT):
        for x in range(BOARD_WIDTH):
            shape_name = game.board[y][x]
            if shape_name:
                color = curses.color_pair(COLORS[shape_name])
                stdscr.addstr(y + 1, x * 2 + 1, BLOCK_CHAR, color)
            else:
                stdscr.addstr(y + 1, x * 2 + 1, EMPTY_CHAR)

    # Draw current piece
    if not game.game_over:
        color = curses.color_pair(COLORS[game.current_piece.shape_name])
        for bx, by in game.current_piece.blocks:
            px = game.current_piece.x + bx
            py = game.current_piece.y + by
            if py >= 0 and py < BOARD_HEIGHT and px >= 0 and px < BOARD_WIDTH:
                stdscr.addstr(py + 1, px * 2 + 1, BLOCK_CHAR, color)


def main(stdscr):
    # Setup curses
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(0)

    # Initialize colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_MAGENTA, -1)
    curses.init_pair(4, curses.COLOR_GREEN, -1)
    curses.init_pair(5, curses.COLOR_RED, -1)
    curses.init_pair(6, curses.COLOR_BLUE, -1)
    curses.init_pair(7, curses.COLOR_WHITE, -1)

    game = Game()
    high_scores = load_high_scores()

    last_drop_time = time.time()
    running = True
    paused = False
    score_saved = False

    while running:
        current_time = time.time()

        # Handle input
        key = stdscr.getch()
        if key == ord('q'):
            running = False
        elif key == ord('p'):
            paused = not paused

        if not paused and not game.game_over:
            if key == curses.KEY_LEFT:
                game.move_piece(-1, 0)
            elif key == curses.KEY_RIGHT:
                game.move_piece(1, 0)
            elif key == curses.KEY_DOWN:
                game.drop_piece()
                last_drop_time = current_time
            elif key == curses.KEY_UP:
                game.rotate_piece()
            elif key == ord(' '):
                while game.drop_piece():
                    pass
                last_drop_time = current_time

            # Automatic drop based on level
            drop_interval = max(0.1, 0.8 - (game.level - 1) * 0.05)
            if current_time - last_drop_time > drop_interval:
                game.drop_piece()
                last_drop_time = current_time

        stdscr.erase()

        # Draw game
        draw_board(stdscr, game)

        # Draw UI
        info_x = BOARD_WIDTH * 2 + 4
        stdscr.addstr(2, info_x, f"Score: {game.score}")
        stdscr.addstr(3, info_x, f"Level: {game.level}")
        stdscr.addstr(4, info_x, f"Lines: {game.lines_cleared}")

        stdscr.addstr(6, info_x, "Controls:")
        stdscr.addstr(7, info_x, "← → : Move")
        stdscr.addstr(8, info_x, "↑   : Rotate")
        stdscr.addstr(9, info_x, "↓   : Soft Drop")
        stdscr.addstr(10, info_x, "SPC : Hard Drop")
        stdscr.addstr(11, info_x, "p   : Pause")
        stdscr.addstr(12, info_x, "q   : Quit")

        if high_scores:
            stdscr.addstr(14, info_x, "High Scores:")
            for i, hs in enumerate(high_scores):
                stdscr.addstr(15 + i, info_x, f"{i+1}. {hs}")

        if paused:
            stdscr.addstr(BOARD_HEIGHT // 2, (BOARD_WIDTH * 2) // 2 - 3, "PAUSED", curses.A_BOLD)
        elif game.game_over:
            stdscr.addstr(BOARD_HEIGHT // 2, (BOARD_WIDTH * 2) // 2 - 4, "GAME OVER", curses.A_BOLD)
            stdscr.addstr(BOARD_HEIGHT // 2 + 1, (BOARD_WIDTH * 2) // 2 - 6, "Press 'q' to quit")
            if not score_saved:
                save_high_score(game.score)
                high_scores = load_high_scores() # reload so they show immediately
                score_saved = True

        stdscr.refresh()
        time.sleep(0.01)

if __name__ == "__main__":
    curses.wrapper(main)
