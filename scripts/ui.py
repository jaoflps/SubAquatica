import pygame


def text(surface, font, value, position, color=(238, 248, 255), center=False):
    image = font.render(value, False, color)
    rect = image.get_rect(center=position) if center else image.get_rect(topleft=position)
    surface.blit(image, rect)
    return rect


def panel(surface, rect, fill=(8, 28, 51), border=(72, 181, 208)):
    pygame.draw.rect(surface, fill, rect)
    pygame.draw.rect(surface, border, rect, 2)


def bar(surface, rect, value, maximum, color):
    pygame.draw.rect(surface, (3, 15, 28), rect)
    width = max(0, int(rect.width * value / maximum))
    pygame.draw.rect(surface, color, (rect.x + 2, rect.y + 2, max(0, width - 4), rect.height - 4))
    pygame.draw.rect(surface, (206, 239, 248), rect, 1)
