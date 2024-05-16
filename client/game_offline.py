from game import Game
import numpy


class GameOffline(Game):
    def __init__(self, screen):
        super().__init__(screen)

        self.turn_player = 1  # X starts first
        self.turn_player_name = "Player 1"

    def handle_move(self) -> None:
        hover_pos = self.get_hover_cell()
        if not hover_pos:
            return

        col, row = hover_pos
        if self.board[row][col] == 0:  # Only update if the cell is empty
            self.board[row][col] = self.turn_player
            self.winner = self.check_winner(col, row)
            if self.winner == 0:
                self.turn_player = 1 if self.turn_player == 2 else 2  # Switch player
                self.turn_player_name = f"Player { self.turn_player }"

    def check_winner(self, col: int, row: int) -> int:
        directions = [
            (1, 0),  # Horizontal
            (0, 1),  # Vertical
            (1, 1),  # Diagonal down-right
            (1, -1),  # Diagonal up-right
        ]

        piece = self.board[row][col]
        for direction in directions:
            dx, dy = direction
            count = 1  # Count the current cell
            start_pos = (col, row)
            end_pos = (col, row)

            # Check in the positive direction
            for i in range(1, 5):
                x = col + i * dx
                y = row + i * dy
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == piece
                ):
                    count += 1
                    end_pos = (x, y)
                else:
                    break

            # Check in the negative direction
            for i in range(1, 5):
                x = col - i * dx
                y = row - i * dy
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == piece
                ):
                    count += 1
                    start_pos = (x, y)
                else:
                    break

            if count >= 5:  # If there are 5 or more in a row
                self.winning_line = (start_pos, end_pos)
                self.winner_name = f"WINNER: Player { int(piece) }"
                return piece

        return 0  # Return 0 if there is no winner

    def reset(self):
        self.board = numpy.zeros(
            (
                self.NUMBER_CELL_GAME_HEIGHT,
                self.NUMBER_CELL_GAME_WIDTH,
            )
        )
        self.winner = 0
        self.winning_line = None
