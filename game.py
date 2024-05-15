import pygame
import sys
from endgame import EndGame
import numpy as np
from color import Color
import time


class Game:
    def __init__(self, cell_size, number_cell_width, number_cell_height):
        pygame.init()
        
        self.font = pygame.font.SysFont("Arial", 14, bold=True)
        self.nav_player_font = pygame.font.SysFont("Arial", 16, bold=True)

        self.CELL_SIZE = cell_size
        # Lấy độ cao là 2 ô cho nav bar
        self.NUMBER_CELL_NAV_HEIGHT = 2

        # Màn hình bàn cờ
        self.NUMBER_CELL_GAME_WIDTH = number_cell_width
        self.NUMBER_CELL_GAME_HEIGHT = number_cell_height - self.NUMBER_CELL_NAV_HEIGHT

        # Screen dimensions
        self.SCREEN_WIDTH = self.CELL_SIZE * self.NUMBER_CELL_GAME_WIDTH
        self.SCREEN_HEIGHT = self.CELL_SIZE * (
            self.NUMBER_CELL_GAME_HEIGHT + self.NUMBER_CELL_NAV_HEIGHT
        )

        self.NAV_HEIGHT = self.CELL_SIZE * self.NUMBER_CELL_NAV_HEIGHT
        self.NAV_WIDTH = self.SCREEN_WIDTH

        self.GAME_HEIGHT = self.CELL_SIZE * self.NUMBER_CELL_GAME_HEIGHT
        self.GAME_WIDTH = self.SCREEN_WIDTH

        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))

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
        self.padding = 2  # Padding để hình ảnh không đè lên viền ô
        self.x_img = pygame.image.load("x.png")
        self.o_img = pygame.image.load("o.png")
        self.x_img = pygame.transform.scale(
            self.x_img,
            (self.CELL_SIZE - 2 * self.padding, self.CELL_SIZE - 2 * self.padding),
        )
        self.o_img = pygame.transform.scale(
            self.o_img,
            (self.CELL_SIZE - 2 * self.padding, self.CELL_SIZE - 2 * self.padding),
        )
        
        # nav options
        self.nav_options = ["Player turn", "Reset", "Exit"]
        self.noti_options = ["Winner", "Play again", "Exit"]
        self.nav_rects = []  # To store button rectangles
        self.noti_rects = []

    def draw_screen(self):
        self.draw_nav()
        self.draw_game()

        if self.winner != 0:
            self.draw_end_game()

    def draw_nav(self):
        self.nav_surface.fill(Color.WHITE)
        nav_option_width = 100
        nav_option_height = 30
                
        self.nav_rects = []
        for i, option in enumerate(self.nav_options):
            xButton = self.NAV_WIDTH // 2 + i * 130 - 360 // 2
            yButton = self.NAV_HEIGHT // 2 - nav_option_height // 2
            if(option == "Player turn"): 
                text_surf, text_rect = self.draw_text(f'Player {self.current_player}\'s turn', Color.BLACK, xButton + nav_option_width // 2, yButton + nav_option_height // 2, self.nav_player_font)
                self.nav_surface.blit(text_surf, text_rect)
            else: self.nav_rects.append(self.draw_button( "nav", option, xButton, yButton, nav_option_width, nav_option_height))
        
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

                # Ô đó được hover khi chưa được đánh và chưa có ai thắng
                if (
                    (col, row) == hover_pos
                    and self.board[row][col] == 0
                    and self.winner == 0
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
        
    def draw_text(self, text, color, x, y, font = None):
        if(font):
            textobj = font.render(text, True, color)
        else: textobj = self.font.render(text, True, color)
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
        if(surface_type == "nav"):
            surface = self.nav_surface
            if(self.winner != 0):
                button_color = Color.WHITE
                text_color = Color.BLUE
        elif(surface_type == "screen"):
            surface = self.screen
            
        # Draw button rectangle
        pygame.draw.rect(surface, button_color, button_rect)
        pygame.draw.rect(surface, Color.BLACK, button_rect, 2)  # Border

        # Draw text on button
        text_surf, text_rect = self.draw_text(text, text_color, x + width // 2, y + height // 2)
        surface.blit(text_surf, text_rect)

        return button_rect

    def draw_end_game(self):
        notification_width = 220
        notification_height = 180
        notification_x = self.GAME_WIDTH // 2 - notification_width // 2
        notification_y =  self.GAME_HEIGHT // 2 - notification_height // 2 + self.NAV_HEIGHT

        # Vẽ hình chữ nhật thông báo
        pygame.draw.rect(self.screen, Color.WHITE, [notification_x, notification_y, notification_width, notification_height])
        pygame.draw.rect(self.screen, Color.BLUE, [notification_x, notification_y, notification_width, notification_height], 2)
             
        noti_option_width = 100
        noti_option_height = 30
    
        self.noti_rects = []
        for i, option in enumerate(self.noti_options):
            xButton = notification_x + (notification_width - noti_option_width) // 2
            yButton = notification_y + (notification_height - noti_option_height) // 2 + i*50 - 110 // 2
            if(option == "Winner"): 
                text_surf, text_rect = self.draw_text(f'{option}: Player {self.current_player}', Color.BLACK, xButton + noti_option_width // 2, yButton + noti_option_height // 2, self.nav_player_font)
                self.screen.blit(text_surf, text_rect)
            else: self.noti_rects.append(self.draw_button("screen", option, xButton, yButton, noti_option_width, noti_option_height))
        return None;

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

    def handle_click(self):
        if self.winner != 0:
            return
        hover_pos = self.get_hover_cell()
        if hover_pos == None:
            return
        col, row = hover_pos
        if self.board[row][col] == 0:  # Only update if the cell is empty
            self.board[row][col] = self.current_player
            self.current_player = 1 if self.current_player == 2 else 2  # Switch player
            self.winner = self.check_winner(col, row)

    def check_winner(self, col, row):

        directions = [
            (1, 0),
            (0, 1),
            (1, 1),
            (1, -1),
        ]  # Ngang, dọc, chéo xuôi, chéo ngược

        current_player = self.board[row][col]
        for direction in directions:
            dx, dy = direction
            count = 1  # Đếm số lượng quân liên tiếp
            # Kiểm tra theo hướng của direction
            for i in range(1, 5):
                x = col + i * dx
                y = row + i * dy
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == current_player
                ):
                    count += 1
                else:
                    break
            # Kiểm tra theo hướng đối diện của direction
            for i in range(1, 5):
                x = col - i * dx
                y = row - i * dy
                if (
                    0 <= x < self.NUMBER_CELL_GAME_WIDTH
                    and 0 <= y < self.NUMBER_CELL_GAME_HEIGHT
                    and self.board[y][x] == current_player
                ):
                    count += 1
                else:
                    break

            if count >= 5:  # Nếu có 5 quân liên tiếp, người chơi hiện tại thắng
                return current_player

        return 0  # Trả về 0 nếu không có ai thắng

    def handel_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            pygame.quit()
            sys.exit()

        else:
            if event.type == pygame.MOUSEBUTTONUP:
                # Kiểm tra xem nút nào được nhấn
                if event.button == 1:  # 1 là nút chuột trái
                    self.handle_click()
                for i, rect in enumerate(self.nav_rects):
                    if(self.winner == 0):
                        if rect.collidepoint(event.pos):
                            if i == 0:
                                print("Options clicked")
                                self.board = np.zeros((self.NUMBER_CELL_GAME_HEIGHT, self.NUMBER_CELL_GAME_WIDTH))
                                self.current_player = 1  # X starts first
                                self.winner = 0
                                self.running = True
                            elif i == 1:
                                self.running = False
                for i, rect in enumerate(self.noti_rects):
                    if(self.winner != 0):
                        if (rect.collidepoint(event.pos)):
                            if i == 0:
                                print("Options clicked")
                                self.board = np.zeros((self.NUMBER_CELL_GAME_HEIGHT, self.NUMBER_CELL_GAME_WIDTH))
                                self.current_player = 1  # X starts first
                                self.winner = 0
                                self.running = True
                            elif i == 1:
                                self.running = False

    def run(self):
        # Clear all events before switching screens
        pygame.event.clear()

        while self.running:

            self.draw_screen()
            for event in pygame.event.get():
                self.handel_event(event)


            pygame.display.update()


if __name__ == "__main__":
    game = Game(
        cell_size=30,
        number_cell_width=28,
        number_cell_height=20,
    )
    game.run()
