import pygame


class Utils:
    def draw_text(text, color, x, y):
        font = pygame.font.SysFont("Arial", 36, bold=True)
        textobj = font.render(text, True, color)
        textrect = textobj.get_rect(center=(x, y))
        return textobj, textrect
