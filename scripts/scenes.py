import random
import pygame

from .entities import Collectible, Creature, Diver
from .ui import bar, panel, text


LEVELS = [
    ("ZONA FOTICA", "200 m", (20, 93, 142), 2, ("angler",), 72, 130, 16),
    ("ZONA DISFOTICA", "1.000 m", (12, 64, 111), 3, ("angler", "jelly"), 92, 165, 21),
    ("ZONA AFOTICA", "4.000 m", (8, 38, 75), 4, ("shark", "jelly", "eel"), 115, 205, 27),
    ("ZONA HADAL", "6.000 m", (6, 23, 52), 5, ("shark", "eel", "leviathan"), 140, 250, 34),
    ("ZONA ABISSAL", "10.000 m", (3, 12, 31), 6, ("angler", "eel", "leviathan"), 165, 330, 43),
]


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.bounds = screen.get_rect().inflate(-36, -90)
        self.font = pygame.font.Font(None, 22)
        self.big = pygame.font.Font(None, 48)
        self.title = pygame.font.Font(None, 68)
        self.state = "menu"
        self.best = 0
        self.reset_run()

    def reset_run(self):
        self.level = 0
        self.credits = 0
        self.speed = 165
        self.lamp = 105
        self.tank = 75
        self.start_level()

    def start_level(self):
        name, _, color, count, species, speed, detection, damage = LEVELS[self.level]
        self.oxygen = self.tank
        self.diver = Diver((85, 82), self.speed, self.lamp)
        self.items = []
        self.creatures = []
        for i in range(count):
            x = random.randint(180, self.bounds.right - 60)
            y = random.randint(170, self.bounds.bottom - 30)
            self.items.append(Collectible((x, y), "artefato" if i % 2 == 0 else "mineral"))
        for index in range(count):
            x = random.randint(190, self.bounds.right - 70)
            y = random.randint(140, self.bounds.bottom - 40)
            self.creatures.append(Creature((x, y), species[index % len(species)], speed, detection, damage))
        self.message = f"COLETE {count} AMOSTRAS E VOLTE AO SUBMERSIVEL"
        self.message_time = 3.5

    def event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.state == "menu":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.reset_run()
                self.state = "play"
            elif event.key == pygame.K_h:
                self.state = "help"
        elif self.state == "help":
            self.state = "menu"
        elif self.state == "play":
            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
        elif self.state == "upgrade":
            costs = {pygame.K_1: ("tanque", 35), pygame.K_2: ("propulsor", 35), pygame.K_3: ("lanterna", 35)}
            if event.key in costs:
                item, cost = costs[event.key]
                if self.credits >= cost:
                    self.credits -= cost
                    if item == "tanque": self.tank += 25
                    if item == "propulsor": self.speed += 30
                    if item == "lanterna": self.lamp += 32
                    self.message, self.message_time = "MELHORIA INSTALADA", 2
                else:
                    self.message, self.message_time = "CREDITOS INSUFICIENTES", 2
            if event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.level == 4 and self.lamp < 169:
                self.message, self.message_time = "A ZONA ABISSAL EXIGE LANTERNA NIVEL 2", 3
                return
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self.state = "play"
                self.start_level()
        elif self.state in ("lost", "win"):
            if event.key in (pygame.K_RETURN, pygame.K_SPACE): self.state = "menu"

    def update(self, dt):
        if self.state != "play":
            return
        self.message_time -= dt
        self.oxygen -= dt * (1 + self.level * .18)
        keys = pygame.key.get_pressed()
        self.diver.update(keys, dt, self.bounds)
        for item in self.items: item.update(dt)
        for creature in self.creatures: creature.update(dt, self.diver.position)
        for item in self.items[:]:
            if self.diver.rect.colliderect(item.rect.inflate(10, 10)):
                self.items.remove(item)
                self.credits += 20
                self.message, self.message_time = "+20 CREDITOS", 1.2
        for creature in self.creatures:
            if self.diver.rect.colliderect(creature.rect.inflate(-8, -8)):
                self.oxygen -= creature.damage
                self.diver.position = pygame.Vector2(85, 90)
                self.diver.rect.center = self.diver.position
                self.message, self.message_time = f"ATAQUE: -{creature.damage} O2", 2
        if not self.items and self.diver.rect.centery < 105:
            self.best = max(self.best, self.level + 1)
            if self.level == len(LEVELS) - 1:
                self.state = "win"
            else:
                self.level += 1
                self.state = "upgrade"
        if self.oxygen <= 0:
            self.state = "lost"

    def background(self):
        name, depth, color, _, _, _, _, _ = LEVELS[self.level]
        self.screen.fill(color)
        # pixelated water bands and cavern walls
        for y in range(45, self.screen.get_height(), 28):
            shade = max(0, color[2] - y // 10)
            pygame.draw.rect(self.screen, (color[0] // 2, color[1] // 2, shade), (0, y, self.screen.get_width(), 2))
        random.seed(self.level)
        for x in range(0, self.screen.get_width(), 42):
            height = random.randint(45, 135)
            pygame.draw.polygon(self.screen, (4, 18, 39), [(x, 45), (x + 25, 45), (x + 36, 45 + height), (x, 65 + height)])
        for x in range(0, self.screen.get_width(), 56):
            height = random.randint(50, 118)
            pygame.draw.polygon(self.screen, (3, 15, 34), [(x, self.bounds.bottom), (x + 45, self.bounds.bottom), (x + 28, self.bounds.bottom - height)])
        # coral and luminous flora: small layered pixel-art details
        for x in range(55, self.screen.get_width(), 96):
            base = self.bounds.bottom - 13 - ((x * 3 + self.level * 9) % 25)
            glow = (46, 213, 186) if self.level > 1 else (232, 118, 146)
            pygame.draw.rect(self.screen, glow, (x, base - 18, 4, 18))
            pygame.draw.rect(self.screen, glow, (x - 8, base - 12, 16, 4))
            pygame.draw.rect(self.screen, (18, 104, 107), (x + 5, base - 11, 4, 11))
        # the surface extraction craft
        pygame.draw.rect(self.screen, (164, 208, 207), (30, 43, 122, 21))
        pygame.draw.rect(self.screen, (230, 251, 247), (48, 30, 62, 14))
        pygame.draw.rect(self.screen, (238, 185, 70), (52, 64, 75, 4))
        for x in range(80, self.screen.get_width(), 126):
            y = 125 + (x * 7 + self.level * 19) % 330
            pygame.draw.rect(self.screen, (52, 168, 175), (x, y, 4, 10))
            pygame.draw.rect(self.screen, (38, 125, 141), (x - 4, y + 4, 12, 4))

    def draw_play(self):
        self.background()
        for item in self.items: item.draw(self.screen)
        for creature in self.creatures: creature.draw(self.screen)
        self.diver.draw(self.screen)
        # darkness with a transparent hole around the lamp
        dark = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        final_dive = self.level == 4
        dark.fill((0, 0, 5, 248 if final_dive else 80 + self.level * 28))
        pygame.draw.circle(dark, (0, 0, 0, 0), self.diver.rect.center, self.lamp if not final_dive else max(48, self.lamp - 42))
        self.screen.blit(dark, (0, 0))
        panel(self.screen, pygame.Rect(12, 8, 300, 30))
        text(self.screen, self.font, f"{LEVELS[self.level][0]}  |  {LEVELS[self.level][1]}", (20, 16))
        panel(self.screen, pygame.Rect(670, 8, 278, 30))
        text(self.screen, self.font, "O2", (680, 16), (159, 235, 255))
        bar(self.screen, pygame.Rect(710, 14, 126, 16), max(0, self.oxygen), self.tank, (67, 218, 232) if self.oxygen > 20 else (240, 92, 79))
        text(self.screen, self.font, f"{self.credits:03d} C", (850, 16), (255, 221, 111))
        remaining = len(self.items)
        text(self.screen, self.font, f"AMOSTRAS: {remaining}  |  AMEACAS: {len(self.creatures)}", (15, 548), (220, 244, 248))
        if self.message_time > 0:
            panel(self.screen, pygame.Rect(245, 512, 470, 32), (8, 27, 49), (76, 201, 202))
            text(self.screen, self.font, self.message, (480, 528), center=True)

    def draw_center(self, heading, lines, footer):
        self.background()
        shade = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA); shade.fill((0, 4, 12, 180)); self.screen.blit(shade, (0, 0))
        panel(self.screen, pygame.Rect(154, 92, 652, 390), (6, 28, 50), (74, 210, 217))
        text(self.screen, self.title, heading, (480, 150), (114, 237, 237), True)
        for index, line in enumerate(lines): text(self.screen, self.font, line, (480, 225 + index * 32), center=True)
        text(self.screen, self.font, footer, (480, 442), (255, 220, 111), True)

    def draw(self):
        if self.state == "play": self.draw_play()
        elif self.state == "menu": self.draw_center("SUBAQUATICA", ["Explore as fossas, encontre amostras e retorne antes do oxigenio acabar.", "Cinco zonas oceanicas. Criaturas territoriais. Escuridao total."], "[ENTER] MERGULHAR     [H] COMO JOGAR")
        elif self.state == "help": self.draw_center("CONTROLES", ["WASD ou SETAS - mover o mergulhador", "Colete todas as amostras e volte ao submarino no alto da tela.", "Criaturas detectam e perseguem voce. Cada zona aumenta a ameaca.", "A Zona Abissal exige duas melhorias de lanterna."], "PRESSIONE QUALQUER TECLA PARA VOLTAR")
        elif self.state == "upgrade": self.draw_center("ESTACAO DE MELHORIAS", [f"CREDITOS DISPONIVEIS: {self.credits}", "[1] TANQUE +25 O2 - 35 C", "[2] PROPULSOR +30 VELOCIDADE - 35 C", "[3] LANTERNA +32 ALCANCE - 35 C"], "[ENTER] DESCER PARA A PROXIMA ZONA")
        elif self.state == "lost": self.draw_center("OXIGENIO ESGOTADO", ["A fossa venceu esta expedicao.", f"ZONAS ALCANCADAS: {self.best}/5"], "[ENTER] VOLTAR AO MENU")
        elif self.state == "win": self.draw_center("EXPEDICAO CONCLUIDA", ["Voce trouxe amostras das cinco zonas oceanicas.", "A Zona Abissal agora guarda seus segredos no laboratorio."], "[ENTER] VOLTAR AO MENU")
