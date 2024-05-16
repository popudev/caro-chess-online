import pygame
import sys
import numpy as np
from color import Color
import socketio
from asset import Asset
from config import Config
from utils import Utils


class Game:
    def __init__(self, screen):
        self.screen = screen

        self.CELL_SIZE = Config.CELL_SIZE
        # Lấy độ cao là 2 ô cho nav bar
        self.NUMBER_CELL_NAV_HEIGHT = 2

        # Màn hình bàn cờ
        self.NUMBER_CELL_GAME_WIDTH = Config.NUMBER_CELL_WIDTH
        self.NUMBER_CELL_GAME_HEIGHT = (
            Config.NUMBER_CELL_HEIGHT - self.NUMBER_CELL_NAV_HEIGHT
        )

        # Screen dimensions
        self.SCREEN_WIDTH = self.CELL_SIZE * self.NUMBER_CELL_GAME_WIDTH
        self.SCREEN_HEIGHT = self.CELL_SIZE * (
            self.NUMBER_CELL_GAME_HEIGHT + self.NUMBER_CELL_NAV_HEIGHT
        )

        self.NAV_HEIGHT = self.CELL_SIZE * self.NUMBER_CELL_NAV_HEIGHT
        self.NAV_WIDTH = self.SCREEN_WIDTH

        self.GAME_HEIGHT = self.CELL_SIZE * self.NUMBER_CELL_GAME_HEIGHT
        self.GAME_WIDTH = self.SCREEN_WIDTH

        # Tạo bề mặt cho nav bar
        self.nav_surface = pygame.Surface((self.NAV_WIDTH, self.NAV_HEIGHT))

        # Tạo bề mặt cho bàn cờ
        self.game_surface = pygame.Surface((self.GAME_WIDTH, self.GAME_HEIGHT))

        # Khởi tạo dữ liệu bàn cờ là mảng 2 chiều
        self.board = np.zeros(
            (self.NUMBER_CELL_GAME_HEIGHT, self.NUMBER_CELL_GAME_WIDTH)
        )
        self.current_player = 1  # X starts first
        self.winner = 0
        self.running = True

        # Tải ảnh và thay đổi kích thước với padding
        # Padding để hình ảnh không đè lên viền ô
        self.padding = 2
        piece_size = (
            self.CELL_SIZE - 2 * self.padding,
            self.CELL_SIZE - 2 * self.padding,
        )
        self.x_img = pygame.transform.scale(Asset.X_IMG, piece_size)
        self.o_img = pygame.transform.scale(Asset.O_IMG, piece_size)

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

    def draw_screen(self):
        self.screen.fill(Color.WHITE)

        if self.isError:
            self.draw_connecting_server(isError=True)
            return

        if self.isJoined == False:  # Nếu chưa join game
            self.draw_waiting_join_game()
            return

        self.draw_nav()
        self.draw_game()

        if self.isStart == False:
            self.draw_waiting_opponent_join()
            return

        if self.winner != 0:
            self.draw_winning_line()
            self.draw_end_game()

    def draw_nav(self):
        self.nav_surface.fill(Color.WHITE)

        self.screen.blit(self.nav_surface, (0, 0))

    def draw_game(self):
        background_color = Color.WHITE
        border_color = Color.BLACK

        self.game_surface.fill(background_color)
        self.draw_board(border_color)
        self.screen.blit(self.game_surface, (0, self.NAV_HEIGHT))

    def draw_board(self, border_color):
        hover_pos = self.get_hover_cell()

        for row in range(self.NUMBER_CELL_GAME_HEIGHT):
            for col in range(self.NUMBER_CELL_GAME_WIDTH):

                rect = pygame.Rect(
                    col * self.CELL_SIZE,
                    row * self.CELL_SIZE,
                    self.CELL_SIZE,
                    self.CELL_SIZE,
                )

                # Ô đó được hover khi game bắt đầu, chưa được đánh và chưa có ai thắng
                if (
                    (col, row) == hover_pos
                    and self.board[row][col] == 0
                    and self.winner == 0
                    and self.isStart == True
                    and self.isMove == True
                ):
                    # Tô màu cho ô
                    pygame.draw.rect(self.game_surface, Color.HOVER_COLOR, rect)

                # Vẽ viền cho ô
                pygame.draw.rect(self.game_surface, border_color, rect, 1)

                if self.board[row][col] == 1:
                    self.draw_x(col, row)
                elif self.board[row][col] == 2:
                    self.draw_o(col, row)

    def draw_x(self, col, row):
        x_pos = col * self.CELL_SIZE + self.padding
        y_pos = row * self.CELL_SIZE + self.padding
        self.game_surface.blit(self.x_img, (x_pos, y_pos))

    def draw_o(self, col, row):
        x_pos = col * self.CELL_SIZE + self.padding
        y_pos = row * self.CELL_SIZE + self.padding
        self.game_surface.blit(self.o_img, (x_pos, y_pos))

    def draw_winning_line(self):
        if not hasattr(self, "winning_line"):
            return

        start_pos, end_pos = self.winning_line
        start_pixel = (
            start_pos[0] * self.CELL_SIZE + self.CELL_SIZE // 2,
            start_pos[1] * self.CELL_SIZE + self.CELL_SIZE // 2 + self.NAV_HEIGHT,
        )
        end_pixel = (
            end_pos[0] * self.CELL_SIZE + self.CELL_SIZE // 2,
            end_pos[1] * self.CELL_SIZE + self.CELL_SIZE // 2 + self.NAV_HEIGHT,
        )
        color = Color.RED if self.winner == 1 else Color.BLUE
        pygame.draw.line(self.screen, color, start_pixel, end_pixel, 5)

    def draw_end_game(self):
        # self.endgame_screen.draw(self.winner)
        pass

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

    def listen_socket_events(self):
        self.sio.on("connect", self.handle_connect_event)
        self.sio.on("joined", self.handle_joined_event)
        self.sio.on("start_game", self.handle_start_game_event)
        self.sio.on("starting_player", self.handle_starting_player_event)
        self.sio.on("move", self.handle_move_event)
        self.sio.on("undo_move", self.handle_undo_move_event)
        self.sio.on("game_over", self.handle_game_over_event)

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
        else:
            self.isMove = False

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
        print("Người chơi thắng: ", self.winner)

    def get_hover_cell(self):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        col = mouse_x // self.CELL_SIZE
        row = (mouse_y - self.NAV_HEIGHT) // self.CELL_SIZE
        if (
            0 <= col < self.NUMBER_CELL_GAME_WIDTH
            and 0 <= row < self.NUMBER_CELL_GAME_HEIGHT
        ):
            return col, row
        return None

    def handle_move(self):
        if self.winner != 0:
            return
        hover_pos = self.get_hover_cell()
        if hover_pos == None:
            return
        col, row = hover_pos
        # Chỉ được đánh vào những ô trống và đến lượt của mình
        if self.board[row][col] == 0 and self.isMove == True:
            self.sio.emit("move", {"game_id": self.game_id, "row": row, "col": col})

    def handel_game_event(self, event):

        if self.isStart == False:
            return

        if event.type == pygame.MOUSEBUTTONUP:
            # Kiểm tra xem nút nào được nhấn
            if event.button == 1:  # 1 là nút chuột trái
                self.handle_move()

    def run(self):
        clock = pygame.time.Clock()
        self.screen.fill(Color.WHITE)

        self.draw_connecting_server()

        if self.sio.connected == False and self.isError == False:
            try:
                self.sio.connect("http://localhost:5000")
            except:
                self.isError = True

        self.sio.emit("join", {})

        while self.running:
            clock.tick(60)
            self.draw_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

                self.handel_game_event(event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if (
                        self.btn_go_back_error != None
                        and self.btn_go_back_error.collidepoint(event.pos)
                    ):
                        self.running = False

            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()
