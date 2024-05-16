from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
import numpy as np
import random
import string
from config import Config
from typing import List, Dict, Optional

app = Flask(__name__)
app.config["SECRET_KEY"] = "secret!"
socketio = SocketIO(app)


class Game:
    def __init__(self, game_id: str) -> None:
        self.game_id: str = game_id
        self.player_ids: List[str] = []
        self.move_history = []
        self.board: np.ndarray = np.zeros(
            (Config.NUMBER_CELL_HEIGHT - 2, Config.NUMBER_CELL_WIDTH)
        )
        self.NUMBER_CELL_GAME_WIDTH: int = Config.NUMBER_CELL_WIDTH
        self.NUMBER_CELL_GAME_HEIGHT: int = Config.NUMBER_CELL_HEIGHT - 2
        self.turn_player_id: Optional[str] = None
        self.piece: int = 1

    def add_player(self, player_sid: str) -> bool:
        if len(self.player_ids) < 2:
            self.player_ids.append(player_sid)
            return True
        else:
            return False

    def remove_player(self, player_sid: str) -> None:
        if player_sid in self.player_ids:
            self.player_ids.remove(player_sid)

    def make_move(self, row: int, col: int, player_id: str) -> bool:
        if player_id != self.turn_player_id:
            return False

        if self.board[row][col] == 0:
            self.board[row][col] = self.piece
            self.move_history.append((self.piece, row, col))

            self.piece = 1 if self.piece == 2 else 2
            self.turn_player_id = (
                self.player_ids[0]
                if player_id == self.player_ids[1]
                else self.player_ids[1]
            )

            return True
        else:
            return False

    def undo_move(self, player_id) -> None:
        if len(self.player_ids) != 2:
            return  # Cannot undo move if there are not two players
        if len(self.move_history) < 2:
            return  # Cannot undo move if there are no previous moves
        if player_id != self.turn_player_id:
            return  # Cannot undo move if it is not the player's turn

        # Revert the board to the state before the last move
        prev_move = self.move_history.pop()  # Remove the last move
        prev_piece, prev_row, prev_col = prev_move
        self.board[prev_row][prev_col] = 0  # Reset the cell to empty
        self.piece = prev_piece  # Switch back to the previous player's piece
        self.turn_player_id = (
            self.player_ids[0]
            if self.turn_player_id == self.player_ids[1]
            else self.player_ids[1]
        )  # Switch back to the previous player's turn

        return prev_move

    def set_turn_player_id(self, turn_player_id: str) -> None:
        self.turn_player_id = turn_player_id

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
                return {
                    "winning_line": (start_pos, end_pos),
                    "piece": piece,
                }

        return 0  # Return 0 if there is no winner


class CaroServer:
    def __init__(self) -> None:
        self.games: Dict[str, Game] = {}

    def on_connect(self) -> None:
        print("Client connected:", request.sid)

    def on_disconnect(self) -> None:
        print("Client disconnected:", request.sid)
        self.remove_player_from_game(request.sid)

    def on_join(self, data: Dict[str, str]) -> None:
        # Attempt to find an existing game with an open spot
        game_id = None
        for gid, game in self.games.items():
            if len(game.player_ids) < 2:
                game_id = gid
                break

        # If no open game is found, create a new game
        if game_id is None:
            game_id = self.generate_game_id()
            self.games[game_id] = Game(game_id)

        print("Joining game_id:", game_id)
        game = self.games[game_id]

        if game.add_player(request.sid):
            join_room(game_id)
            emit(
                "joined",
                {"game_id": game_id, "player_id": request.sid},
                room=request.sid,
            )

            if len(game.player_ids) == 2:
                emit("start_game", {"game_id": game_id}, room=game_id)
                starting_player_id = random.choice(game.player_ids)
                game.set_turn_player_id(starting_player_id)
                emit(
                    "starting_player",
                    {"player_id": starting_player_id, "piece": game.piece},
                    room=game_id,
                )

    def on_move(self, data: Dict[str, int]) -> None:
        game_id = data["game_id"]
        row = data["row"]
        col = data["col"]
        player_id = request.sid
        game = self.games[game_id]
        if game.make_move(row, col, player_id):
            emit(
                "move",
                {"row": row, "col": col, "piece": game.board[row][col]},
                room=game_id,
            )

            winner = game.check_winner(col, row)
            if winner != 0:
                emit("game_over", {"winner": winner}, room=game_id)
            else:
                emit(
                    "starting_player",
                    {"player_id": game.turn_player_id, "piece": game.piece},
                    room=game_id,
                )

    def on_undo_move(self, data: Dict[str, str]) -> None:
        game_id = data["game_id"]
        game = self.games.get(game_id)
        player_id = request.sid

        if game:
            prev_move = game.undo_move(player_id)
            # Notify clients that the move was undone
            emit("undo_move", {"prev_move": prev_move}, room=game_id)
            # Notify the next player to make a move
            emit(
                "starting_player",
                {"player_id": game.turn_player_id, "piece": game.piece},
                room=game_id,
            )

    def remove_player_from_game(self, player_sid: str) -> None:
        for game_id, game in list(self.games.items()):
            if player_sid in game.player_ids:
                game.remove_player(player_sid)
                leave_room(game_id)

                # Notify remaining player and clean up if necessary
                if len(game.player_ids) == 0:
                    del self.games[game_id]
                elif len(game.player_ids) == 1:
                    remaining_player_id = game.player_ids[0]
                    emit(
                        "opponent_left",
                        {"message": "Your opponent has left the game."},
                        room=remaining_player_id,
                    )

    def generate_game_id(self) -> str:
        return "".join(random.choices(string.digits, k=6))


caro_server = CaroServer()


# Socket event handlers
@socketio.on("connect")
def on_connect() -> None:
    caro_server.on_connect()


@socketio.on("disconnect")
def on_disconnect() -> None:
    caro_server.on_disconnect()


@socketio.on("join")
def on_join(data: Dict[str, str]) -> None:
    caro_server.on_join(data)


@socketio.on("move")
def on_move(data: Dict[str, int]) -> None:
    caro_server.on_move(data)


@socketio.on("undo_move")
def on_undo_move(data: Dict[str, str]) -> None:
    caro_server.on_undo_move(data)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
