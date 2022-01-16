#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from random import choice

pygame.init()

WIDTH = 1280
HEIGHT = 768
CELL_SIZE = 16

cell_font = pygame.font.SysFont(pygame.font.get_default_font(), 24)

class Cell:
    def __init__(self, val, pos=None):
        self.val = val
        self.count = 1000
        self.path_from = None
        self.pos = pos
        if self.val == 1: 
            self.marker = '.'
            self.color = (30, 30, 30)
        else:
            self.marker = self.val
            self.color = (0, 150, 0)

    def __repr__(self):
        return f'{str(self.val)}'

    def __str__(self):
        return f'{self.marker}'

win = pygame.display.set_mode((WIDTH, HEIGHT))

dist = [1, 1, 50]

map_x = int(WIDTH / CELL_SIZE)
map_y = int(HEIGHT / CELL_SIZE)
maze = [[Cell(val=choice(dist), pos=[ix,iy]) for iy in range(map_y)] for ix in range(map_x)]

def draw_map():
    for y in range(map_y):
        for x in range(map_x):
            pygame.draw.rect(win, maze[x][y].color, [x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE])

s = (0, map_y-1)
e = (map_x-1, 0)
open_list = [s]

maze[s[0]][s[1]].count = 0

neighbours = [[-1,0], [1,0], [0,-1], [0,1]]

def is_valid(pos):
    return pos[0] >= 0 and pos[1] >= 0 and pos[0] < map_x and pos[1] < map_y

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
cell = maze[e[0]][e[1]]
while cell != None:
    path.append(cell.pos)
    cell = cell.path_from

path.reverse()

for p in path:
    maze[p[0]][p[1]].color = (50, 50, 200)

app_running = True
clock = pygame.time.Clock()

win.fill((30, 30, 30))

while app_running:
    clock.tick(60)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_running = False

    draw_map()

    pygame.display.update()

pygame.quit()