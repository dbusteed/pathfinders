import numpy as np
import pygame
from random import randint, choice
from src.settings import *
from src.entities import Pathfinder, Tile
from src.util import (
    AStarCell, bitmask_map, neighbors8,
    load_image, load_durability_images,
)

class World:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = pygame.sprite.Group()

        self.grass_sprite = load_image('sprites/grass.png')
        self.village_sprite = load_image('sprites/village.png')
        self.path_sprites = load_durability_images('sprites/path', 'path_')
        self.forest_sprites = load_durability_images('sprites/forest', 'forest_')
        
        self.last_grass_regrow = 0

        self.build_world()


    def build_world(self):

        # STEP 1
        #   initialize the map with grass tiles. the map
        #   will be "sideways" so that we can index
        #   more naturally later on with (x, y) pairs
        #
        self.map = [[0] * WORLD_Y for _ in range(WORLD_X)]
        for x, col in enumerate(self.map):
            for y, _ in enumerate(col):
                self.map[x][y] = Tile((x, y), [self.visible_sprites], 'grass', self.grass_sprite)
        self.map = np.array(self.map)

        # STEP 2
        #   set some of the grass tiles to forests. after the 
        #   forests are added, loop back thru and update the sprites
        #
        self.forests = []
        for _ in range(N_TREES):
            x, y = randint(0, WORLD_X-1), randint(0, WORLD_Y-1)
            self.map[x][y].kind = 'forest'
            self.forests.append((x, y))

        for x, y in self.forests:
            for npos in [(x + _x, y + _y) for _x, _y in neighbors8]:
                if self.is_forest(npos):
                    self.map[npos].image = self.forest_sprites[17][self.bitmask(*npos, 'is_forest')]

        # STEP 3
        #   next, add the villages by putting them in random positions.
        #   uncomment the `neighbors` block to prevent villages
        #   being placed directly next to one another
        #
        v = N_VILLAGES
        self.villages = []
        while v:
            pos = randint(0, WORLD_X-1), randint(0, WORLD_Y-1)
            
            if self.map[pos].kind == 'grass':
                valid = True
                # neighbors = [(x + _x, y + _y) for _x, _y in neighbors8]
                # neighbors = [pos for pos in neighbors if self.is_valid(pos)]
                # for npos in neighbors:
                #     if self.map[npos].kind == 'village':
                #         valid = False
                #         break
                if valid:
                    self.map[pos].kind = 'village'
                    self.map[pos].image = self.village_sprite
                    self.map[pos].durability = 1
                    self.villages.append(pos)
                    v -= 1

        # STEP 4
        #   add the pathfinders
        #
        for _ in range(N_PATHFINDERS):
            Pathfinder(choice(self.villages), [self.visible_sprites], self)
        

    def find_path(self, start, end):
        neighbours = [[-1,0], [1,0], [0,-1], [0,1]]
        m = np.array([[AStarCell(self.map[x][y].nav_value(), (x, y)) for y in range(len(self.map[0]))] for x in range(len(self.map))])
        for y in range(WORLD_Y):
            for x in range(WORLD_X):
                m[x][y].count = 1000
                m[x][y].path_from = None
        m[start].count = 0
        
        open_list = [start]
        while open_list:
            cur_pos = open_list.pop(0)
            cur_cell = m[cur_pos]

            for n in neighbours:
                ncell_pos = (cur_pos[0] + n[0], cur_pos[1] + n[1])
                if not self.is_valid(ncell_pos):
                    continue

                cell = m[ncell_pos]
                dist = cur_cell.count + cell.val
                if cell.count > dist:
                    cell.count = dist
                    cell.path_from = cur_cell
                    open_list.append(ncell_pos)

        path = []
        cell = m[end]
        while cell != None:
            path.append(cell.pos)
            cell = cell.path_from
        path.reverse()

        return path


    def bitmask(self, x, y, tile_check):
        res = 0
        if getattr(self, tile_check)((x-1, y-1)): res += 1
        if getattr(self, tile_check)((  x, y-1)): res += 2
        if getattr(self, tile_check)((x+1, y-1)): res += 4
        if getattr(self, tile_check)((x-1,   y)): res += 8
        if getattr(self, tile_check)((x+1,   y)): res += 16
        if getattr(self, tile_check)((x-1, y+1)): res += 32
        if getattr(self, tile_check)((  x, y+1)): res += 64
        if getattr(self, tile_check)((x+1, y+1)): res += 128
        return bitmask_map[res]


    def is_valid(self, pos):
        return pos[0] >= 0 and pos[1] >= 0 and pos[0] < WORLD_X and pos[1] < WORLD_Y


    def is_path(self, pos):
        return self.is_valid(pos) and self.map[pos[0]][pos[1]].kind in ('path', 'village')


    def is_forest(self, pos):
        return self.is_valid(pos) and self.map[pos[0]][pos[1]].kind == 'forest'


    def regrowth(self):
        if pygame.time.get_ticks() - self.last_grass_regrow <= GRASS_REGROW_RATE:
            return
        
        for _ in range(GRASS_REGROW_AMT):
            pos = randint(0, WORLD_X-1), randint(0, WORLD_Y-1)
            if self.map[pos].kind == 'path':
                dur = min(17, self.map[pos].durability + 1)
                self.map[pos].durability = dur
                if dur >= 17:
                    self.map[pos].kind = 'grass'
                    self.map[pos].image = self.grass_sprite
                else:
                    self.map[pos].image = self.path_sprites[dur][self.bitmask(*pos, 'is_path')]

        self.last_grass_regrow = pygame.time.get_ticks()


    def swap_tile(self, pos, kind):
        self.map[pos].durability = 17

        if kind == 'forest':
            self.map[pos].kind = 'forest'
            self.map[pos].image = self.forest_sprites[17][self.bitmask(*pos, 'is_forest')]
            for npos in [(pos[0] + _x, pos[1] + _y) for _x, _y in neighbors8]:
                if self.is_forest(npos):
                    self.map[npos].image = self.forest_sprites[self.map[npos].durability][self.bitmask(*npos, 'is_forest')]
        elif kind == 'grass':
            self.map[pos].kind = 'grass'
            self.map[pos].image = self.grass_sprite
            for npos in [(pos[0] + _x, pos[1] + _y) for _x, _y in neighbors8]:
                if self.is_forest(npos):
                    self.map[npos].image = self.forest_sprites[self.map[npos].durability][self.bitmask(*npos, 'is_forest')]
                if self.is_path(npos) and self.map[npos].kind != 'village':
                    self.map[npos].image = self.path_sprites[self.map[npos].durability][self.bitmask(*npos, 'is_path')]


    def run(self):
        self.visible_sprites.draw(self.display_surface)
        self.visible_sprites.update()
        self.regrowth()