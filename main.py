import pygame

from scripts.scenes import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((960, 576))
    pygame.display.set_caption("SubAquatica - Expedicao Abissal")
    clock = pygame.time.Clock()
    game = Game(screen)
    running = True
    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                game.event(event)
        game.update(dt)
        game.draw()
        pygame.display.flip()
    pygame.quit()


if __name__ == "__main__":
    main()
