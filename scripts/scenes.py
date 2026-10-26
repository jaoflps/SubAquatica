import random
import pygame

from .entities import Collectible, Creature, Diver
from .ui import bar, panel, text


LEVELS = [
    {"name": "ZONA FOTICA", "depth": "100 m", "color": (22, 112, 164), "items": 2, "species": ("angler",), "speed": 45, "detect": 90, "damage": 7, "theme": "coral", "brief": "Aprenda a coletar amostras e retornar ao submarino."},
    {"name": "JARDIM DE CORAIS", "depth": "500 m", "color": (15, 87, 139), "items": 2, "species": ("angler", "jelly"), "speed": 55, "detect": 110, "damage": 9, "theme": "garden", "brief": "Corais densos escondem perolas e aguas-vivas."},
    {"name": "CANION CREPUSCULAR", "depth": "1.200 m", "color": (10, 62, 108), "items": 3, "species": ("shark", "jelly", "eel"), "speed": 70, "detect": 135, "damage": 12, "theme": "canyon", "brief": "O canyon reduz a visibilidade e atrai predadores."},
    {"name": "CAVERNA AFOTICA", "depth": "3.000 m", "color": (7, 44, 83), "items": 3, "species": ("shark", "eel", "crab"), "speed": 82, "detect": 155, "damage": 15, "theme": "cave", "brief": "Cristais revelam o caminho dentro da caverna escura."},
    {"name": "RUINAS AFUNDADAS", "depth": "4.500 m", "color": (6, 34, 67), "items": 4, "species": ("crab", "ghost", "eel"), "speed": 95, "detect": 175, "damage": 18, "theme": "ruins", "brief": "Recupere reliquias antigas protegidas por sentinelas."},
    {"name": "FOSSA HADAL", "depth": "6.500 m", "color": (4, 25, 53), "items": 4, "species": ("shark", "leviathan", "eel"), "speed": 108, "detect": 195, "damage": 21, "theme": "trench", "brief": "A pressao aumenta. Evite os leviatas da fossa."},
    {"name": "BOSQUE BIOLUMINESCENTE", "depth": "8.000 m", "color": (4, 20, 48), "items": 4, "species": ("ghost", "jelly", "leviathan"), "speed": 122, "detect": 215, "damage": 24, "theme": "forest", "brief": "As luzes do bosque atraem criaturas invisiveis."},
    {"name": "ZONA ABISSAL", "depth": "10.000 m", "color": (2, 10, 29), "items": 5, "species": ("angler", "ghost", "leviathan", "eel"), "speed": 138, "detect": 240, "damage": 27, "theme": "abyss", "brief": "Expedicao final: escuridao total e perigos extremos."},
]


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.bounds = screen.get_rect().inflate(-36, -90)
        self.font, self.title = pygame.font.Font(None, 22), pygame.font.Font(None, 62)
        self.state, self.best = "menu", 0
        self.reset_run()

    @property
    def stage(self):
        return LEVELS[self.level]

    def reset_run(self):
        self.level, self.credits = 0, 0
        self.speed, self.lamp, self.tank = 185, 135, 120
        self.start_level()

    def start_level(self):
        stage = self.stage
        self.oxygen, self.hurt_timer = self.tank, 0
        self.diver = Diver((85, 82), self.speed, self.lamp)
        types = ("artefato", "mineral", "perola", "cristal")
        self.items = [Collectible((random.randint(185, self.bounds.right - 60), random.randint(170, self.bounds.bottom - 35)), types[(i + self.level) % len(types)]) for i in range(stage["items"])]
        self.creatures = [Creature((random.randint(210, self.bounds.right - 70), random.randint(145, self.bounds.bottom - 45)), stage["species"][i % len(stage["species"])], stage["speed"], stage["detect"], stage["damage"]) for i in range(stage["items"])]
        self.message, self.message_time = f"COLETE {stage['items']} AMOSTRAS E VOLTE AO SUBMERSIVEL", 3.5

    def event(self, event):
        if event.type != pygame.KEYDOWN: return
        if self.state == "menu":
            if event.key in (pygame.K_RETURN, pygame.K_SPACE): self.reset_run(); self.state = "briefing"
            elif event.key == pygame.K_h: self.state = "help"
        elif self.state in ("help", "briefing"):
            self.state = "play" if self.state == "briefing" else "menu"
        elif self.state == "play" and event.key == pygame.K_ESCAPE:
            self.state = "menu"
        elif self.state == "upgrade":
            costs = {pygame.K_1: ("tanque", 25), pygame.K_2: ("propulsor", 25), pygame.K_3: ("lanterna", 25)}
            if event.key in costs:
                item, cost = costs[event.key]
                if self.credits >= cost:
                    self.credits -= cost
                    if item == "tanque": self.tank += 35
                    elif item == "propulsor": self.speed += 35
                    else: self.lamp += 40
                    self.message, self.message_time = "MELHORIA INSTALADA", 2
                else: self.message, self.message_time = "CREDITOS INSUFICIENTES", 2
            if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                if self.level == 7 and self.lamp < 175:
                    self.message, self.message_time = "A ZONA ABISSAL EXIGE UMA MELHORIA DE LANTERNA", 3
                else:
                    self.start_level(); self.state = "briefing"
        elif self.state in ("lost", "win") and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.state = "menu"

    def update(self, dt):
        if self.state != "play": return
        self.message_time -= dt; self.hurt_timer = max(0, self.hurt_timer - dt)
        self.oxygen -= dt * (.52 + self.level * .075)
        self.diver.update(pygame.key.get_pressed(), dt, self.bounds)
        for item in self.items: item.update(dt)
        for creature in self.creatures: creature.update(dt, self.diver.position)
        for item in self.items[:]:
            if self.diver.rect.colliderect(item.rect.inflate(10, 10)):
                self.items.remove(item); self.credits += item.value
                self.message, self.message_time = f"+{item.value} CREDITOS", 1.2
        if self.hurt_timer == 0:
            for creature in self.creatures:
                if self.diver.rect.colliderect(creature.rect.inflate(-8, -8)):
                    self.oxygen -= creature.damage; self.hurt_timer = 1.4
                    self.diver.position = pygame.Vector2(85, 90); self.diver.rect.center = self.diver.position
                    self.message, self.message_time = f"ATAQUE: -{creature.damage} O2", 2
                    break
        if not self.items and self.diver.rect.centery < 105:
            self.best = max(self.best, self.level + 1)
            if self.level == len(LEVELS) - 1: self.state = "win"
            else: self.level += 1; self.state = "upgrade"
        if self.oxygen <= 0: self.state = "lost"

    def draw_theme(self, theme):
        if theme == "ruins":
            for x in (280, 620, 810):
                pygame.draw.rect(self.screen, (77, 112, 115), (x, 330, 16, 130)); pygame.draw.rect(self.screen, (122, 157, 151), (x - 8, 324, 32, 10))
        elif theme in ("cave", "trench"):
            for x in range(110, 920, 180): pygame.draw.polygon(self.screen, (4, 17, 38), [(x, 70), (x + 48, 70), (x + 24, 185)])
        elif theme in ("forest", "abyss"):
            for x in range(80, 930, 110):
                height = 45 + (x * 3 % 80); pygame.draw.rect(self.screen, (24, 101, 109), (x, self.bounds.bottom - height, 5, height)); pygame.draw.rect(self.screen, (66, 229, 195), (x - 5, self.bounds.bottom - height, 15, 5))
        elif theme == "garden":
            for x in range(80, 930, 100):
                pygame.draw.rect(self.screen, (221, 111, 152), (x, self.bounds.bottom - 46, 5, 36)); pygame.draw.rect(self.screen, (239, 160, 185), (x - 9, self.bounds.bottom - 35, 23, 6))
        else:
            for x in range(85, 930, 108):
                pygame.draw.rect(self.screen, (42, 173, 151), (x, self.bounds.bottom - 42, 4, 30)); pygame.draw.rect(self.screen, (61, 220, 188), (x - 7, self.bounds.bottom - 30, 17, 5))

    def background(self):
        stage, color = self.stage, self.stage["color"]
        self.screen.fill(color)
        for y in range(45, self.screen.get_height(), 28):
            pygame.draw.rect(self.screen, (color[0] // 2, color[1] // 2, max(0, color[2] - y // 10)), (0, y, self.screen.get_width(), 2))
        random.seed(self.level)
        for x in range(0, self.screen.get_width(), 48):
            height = random.randint(45, 125); pygame.draw.polygon(self.screen, (4, 18, 39), [(x, 45), (x + 25, 45), (x + 40, 45 + height), (x, 65 + height)])
        for x in range(0, self.screen.get_width(), 58):
            height = random.randint(50, 112); pygame.draw.polygon(self.screen, (3, 15, 34), [(x, self.bounds.bottom), (x + 45, self.bounds.bottom), (x + 28, self.bounds.bottom - height)])
        self.draw_theme(stage["theme"])
        pygame.draw.rect(self.screen, (164, 208, 207), (30, 43, 122, 21)); pygame.draw.rect(self.screen, (230, 251, 247), (48, 30, 62, 14)); pygame.draw.rect(self.screen, (238, 185, 70), (52, 64, 75, 4))

    def draw_play(self):
        self.background()
        for item in self.items: item.draw(self.screen)
        for creature in self.creatures: creature.draw(self.screen)
        self.diver.draw(self.screen)
        dark = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        final_dive = self.level == 7
        dark.fill((0, 0, 5, 228 if final_dive else 65 + self.level * 20))
        radius = self.lamp if not final_dive else max(80, self.lamp - 20)
        pygame.draw.circle(dark, (0, 0, 0, 0), self.diver.rect.center, radius); self.screen.blit(dark, (0, 0))
        panel(self.screen, pygame.Rect(12, 8, 330, 30)); text(self.screen, self.font, f"FASE {self.level + 1}/8: {self.stage['name']}", (20, 16))
        panel(self.screen, pygame.Rect(670, 8, 278, 30)); text(self.screen, self.font, "O2", (680, 16), (159, 235, 255)); bar(self.screen, pygame.Rect(710, 14, 126, 16), max(0, self.oxygen), self.tank, (67, 218, 232) if self.oxygen > 25 else (240, 92, 79)); text(self.screen, self.font, f"{self.credits:03d} C", (850, 16), (255, 221, 111))
        text(self.screen, self.font, f"AMOSTRAS: {len(self.items)}  |  AMEACAS: {len(self.creatures)}", (15, 548), (220, 244, 248))
        if self.message_time > 0:
            panel(self.screen, pygame.Rect(245, 512, 470, 32), (8, 27, 49), (76, 201, 202)); text(self.screen, self.font, self.message, (480, 528), center=True)

    def draw_center(self, heading, lines, footer):
        self.background(); shade = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA); shade.fill((0, 4, 12, 185)); self.screen.blit(shade, (0, 0))
        panel(self.screen, pygame.Rect(154, 82, 652, 405), (6, 28, 50), (74, 210, 217)); text(self.screen, self.title, heading, (480, 140), (114, 237, 237), True)
        for index, line in enumerate(lines): text(self.screen, self.font, line, (480, 215 + index * 32), center=True)
        text(self.screen, self.font, footer, (480, 450), (255, 220, 111), True)

    def draw(self):
        if self.state == "play": self.draw_play()
        elif self.state == "menu": self.draw_center("SUBAQUATICA", ["Oito zonas oceanicas. Criaturas territoriais. Exploracao abissal.", "Colete amostras e sobreviva ate a Zona Abissal."], "[ENTER] MERGULHAR     [H] COMO JOGAR")
        elif self.state == "help": self.draw_center("CONTROLES", ["WASD ou SETAS - mover o mergulhador", "Colete todas as amostras e retorne ao submarino.", "Criaturas detectam e perseguem voce. Melhore o traje entre as fases.", "A Zona Abissal exige uma melhoria de lanterna."], "PRESSIONE QUALQUER TECLA PARA VOLTAR")
        elif self.state == "briefing": self.draw_center(f"FASE {self.level + 1}", [self.stage["name"], f"PROFUNDIDADE: {self.stage['depth']}", self.stage["brief"], f"OBJETIVO: COLETAR {self.stage['items']} AMOSTRAS"], "[ENTER] INICIAR EXPEDICAO")
        elif self.state == "upgrade": self.draw_center("ESTACAO DE MELHORIAS", [f"CREDITOS DISPONIVEIS: {self.credits}", "[1] TANQUE +35 O2 - 25 C", "[2] PROPULSOR +35 VELOCIDADE - 25 C", "[3] LANTERNA +40 ALCANCE - 25 C"], "[ENTER] VER BRIEFING DA PROXIMA FASE")
        elif self.state == "lost": self.draw_center("OXIGENIO ESGOTADO", ["A expedicao terminou antes do retorno.", f"FASES ALCANCADAS: {self.best}/8"], "[ENTER] VOLTAR AO MENU")
        elif self.state == "win": self.draw_center("EXPEDICAO CONCLUIDA", ["Voce trouxe amostras das oito zonas oceanicas.", "A Zona Abissal agora guarda seus segredos no laboratorio."], "[ENTER] VOLTAR AO MENU")
