import pygame
import sys
from game import Game
import time


class Menu:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        self.CELL_SIZE = 30
        self.NUMBER_CELL_WIDTH = 28
        self.NUMBER_CELL_HEIGHT = 20

        # Screen dimensions
        self.SCREEN_WIDTH = self.CELL_SIZE * self.NUMBER_CELL_WIDTH
        self.SCREEN_HEIGHT = self.CELL_SIZE * self.NUMBER_CELL_HEIGHT

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 191, 255)  # Light Sea Blue
        self.RED = (255, 0, 0)

        # Load background image and scale it to fit the screen
        self.background_image = pygame.image.load("background.jpg")
        self.background_image = pygame.transform.scale(
            self.background_image, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        # Create screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Game Caro")

        # Font settings (bold)
        self.font = pygame.font.SysFont("Arial", 36, bold=True)

        # Menu options
        self.menu_options = ["Start Game", "Options", "Exit"]
        self.menu_rects = []  # To store button rectangles

    def draw_text(self, text, color, x, y):
        textobj = self.font.render(text, True, color)
        textrect = textobj.get_rect(center=(x, y))
        return textobj, textrect

    def draw_button(self, text, x, y):
        mx, my = pygame.mouse.get_pos()
        button_rect = pygame.Rect(x - 100, y - 25, 200, 50)
        is_hover = button_rect.collidepoint(mx, my)
        # Button colors
        button_color = self.GRAY if is_hover else self.WHITE
        text_color = self.RED if is_hover else self.BLUE

        # Draw button rectangle

        pygame.draw.rect(self.screen, button_color, button_rect)
        pygame.draw.rect(self.screen, self.BLACK, button_rect, 2)  # Border

        # Draw text on button
        text_surf, text_rect = self.draw_text(text, text_color, x, y)
        self.screen.blit(text_surf, text_rect)

        return button_rect

    def run(self):

        while True:
            self.screen.blit(self.background_image, (0, 0))

            # Draw menu options and store their rects

            # Draw menu options and store their rects
            self.menu_rects = []
            for i, option in enumerate(self.menu_options):
                xButton = self.SCREEN_WIDTH // 2
                yButton = 220 + i * 60
                self.menu_rects.append(self.draw_button(option, xButton, yButton))

            # Event handling
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, rect in enumerate(self.menu_rects):
                        if rect.collidepoint(event.pos):
                            if i == 0:
                                print("Start Game clicked")
                                self.start_game()
                            elif i == 1:
                                print("Options clicked")
                                self.show_options()
                            elif i == 2:
                                pygame.quit()
                                sys.exit()

            pygame.display.update()

    def start_game(self):
        # Switch to loading screen
        self.screen.fill(self.WHITE)
        loading_text, loading_rect = self.draw_text(
            "Loading...", self.BLACK, self.SCREEN_WIDTH // 2, self.SCREEN_HEIGHT // 2
        )
        self.screen.blit(loading_text, loading_rect)
        pygame.display.update()

        # Simulate loading time
        time.sleep(2)
        # Placeholder for starting the game
        game = Game(
            cell_size=self.CELL_SIZE,
            number_cell_width=self.NUMBER_CELL_WIDTH,
            number_cell_height=self.NUMBER_CELL_HEIGHT,
        )
        game.run()
        # Here you would initialize your game or switch to the game screen
        # Example:
        # self.run_game()

    def show_options(self):
        # Placeholder for options menu
        print("Showing options...")
        # Here you would show your options screen or logic
        # Example:
        # self.run_options()


if __name__ == "__main__":
    game_menu = Menu()
    game_menu.run()
