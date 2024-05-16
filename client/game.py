from config import Config
from asset import Asset
import pygame
import numpy as np
from color import Color
import sys


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.nav_player_font = pygame.font.SysFont("Arial", 16, bold=True)
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
        self.winning_line = None
        self.winner = 0
        self.running = True
        self.isStart = False
        self.turn_player_name = ""
        self.winner_name = ""

        # Tải ảnh và thay đổi kích thước với padding
        # Padding để hình ảnh không đè lên viền ô
        self.padding = 2
        piece_size = (
            self.CELL_SIZE - 2 * self.padding,
            self.CELL_SIZE - 2 * self.padding,
        )
        self.x_img = pygame.transform.scale(Asset.X_IMG, piece_size)
        self.o_img = pygame.transform.scale(Asset.O_IMG, piece_size)

        # Các nút trên navbar
        self.nav_options_start_game = ["Start", "Exit"]
        self.nav_options_starting_game = ["Player turn", "Reset", "Exit"]
        self.nav_rects = []  # Lưu trữ nút để xử lý sự kiện click

        # Các nút thông báo
        self.noti_options = ["Winner", "Play again", "Exit"]
        self.noti_rects = []  # Lưu trữ nút để xử lý sự kiện click

        self.button_sound = pygame.mixer.Sound("res/mp3/click.mp3")
        self.move_sound = pygame.mixer.Sound("res/mp3/pop.mp3")
        self.victory_sound = pygame.mixer.Sound("res/mp3/victory.mp3")
        self.gameover_sound = pygame.mixer.Sound("res/mp3/gameover.mp3")

    def play_sounds(self, sound):
        sound.play()

    def draw_screen(self):
        self.screen.fill(Color.WHITE)
        self.nav_rects = []
        self.draw_nav()
        self.draw_game()

        if self.winner != 0:
            self.draw_winning_line()
            self.draw_end_game()

    def draw_nav(self):
        self.nav_surface.fill(Color.WHITE)
        nav_option_width = 100
        nav_option_height = 30
        nav_options = self.nav_options_start_game

        if self.isStart:
            nav_options = self.nav_options_starting_game

        self.nav_rects = []
        number_btn = len(nav_options)
        for i, option in enumerate(nav_options):
            xButton = (
                self.NAV_WIDTH // 2
                + i * 130
                - (number_btn * 100 + (number_btn - 1) * 30) // 2
            )
            yButton = self.NAV_HEIGHT // 2 - nav_option_height // 2
            if option == "Player turn":
                text_surf, text_rect = self.draw_text(
                    f"{ self.turn_player_name }'s turn",
                    Color.BLACK,
                    xButton + nav_option_width // 2,
                    yButton + nav_option_height // 2,
                    self.nav_player_font,
                )
                self.nav_surface.blit(text_surf, text_rect)
            else:
                btn = self.draw_button(
                    "nav",
                    option,
                    xButton,
                    yButton,
                    nav_option_width,
                    nav_option_height,
                )
                self.nav_rects.append({"rect": btn, "option": option})

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
                if (col, row) == hover_pos and self.board[row][col] == 0:
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
        notification_width = 220
        notification_height = 180
        notification_x = self.GAME_WIDTH // 2 - notification_width // 2
        notification_y = (
            self.GAME_HEIGHT // 2 - notification_height // 2 + self.NAV_HEIGHT
        )

        # Vẽ hình chữ nhật thông báo
        pygame.draw.rect(
            self.screen,
            Color.WHITE,
            [notification_x, notification_y, notification_width, notification_height],
        )
        pygame.draw.rect(
            self.screen,
            Color.BLUE,
            [notification_x, notification_y, notification_width, notification_height],
            2,
        )

        noti_option_width = 100
        noti_option_height = 30

        self.noti_rects = []
        for i, option in enumerate(self.noti_options):
            xButton = notification_x + (notification_width - noti_option_width) // 2
            yButton = (
                notification_y
                + (notification_height - noti_option_height) // 2
                + i * 50
                - 110 // 2
            )
            if option == "Winner":
                text_surf, text_rect = self.draw_text(
                    f"{self.winner_name}",
                    Color.BLACK,
                    xButton + noti_option_width // 2,
                    yButton + noti_option_height // 2,
                    self.nav_player_font,
                )
                self.screen.blit(text_surf, text_rect)
            else:
                self.noti_rects.append(
                    self.draw_button(
                        "screen",
                        option,
                        xButton,
                        yButton,
                        noti_option_width,
                        noti_option_height,
                    )
                )
        return None

    def draw_text(self, text, color, x, y, font=None):
        if font:
            textobj = font.render(text, True, color)
        else:
            textobj = self.font.render(text, True, color)
        textrect = textobj.get_rect(center=(x, y))
        return textobj, textrect

    def draw_button(self, surface_type, text, x, y, width, height):
        mx, my = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x, y, width, height)
        is_hover = button_rect.collidepoint(mx, my)
        # Button colors
        button_color = Color.GRAY if is_hover else Color.WHITE
        text_color = Color.RED if is_hover else Color.BLUE

        surface = self.game_surface
        if surface_type == "nav":
            surface = self.nav_surface
            if self.winner != 0:
                button_color = Color.WHITE
                text_color = Color.BLUE
        elif surface_type == "screen":
            surface = self.screen

        # Draw button rectangle
        pygame.draw.rect(surface, button_color, button_rect)
        pygame.draw.rect(surface, Color.BLACK, button_rect, 2)  # Border

        # Draw text on button
        text_surf, text_rect = self.draw_text(
            text, text_color, x + width // 2, y + height // 2
        )
        surface.blit(text_surf, text_rect)

        return button_rect

    def check_hover_cell(self):
        # Các lớp kế thừa có thể xử lý sự kiện hover riêng
        if self.winner == 0 and self.isStart:
            return True

        return False

    def get_hover_cell(self):
        if not self.check_hover_cell():
            return None

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
        # Các lớp con có thể xử lý sự kiện đánh cờ riêng
        # Online thì emit đến server
        # Offline thì ghi lại dữ liệu
        print("handle_move")
        pass

    def handle_event_more(self, event):
        # Các lớp con có thể xử lý thêm sư kiện
        pass

    def handel_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()

        else:
            # Các lớp con có thể xử lý thêm sự kiện
            self.handle_event_more(event)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Sự kiện đánh cờ được các lớp con xử lý riêng
                if self.isStart:
                    self.handle_move()

                for i, nav_item in enumerate(self.nav_rects):
                    if self.winner == 0:
                        if nav_item["rect"].collidepoint(event.pos):
                            self.play_sounds(self.button_sound)
                            if nav_item["option"] == "Start":
                                self.isStart = True

                            elif nav_item["option"] == "Exit":
                                self.running = False
                                pygame.mixer.music.play(loops=-1)

                            elif nav_item["option"] == "Reset" and self.isStart:
                                self.reset()

                for i, rect in enumerate(self.noti_rects):
                    if self.winner != 0:
                        if rect.collidepoint(event.pos):
                            self.play_sounds(self.button_sound)
                            if i == 0:
                                self.reset()
                            elif i == 1:
                                self.running = False
                                pygame.mixer.music.play(loops=-1)

    def reset(self):
        # Các lớp kế thừa sẽ xử lý
        pass

    def run_before(self):
        pass

    def run_after(self):
        pass

    def run(self):
        clock = pygame.time.Clock()
        self.screen.fill(Color.WHITE)
        # Clear all events before switching screens
        pygame.event.clear()

        self.run_before()

        while self.running:
            clock.tick(60)

            self.draw_screen()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    pygame.quit()
                    sys.exit()

                self.handel_event(event)

            pygame.display.update()

        self.run_after()
