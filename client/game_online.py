import pygame
import sys
import numpy as np
from color import Color
import socketio
from asset import Asset
from config import Config
from utils import Utils
from game import Game


class GameOnline(Game):
    def __init__(self, screen):
        super().__init__(screen)

        # Khởi tạo lại nút mới vào màn hình game
        self.nav_options_start_game = ["Exit"]

        # Khởi tạo một số nút tùy theo màn hình sẽ hiển thị trong game
        self.btn_go_back_error = None

        # Khởi tạo SocketIO client
        self.sio = socketio.Client()
        self.game_id = None
        self.player_current_id = None

        self.listen_socket_events()
        self.isError = False
        self.isJoined = False
        self.isStart = False
        self.isMove = False
        self.isOpponentLeft = False

    def draw_screen(self):
        self.screen.fill(Color.WHITE)
        self.nav_rects = []
        if self.isError:
            self.draw_connecting_server(isError=True)
            return

        if self.isJoined == False:  # Nếu chưa join game
            self.draw_waiting_join_game()
            return

        if self.isOpponentLeft:
            self.draw_opponent_left()
            return

        self.draw_nav()
        self.draw_game()

        if self.isStart == False:
            self.draw_waiting_opponent_join()
            return

        if self.winner != 0:
            self.draw_winning_line()
            self.draw_end_game()

    def draw_connecting_server(self, isError=False):
        font = pygame.font.Font(None, 36)

        if not isError:
            textStr = "Waiting to connect..."
            text = font.render(textStr, True, Color.BLACK)
            x = self.SCREEN_WIDTH // 2
            y = self.SCREEN_HEIGHT // 2
            textrect = text.get_rect(center=(x, y))
            self.screen.blit(text, textrect)

        else:
            textStr = "Server Error! Please try again later!"
            text = font.render(textStr, True, Color.BLACK)
            x = self.SCREEN_WIDTH // 2
            y = self.SCREEN_HEIGHT // 2 - 50
            textrect = text.get_rect(center=(x, y))
            self.screen.blit(text, textrect)

            mx, my = pygame.mouse.get_pos()
            xButton = x - 100
            yButton = textrect.y + 50
            self.btn_go_back_error = pygame.Rect(xButton, yButton, 200, 50)
            is_hover = self.btn_go_back_error.collidepoint(mx, my)
            # Button colors
            button_color = Color.HOVER_COLOR if is_hover else Color.WHITE
            text_color = Color.RED if is_hover else Color.BLUE

            # Draw button rectangle

            pygame.draw.rect(self.screen, button_color, self.btn_go_back_error)
            pygame.draw.rect(
                self.screen, Color.BLACK, self.btn_go_back_error, 2
            )  # Border

            # Draw text on button
            text_surf, text_rect = Utils.draw_text(
                "Go back", text_color, x, textrect.y + 75
            )
            self.screen.blit(text_surf, text_rect)

        pygame.display.update()

    def draw_waiting_join_game(self):
        font = pygame.font.Font(None, 36)
        textStr = "Waiting to join game..."
        text = font.render(textStr, True, Color.BLACK)
        x = self.SCREEN_WIDTH // 2
        y = self.SCREEN_HEIGHT // 2
        textrect = text.get_rect(center=(x, y))
        self.screen.fill(Color.WHITE)
        self.screen.blit(text, textrect)

    def draw_waiting_opponent_join(self):
        font = pygame.font.Font(None, 36)
        textStr = "Waiting for opponent to join..."
        text = font.render(textStr, True, Color.WHITE)
        x = self.SCREEN_WIDTH // 2
        y = self.SCREEN_HEIGHT // 2
        textrect = text.get_rect(center=(x, y))

        pygame.draw.rect(
            self.screen,
            Color.BLACK,
            (
                textrect.x - 10,
                textrect.y - 10,
                textrect.width + 20,
                textrect.height + 20,
            ),
        )
        self.screen.blit(text, textrect)

    def draw_opponent_left(self):
        self.screen.fill(Color.WHITE)
        font = pygame.font.Font(None, 36)
        textStr = "Your opponent has left the game!"
        text = font.render(textStr, True, Color.BLACK)
        x = self.SCREEN_WIDTH // 2
        y = self.SCREEN_HEIGHT // 2 - 50
        textrect = text.get_rect(center=(x, y))

        self.screen.blit(text, textrect)

        mx, my = pygame.mouse.get_pos()
        xButton = x - 100
        yButton = textrect.y + 50
        self.btn_go_back_error = pygame.Rect(xButton, yButton, 200, 50)
        is_hover = self.btn_go_back_error.collidepoint(mx, my)
        # Button colors
        button_color = Color.HOVER_COLOR if is_hover else Color.WHITE
        text_color = Color.RED if is_hover else Color.BLUE

        # Draw button rectangle

        pygame.draw.rect(self.screen, button_color, self.btn_go_back_error)
        pygame.draw.rect(self.screen, Color.BLACK, self.btn_go_back_error, 2)  # Border

        # Draw text on button
        text_surf, text_rect = Utils.draw_text(
            "Go back", text_color, x, textrect.y + 75
        )
        self.screen.blit(text_surf, text_rect)

    def check_hover_cell(self):
        # Các lớp kế thừa có thể xử lý sự kiện hover riêng
        if (
            self.winner == 0
            and self.isStart
            and self.isJoined
            and self.isMove
            and self.isOpponentLeft == False
        ):
            return True

        return False

    def handle_move(self):
        hover_pos = self.get_hover_cell()
        if hover_pos == None:
            return
        col, row = hover_pos
        # Chỉ được đánh vào những ô trống và đến lượt của mình
        if self.board[row][col] == 0 and self.isMove == True:
            self.sio.emit("move", {"game_id": self.game_id, "row": row, "col": col})

    def listen_socket_events(self):
        self.sio.on("connect", self.handle_connect_event)
        self.sio.on("joined", self.handle_joined_event)
        self.sio.on("start_game", self.handle_start_game_event)
        self.sio.on("starting_player", self.handle_starting_player_event)
        self.sio.on("move", self.handle_move_event)
        self.sio.on("undo_move", self.handle_undo_move_event)
        self.sio.on("opponent_left", self.handle_opponent_left_event)
        self.sio.on("game_over", self.handle_game_over_event)
        self.sio.on("reset_game", self.handle_reset_game_event)

    def handle_connect_event(self):
        print("Connected to server")

    def handle_joined_event(self, data):
        self.isJoined = True
        self.game_id = data["game_id"]
        self.player_current_id = data["player_id"]
        print("Đã vào phòng game: ", self.game_id)

    def handle_start_game_event(self, data):
        self.isStart = True

    def handle_starting_player_event(self, data):
        turn_player_id = data["player_id"]

        if self.player_current_id == turn_player_id:
            self.isMove = True
            self.turn_player_name = "You"
        else:
            self.isMove = False
            self.turn_player_name = "Opponent"

    def handle_move_event(self, data):
        row = data["row"]
        col = data["col"]
        piece = data["piece"]
        if self.board[row][col] == 0:
            self.board[row][col] = piece

    def handle_undo_move_event(self, data):
        # Revert the board to the state before the last move
        prev_move = data["prev_move"]  # Remove the last move
        prev_piece, prev_row, prev_col = prev_move
        self.board[prev_row][prev_col] = 0  # Reset the cell to empty

    def handle_game_over_event(self, data):
        self.winning_line = data["winner"]["winning_line"]
        self.winner = data["winner"]["piece"]
        player_id_winner = data["player_id"]

        if self.player_current_id == player_id_winner:
            self.winner_name = "You win!"
        else:
            self.winner_name = "You lose!"

        self.isMove = False

        print("Người chơi thắng: ", self.winner)

    def handle_opponent_left_event(self, data):
        self.isOpponentLeft = True
        self.sio.disconnect()

    def handle_reset_game_event(self, data):
        self.board = np.zeros(
            (self.NUMBER_CELL_GAME_HEIGHT, self.NUMBER_CELL_GAME_WIDTH)
        )
        self.winner = 0
        self.winning_line = None

    def handle_event_more(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_go_back_error != None and self.btn_go_back_error.collidepoint(
                event.pos
            ):
                self.running = False

    def reset(self):
        self.sio.emit("reset_game", {"game_id": self.game_id})

    def run_before(self):
        self.draw_connecting_server()

        if self.sio.connected == False and self.isError == False:
            try:
                self.sio.connect("http://localhost:5000")
                self.sio.emit("join", {})
            except:
                self.isError = True

    def run_after(self):
        try:
            self.sio.disconnect()
        except:
            self.isError = True
