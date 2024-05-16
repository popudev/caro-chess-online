from game_offline import GameOffline
import random
import time


class GameAI(GameOffline):
    def __init__(self, screen):
        super().__init__(screen)
        self.player_human = 1  # Người chơi là X (1)
        self.player_ai = 2  # AI là O (2)
        self.turn_player_name = "Player 1"

    def handle_move(self) -> None:
        hover_pos = self.get_hover_cell()
        if not hover_pos:
            return

        col, row = hover_pos
        if self.board[row][col] == 0:  # Only update if the cell is empty
            self.play_sounds(self.move_sound)
            self.board[row][col] = self.turn_player
            self.winner = self.check_winner(col, row)
            if self.winner == 0:
                self.turn_player = 1 if self.turn_player == 2 else 2  # Switch player
                self.turn_player_name = (
                    f"Player {self.turn_player}"
                    if self.turn_player == self.player_human
                    else "AI"
                )
                if self.turn_player == self.player_ai:
                    self.ai_move()

    def ai_move(self):
        # # Kiểm tra nếu AI có thể thắng
        # if self.try_to_win():
        #     return
        # Kiểm tra nếu cần chặn đối thủ thắng
        # if self.block_opponent():
        #     return
        # Nếu không thì đánh ngẫu nhiên
        self.random_move()

    def try_to_win(self):

        for row in range(self.NUMBER_CELL_GAME_HEIGHT):
            for col in range(self.NUMBER_CELL_GAME_WIDTH):
                if self.board[row][col] == 0:
                    self.board[row][col] = self.player_ai
                    if self.check_winner(col, row) == self.player_ai:
                        self.winner = self.player_ai
                        self.winner_name = f"Ai win!"
                        return True

                    self.board[row][col] = 0

        return False

    def block_opponent(self):
        hover_pos = self.get_hover_cell()
        if not hover_pos:
            return False

        col, row = hover_pos
        result = self.is_about_to_win(self.player_human, col, row)
        if result:
            self.board[result["block_pos"][1]][result["block_pos"][0]] = self.player_ai
            return True

        return False

    def is_about_to_win(self, player, col, row):
        directions = [
            (1, 0),  # Horizontal
            (0, 1),  # Vertical
            (1, 1),  # Diagonal down-right
            (1, -1),  # Diagonal up-right
        ]

        for direction in directions:
            count = 1  # Count the current cell
            # Check in the positive direction
            start_pos = (col, row)
            end_pos = (col, row)

            for i in range(1, 3):
                x = col + i * direction[0]
                y = row + i * direction[1]
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == player
                ):
                    count += 1
                    end_pos = (x, y)
                else:
                    break
            # Check in the negative direction
            for i in range(1, 3):
                x = col - i * direction[0]
                y = row - i * direction[1]
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == player
                ):
                    count += 1
                    start_pos = (x, y)
                else:
                    break

            if count >= 3:
                # Check the empty cells at both ends of the line
                # Check one end
                x = end_pos[0] + direction[0]
                y = end_pos[1] + direction[1]
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == 0
                ):
                    return {"block_pos": (x, y)}

                # Check the other end
                x = start_pos[0] - direction[0]
                y = start_pos[1] - direction[1]
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == 0
                ):
                    return {"block_pos": (x, y)}

        return False

    def random_move(self):
        empty_cells = [
            (row, col)
            for row in range(self.NUMBER_CELL_GAME_HEIGHT)
            for col in range(self.NUMBER_CELL_GAME_WIDTH)
            if self.board[row][col] == 0
        ]
        if empty_cells:
            row, col = random.choice(empty_cells)
            self.board[row][col] = self.player_ai
            self.winner = self.check_winner(col, row)
            if self.winner == 0:
                self.turn_player = self.player_human
                self.turn_player_name = f"Player {self.turn_player}"

    def reset(self):
        super().reset()
        self.turn_player = self.player_human
        self.turn_player_name = "Player 1"
