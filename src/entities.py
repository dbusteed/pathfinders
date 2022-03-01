import pygame
from random import choice
from src.settings import TILESIZE
from src.util import load_image, neighbors8


nav_values = {
    'village': 0,
    'path': 10,
    'grass': 10,
    'forest': 100,
}


class SpriteEntity(pygame.sprite.Sprite):
    def __init__(self, pos, groups, image):
        super().__init__(groups)
        self.pos = pos
        self.image = image
        self.rect = self.image.get_rect(topleft=(pos[0] * TILESIZE, pos[1] * TILESIZE))


class Pathfinder(SpriteEntity):
    def __init__(self, pos, groups, world):
        super().__init__(pos, groups, load_image('sprites/pathfinder.png'))
        self.world = world
        self.speed = 75
        self.last_move = 0
        self.point_a = choice(self.world.villages)
        self.path = None

        self.point_b = choice(self.world.villages)
        while self.point_b == self.point_a:
            self.point_b = choice(self.world.villages)


    def travel(self):
        if pygame.time.get_ticks() - self.last_move <= self.speed:
            return
        
        if not self.path:
            self.path = self.world.find_path(self.pos, self.point_b)

        moved = True
        if len(self.path) > 1:
            npos = self.path[1]
            nkind = self.world.map[npos].kind

            if nkind in ('grass', 'path'):
                if nkind == 'grass':
                    self.world.map[npos].kind = 'path'
                dur = max(1, self.world.map[npos].durability - 1)
                self.world.map[npos].durability = dur
                self.world.map[npos].image = self.world.path_sprites[dur][self.world.bitmask(*npos, 'is_path')]

                for pos2 in [(npos[0] + _x, npos[1] + _y) for _x, _y in neighbors8]:
                    if self.world.is_path(pos2) and self.world.map[pos2].kind != 'village':
                        self.world.map[pos2].image = self.world.path_sprites[self.world.map[pos2].durability][self.world.bitmask(*pos2, 'is_path')]

            elif nkind == 'forest':
                dur = self.world.map[npos].durability - 1
                if dur > 1:
                    self.world.map[npos].durability = dur
                    self.world.map[npos].image = self.world.forest_sprites[dur][self.world.bitmask(*npos, 'is_forest')]
                    moved = False
                else:
                    self.world.map[npos].kind = 'grass'
                    self.world.map[npos].image = self.world.path_sprites[16][0]
                    self.world.map[npos].durability = 16

                    for pos2 in [(npos[0] + _x, npos[1] + _y) for _x, _y in neighbors8]:
                        if self.world.is_forest(pos2):
                            self.world.map[pos2].image = self.world.forest_sprites[self.world.map[pos2].durability][self.world.bitmask(*pos2, 'is_forest')]

            if moved:
                self.pos = npos
                self.rect = self.image.get_rect(topleft=(self.pos[0] * TILESIZE, self.pos[1] * TILESIZE))
        else:
            self.path = None
            self.point_b = choice(self.world.villages)
            while self.point_b == self.point_a:
                self.point_b = choice(self.world.villages)
        
        if self.path and moved:
            self.path.pop(0)
        self.last_move = pygame.time.get_ticks()

    def update(self):
        self.travel()


class Tile(SpriteEntity):
    def __init__(self, pos, groups, kind, surface=pygame.Surface((TILESIZE, TILESIZE))):
        super().__init__(pos, groups, surface)
        self.kind = kind
        self.base_nav = nav_values[kind]
        self.durability = 17

    def nav_value(self):
        return nav_values[self.kind] + self.durability
