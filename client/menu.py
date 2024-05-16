import pygame
import sys
from game_offline import GameOffline
from asset import Asset
from config import Config
from game_online import GameOnline
from game_ai import GameAI


class Menu:
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        self.CELL_SIZE = Config.CELL_SIZE
        self.NUMBER_CELL_WIDTH = Config.NUMBER_CELL_WIDTH
        self.NUMBER_CELL_HEIGHT = Config.NUMBER_CELL_HEIGHT

        # Screen dimensions
        self.SCREEN_WIDTH = self.CELL_SIZE * self.NUMBER_CELL_WIDTH
        self.SCREEN_HEIGHT = self.CELL_SIZE * self.NUMBER_CELL_HEIGHT

        # Colors
        self.WHITE = (255, 255, 255)
        self.GRAY = (200, 200, 200)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 191, 255)
        self.RED = (255, 0, 0)

        # Load background image and scale it to fit the screen
        self.background_image = pygame.transform.scale(
            Asset.BACKGROUND_IMG, (self.SCREEN_WIDTH, self.SCREEN_HEIGHT)
        )

        # Create screen
        self.screen = pygame.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        pygame.display.set_caption("Game Caro")

        # Font settings (bold)
        self.font = pygame.font.SysFont("Arial", 36, bold=True)

        # Menu options
        self.menu_options = [
            "Start Online",
            "Start 2 Player",
            "Start Bot",
            "Exit",
        ]
        self.menu_rects = []  # To store button rectangles
        
        self.button_sound = pygame.mixer.Sound('res/mp3/click.mp3')
        pygame.mixer.music.load('res/mp3/fight.mp3')
        pygame.mixer.music.play(loops=-1)
        
    def play_sounds(self, sound): 
        sound.play()

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
        clock = pygame.time.Clock()

        while True:
            clock.tick(60)
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
                            pygame.mixer.music.stop()
                            self.play_sounds(self.button_sound)
                            if i == 0:

                                self.start_game_online()
                            elif i == 1:

                                self.start_game_offine()

                            elif i == 2:
                                self.start_game_bot()

                            elif i == 3:
                                pygame.quit()
                                sys.exit()

            pygame.display.update()

    def start_game_online(self):
        game = GameOnline(screen=self.screen)
        game.run()

    def start_game_offine(self):
        game = GameOffline(screen=self.screen)
        game.run()

    def start_game_bot(self):
        game = GameAI(screen=self.screen)
        game.run()


if __name__ == "__main__":
    game_menu = Menu()
    game_menu.run()
