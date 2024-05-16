import pygame
import sys

# Initialize Pygame
pygame.init()

# Set up the screen
WIDTH, HEIGHT = 400, 300
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Input Box with Label")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 32)


def draw_text(surface, text, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(centery=(y))
    surface.blit(text_surface, text_rect)


class InputBox:
    def __init__(self, x, y, width, height, text=""):
        self.input_surface = pygame.Surface((width, height))
        self.rect = pygame.Rect(x, y, width, height)

        self.border_color = BLACK
        self.text = text
        self.font = pygame.font.Font(None, 32)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.border_color = BLUE if self.active else BLACK
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ""
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def update(self):
        width = max(200, self.font.size(self.text)[0] + 10)
        self.rect.w = width

    def draw(self, surface):
        self.input_surface.fill(BLACK)
        pygame.draw.rect(self.input_surface, self.border_color, self.rect, 1)
        surface.blit(self.input_surface, self.rect)


class Label:
    def __init__(self, text, x, y):
        self.text = text
        self.x = x
        self.y = y
        self.font = pygame.font.Font(None, 24)

    def draw(self, surface):
        draw_text(surface, self.text, BLACK, self.x, self.y)


# Input box
input_label = Label("Name:", 50, 80)
input_box = InputBox(120, 100, 200, 40)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        input_box.handle_event(event)

    screen.fill(WHITE)
    input_label.draw(screen)
    input_box.update()
    input_box.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
