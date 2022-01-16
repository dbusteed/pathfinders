#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from random import choice, random, randint
from sys import exit

pygame.init()

world_x = 30
world_y = 20

CELL_SIZE = 32
WIDTH = world_x * CELL_SIZE
HEIGHT = world_y * CELL_SIZE

N_PATHFINDERS = 8
N_VILLAGES = 10

# in milliseconds
TREE_REGROW_RATE = 1000
GRASS_REGROW_RATE = 500

NEW_TREE_PROB = 0.01

if N_VILLAGES < 2:
    print('You need at least 2 villages')
    exit(1)

pygame.display.set_caption("")
win = pygame.display.set_mode((WIDTH, HEIGHT))

path_1 = pygame.transform.scale(pygame.image.load('sprites/path_1.png'), (CELL_SIZE, CELL_SIZE))
path_2 = pygame.transform.scale(pygame.image.load('sprites/path_2.png'), (CELL_SIZE, CELL_SIZE))
path_3 = pygame.transform.scale(pygame.image.load('sprites/path_3.png'), (CELL_SIZE, CELL_SIZE))
path_4 = pygame.transform.scale(pygame.image.load('sprites/path_4.png'), (CELL_SIZE, CELL_SIZE))
path_5 = pygame.transform.scale(pygame.image.load('sprites/path_5.png'), (CELL_SIZE, CELL_SIZE))
path_6 = pygame.transform.scale(pygame.image.load('sprites/path_6.png'), (CELL_SIZE, CELL_SIZE))
path_7 = pygame.transform.scale(pygame.image.load('sprites/path_7.png'), (CELL_SIZE, CELL_SIZE))
path_8 = pygame.transform.scale(pygame.image.load('sprites/path_8.png'), (CELL_SIZE, CELL_SIZE))
forest_1 = pygame.transform.scale(pygame.image.load('sprites/forest_1.png'), (CELL_SIZE, CELL_SIZE))
forest_2 = pygame.transform.scale(pygame.image.load('sprites/forest_2.png'), (CELL_SIZE, CELL_SIZE))
forest_3 = pygame.transform.scale(pygame.image.load('sprites/forest_3.png'), (CELL_SIZE, CELL_SIZE))
forest_4 = pygame.transform.scale(pygame.image.load('sprites/forest_4.png'), (CELL_SIZE, CELL_SIZE))
forest_5 = pygame.transform.scale(pygame.image.load('sprites/forest_5.png'), (CELL_SIZE, CELL_SIZE))
forest_6 = pygame.transform.scale(pygame.image.load('sprites/forest_6.png'), (CELL_SIZE, CELL_SIZE))
forest_7 = pygame.transform.scale(pygame.image.load('sprites/forest_7.png'), (CELL_SIZE, CELL_SIZE))
forest_8 = pygame.transform.scale(pygame.image.load('sprites/forest_8.png'), (CELL_SIZE, CELL_SIZE))
village = pygame.transform.scale(pygame.image.load('sprites/village.png'), (CELL_SIZE, CELL_SIZE))
pathfinder = pygame.transform.scale(pygame.image.load('sprites/pathfinder.png'), (CELL_SIZE, CELL_SIZE))

path_sprites = [
    path_1, path_2, path_3, path_4,
    path_5, path_6, path_7, path_8
]

forest_sprites = [
    forest_1, forest_2, forest_3, forest_4,
    forest_5, forest_6, forest_7, forest_8
]

tile_dist = ['grass', 'grass', 'grass', 'forest', 'forest']

base_values = {
    'grass': 0,
    'village': 0,
    'forest': 50,
}


class Tile:
    def __init__(self, kind):
        self.kind = kind
        
        if kind == 'grass':
            self.durability = 8
            self.sprite = path_sprites[self.durability - 1]
        elif kind == 'forest':
            self.durability = randint(5, 8)
            self.sprite = forest_sprites[self.durability - 1]
        elif kind == 'village':
            self.durability = 1


class PathCell:
    def __init__(self, kind, durability, pos=None):
        self.val = base_values[kind] + durability
        self.count = None
        self.path_from = None
        self.pos = pos


class Pathfinder:
    def __init__(self, world, villages):
        self.speed = 100
        self.last_move = 0
        self.sprite = pathfinder
        self.villages = villages
        self.point_a = choice(villages)
        self.x, self.y = self.point_a

        self.point_b = choice(villages)
        while self.point_b == self.point_a:
            self.point_b = choice(villages)

    def travel(self):
        path = find_path((self.x, self.y), self.point_b, world)
        if len(path) > 1:
            next_x, next_y = path[1]
            next_cell = world[next_x][next_y]
            if next_cell.kind == 'forest':
                if next_cell.durability == 0:
                    world[next_x][next_y].durability = 8
                    world[next_x][next_y].kind = 'grass'
                    world[next_x][next_y].sprite = path_8
                    p.x, p.y = next_x, next_y
                else:
                    next_cell.durability -= 1
                    world[next_x][next_y].sprite = forest_sprites[next_cell.durability]
                pass
            
            elif next_cell.kind == 'grass':
                p.x, p.y = next_x, next_y
                if random() < 0.5:
                    i = max(1, world[next_x][next_y].durability - 1)
                    world[next_x][next_y].durability = i
                    try:
                        world[next_x][next_y].sprite = path_sprites[i-1]
                    except:
                        world[next_x][next_y].sprite = path_sprites[7]
            
            elif next_cell.kind == 'village':
                p.x, p.y = next_x, next_y

        else:
            self.point_b = choice(villages)
            while self.point_b == (self.x, self.y):
                self.point_b = choice(villages)
        
        self.last_move = pygame.time.get_ticks()


def draw_map():
    for y in range(world_y):
        for x in range(world_x):
            win.blit(world[x][y].sprite, (x*CELL_SIZE, y*CELL_SIZE))

def is_valid(pos):
    return pos[0] >= 0 and pos[1] >= 0 and pos[0] < world_x and pos[1] < world_y

neighbours = [[-1,0], [1,0], [0,-1], [0,1]]
def find_path(start, end, world):

    maze = [[PathCell(world[ix][iy].kind, world[ix][iy].durability, [ix, iy]) for iy in range(len(world[0]))] for ix in range(len(world))]
    for y in range(world_y):
        for x in range(world_x):
            maze[x][y].count = 1000
            maze[x][y].path_from = None

    maze[start[0]][start[1]].count = 0

    open_list = [start]
    while open_list:
        cur_pos = open_list.pop(0)
        cur_cell = maze[cur_pos[0]][cur_pos[1]]

        for n in neighbours:
            ncell_pos = [cur_pos[0] + n[0], cur_pos[1] + n[1]]
            if not is_valid(ncell_pos):
                continue
            
            cell = maze[ncell_pos[0]][ncell_pos[1]]
            
            dist = cur_cell.count + cell.val
            if cell.count > dist:
                cell.count = dist
                cell.path_from = cur_cell
                open_list.append(ncell_pos)

    path = []
    cell = maze[end[0]][end[1]]
    while cell != None:
        path.append(cell.pos)
        cell = cell.path_from

    path.reverse()

    return path

app_running = True
clock = pygame.time.Clock()

world = [[Tile(choice(tile_dist)) for iy in range(world_y)] for ix in range(world_x)]

villages = [(randint(0, world_x-1), randint(0, world_y-1)) for _ in range(N_VILLAGES)]
pathfinders = [Pathfinder(world, villages) for _ in range(N_PATHFINDERS)]

for v in villages:
    world[v[0]][v[1]].kind = 'village'
    world[v[0]][v[1]].sprite = village

last_tree_regrow = 0
last_grass_regrow = 0

input()

while app_running:
    clock.tick(60)
     
    draw_map()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_running = False

        # elif event.type == pygame.MOUSEBUTTONDOWN:
        #     if event.button == 1:
        #         x = event.pos[0] // CELL_SIZE
        #         y = event.pos[1] // CELL_SIZE
        #         if world[x][y].kind == 'grass':
        #             world[x][y] = Tile('forest')

    for p in pathfinders:
        if pygame.time.get_ticks() - p.last_move > p.speed:
            p.travel()

        win.blit(p.sprite, (p.x*CELL_SIZE, p.y*CELL_SIZE))

    if pygame.time.get_ticks() - last_tree_regrow > TREE_REGROW_RATE:
        x = randint(0, world_x - 1)
        y = randint(0, world_y - 1)
        if world[x][y].kind == 'forest':
            d = min(8, world[x][y].durability + 1)
            world[x][y].durability = d
            world[x][y].sprite = forest_sprites[d - 1]
        elif world[x][y].kind == 'grass':
            if world[x][y].durability == 8:
                if random() < NEW_TREE_PROB:
                    world[x][y].durability = 1
                    world[x][y].sprite = forest_sprites[0]
                    world[x][y].kind = 'forest'

    if pygame.time.get_ticks() - last_grass_regrow > GRASS_REGROW_RATE:
        while True:
            x = randint(0, world_x - 1)
            y = randint(0, world_y - 1)
            if world[x][y].kind == 'grass':
                d = min(8, world[x][y].durability + 1)
                world[x][y].durability = d
                world[x][y].sprite = path_sprites[d - 1]
                break
        
        last_regrow = pygame.time.get_ticks()

    pygame.display.update()

pygame.quit()
