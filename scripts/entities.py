import math
import random
import pygame

PIXEL = 4


def pixel_sprite(rows, palette):
    """Turns compact character maps into crisp, scaled pixel-art surfaces."""
    surface = pygame.Surface((len(rows[0]), len(rows)), pygame.SRCALPHA)
    for y, row in enumerate(rows):
        for x, cell in enumerate(row):
            if cell != ".": surface.set_at((x, y), palette[cell])
    return pygame.transform.scale(surface, (surface.get_width() * PIXEL, surface.get_height() * PIXEL))


DIVER = pixel_sprite(["...bbbb...", ".ccwwcc..", ".cwwwwc..", ".cttttc..", "..cttc...", ".orTTrro.", ".oTbbTTo.", "..TbbT...", ".gg..gg.."], {"b": (37, 87, 125), "c": (92, 212, 230), "w": (205, 252, 255), "t": (19, 49, 79), "o": (226, 116, 55), "r": (168, 63, 42), "T": (38, 142, 176), "g": (50, 80, 103)})

CREATURES = {
    "angler": ([".....y......", "....y.......", "...g........", ".gggggg.....", "ggwgggg.....", ".gggggtt....", "..gggg......", "...g........"], {"g": (44, 158, 137), "w": (230, 255, 242), "t": (235, 218, 148), "y": (255, 232, 94)}),
    "shark": ([".....n......", "....nn......", ".bbbbbbbb...", "bbbeebbbbbb", ".bbbbbbbb...", "...bb.......", "..b..b......"], {"b": (79, 128, 157), "n": (50, 87, 115), "e": (255, 231, 178)}),
    "jelly": (["...pppp...", ".ppwwwwpp.", ".pwpwwpwp.", ".pppppppp.", "..p.p.p...", ".p..p..p..", "p...p...p."], {"p": (181, 79, 224), "w": (238, 190, 255)}),
    "eel": (["..lllllll..", ".llgggggll.", "llggwgggll", ".llgggggll.", "..lllllll.."], {"l": (28, 93, 101), "g": (74, 197, 161), "w": (252, 239, 127)}),
    "leviathan": (["....m.......", "...mmm......", ".mmmmmmmm...", "mmrmmmmmrrrr", "mmmwmmmmrrrr", ".mmmmmmmm...", "..mm..mm....", ".m......m..."], {"m": (108, 49, 125), "r": (62, 27, 84), "w": (255, 125, 107)}),
}


class Diver:
    def __init__(self, position, speed, lamp_radius):
        self.image = DIVER; self.rect = self.image.get_rect(center=position)
        self.position = pygame.Vector2(self.rect.center); self.speed, self.lamp_radius = speed, lamp_radius; self.direction = pygame.Vector2(1, 0)

    def update(self, keys, dt, bounds):
        move = pygame.Vector2(keys[pygame.K_d] - keys[pygame.K_a] + keys[pygame.K_RIGHT] - keys[pygame.K_LEFT], keys[pygame.K_s] - keys[pygame.K_w] + keys[pygame.K_DOWN] - keys[pygame.K_UP])
        if move.length_squared(): self.direction = move.normalize(); self.position += self.direction * self.speed * dt
        self.position.x = max(bounds.left + 22, min(bounds.right - 22, self.position.x)); self.position.y = max(bounds.top + 22, min(bounds.bottom - 22, self.position.y)); self.rect.center = round(self.position.x), round(self.position.y)

    def draw(self, screen): screen.blit(self.image if self.direction.x >= 0 else pygame.transform.flip(self.image, True, False), self.rect)


class Creature:
    def __init__(self, position, species, speed, detection, damage):
        rows, palette = CREATURES[species]; self.image = pixel_sprite(rows, palette)
        self.species, self.speed, self.detection, self.damage = species, speed, detection, damage
        self.position = pygame.Vector2(position); self.home = pygame.Vector2(position); self.phase = random.random() * math.tau; self.rect = self.image.get_rect(center=position); self.chasing = False

    def update(self, dt, target):
        distance = self.position.distance_to(target); self.chasing = distance < self.detection
        if self.chasing and distance > 3: self.position += (target - self.position).normalize() * self.speed * dt
        else:
            self.phase += dt; self.position += pygame.Vector2(math.cos(self.phase * 1.3), math.sin(self.phase * 1.9)) * (self.speed * .18 * dt)
            if self.position.distance_to(self.home) > 80: self.position += (self.home - self.position).normalize() * self.speed * .25 * dt
        self.rect.center = round(self.position.x), round(self.position.y)

    def draw(self, screen):
        screen.blit(self.image if not self.chasing or self.position.x < self.home.x else pygame.transform.flip(self.image, True, False), self.rect)
        if self.chasing: pygame.draw.rect(screen, (255, 102, 110), (self.rect.centerx - 2, self.rect.top - 7, 4, 3))


class Collectible:
    def __init__(self, position, kind): self.position, self.kind = pygame.Vector2(position), kind; self.rect = pygame.Rect(0, 0, 18, 18); self.rect.center = position; self.bob = random.random() * math.tau
    def update(self, dt): self.bob += dt * 2; self.rect.centery = round(self.position.y + math.sin(self.bob) * 3)
    def draw(self, screen):
        x, y = self.rect.center
        if self.kind == "artefato":
            pygame.draw.rect(screen, (111, 69, 46), (x - 7, y - 7, 14, 14)); pygame.draw.rect(screen, (236, 183, 79), (x - 5, y - 5, 10, 10)); pygame.draw.rect(screen, (255, 241, 165), (x - 2, y - 4, 4, 4))
        else:
            pygame.draw.polygon(screen, (66, 151, 170), [(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)]); pygame.draw.polygon(screen, (139, 250, 220), [(x, y - 6), (x + 3, y), (x, y + 4), (x - 3, y)]); pygame.draw.rect(screen, (219, 255, 247), (x - 1, y - 4, 2, 5))
