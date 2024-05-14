import pygame
import sys


class EndGame:
    def __init__(self, game):
        self.game = game
        self.font = pygame.font.SysFont(None, 40)
        self.text_color = (255, 255, 255)
        self.button_color = (0, 100, 200)
        self.button_text_color = (255, 255, 255)
        self.reset_button_rect = pygame.Rect(
            game.window_size // 2 - 100, game.window_size // 2 + 50, 200, 50
        )
        self.exit_button_rect = pygame.Rect(
            game.window_size // 2 - 100, game.window_size // 2 + 120, 200, 50
        )

    def draw(self, winner):
        winner_text = f"Người chơi {winner} thắng!"
        winner_surface = self.font.render(winner_text, True, self.text_color)
        winner_rect = winner_surface.get_rect(
            center=(self.game.window_size // 2, self.game.window_size // 2)
        )
        self.game.window.blit(winner_surface, winner_rect)

        reset_button_text = "Chơi lại"
        self.draw_button(self.reset_button_rect, self.button_color, reset_button_text)

        exit_button_text = "Thoát"
        self.draw_button(self.exit_button_rect, self.button_color, exit_button_text)

        # pygame.display.flip()

    def draw_button(self, rect, color, text):
        pygame.draw.rect(self.game.window, color, rect)
        button_text = self.font.render(text, True, self.button_text_color)
        button_rect = button_text.get_rect(center=rect.center)
        self.game.window.blit(button_text, button_rect)

    def handle_click(self, pos):
        if self.reset_button_rect.collidepoint(pos):
            self.game.reset()
        elif self.exit_button_rect.collidepoint(pos):
            pygame.quit()
            sys.exit()

    def run(self):
        pass
