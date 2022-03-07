#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import sys
from src.settings import *
from src.world import World


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.world = World()

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        pos = tuple(map(lambda x: x // TILESIZE, event.pos))
                        self.world.swap_tile(pos, 'forest')

                    elif event.button == 3:
                        pos = tuple(map(lambda x: x // TILESIZE, event.pos))
                        self.world.swap_tile(pos, 'grass')

            self.screen.fill((18, 135, 3))
            self.world.run()
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    print('LMB to add tree')
    print('RMB to add grass')
    game = Game()
    game.run()
