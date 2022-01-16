#!/usr/bin/python3

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from random import choice

pygame.init()

WIDTH = 1000
HEIGHT = 600
CELL_SIZE = 50

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

dist = [1, 1, 1, 1, 50]

map_x = int(WIDTH / CELL_SIZE)
map_y = int(HEIGHT / CELL_SIZE)
maze = [[Cell(val=choice(dist), pos=[ix,iy]) for iy in range(map_y)] for ix in range(map_x)]

def draw_map():
    for y in range(map_y):
        for x in range(map_x):
            pygame.draw.rect(win, maze[x][y].color, [x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE])
            pygame.draw.rect(win, (50, 50, 50), [x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE], 1)
            # text = cell_font.render( "{}".format(maze[x][y].val), True, (255,255,255))
            # win.blit(text, (x*50 + 20, y*50 + 20))


s = (0, map_y // 2)
e = (map_x-1, map_y // 2)

neighbours = [[-1,0], [1,0], [0,-1], [0,1]]

def is_valid(pos):
    return pos[0] >= 0 and pos[1] >= 0 and pos[0] < map_x and pos[1] < map_y

def find_path(start, end):
    for y in range(map_y):
        for x in range(map_x):
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

win.fill((30, 30, 30))

i = 0
pad = CELL_SIZE // 5

last_move = 0

x, y = s

print()
print('"Dynamic" pathfinding example. Click on an open')
print('space to make it an obstacle, and watch the white')
print('square navigate around the new terrain. NOTE: the')
print('square will travel thru obstacles if no other')
print('path is available')
print()

while app_running:
    clock.tick(60)
    
    win.fill((30, 30, 30))
    draw_map()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click_x = event.pos[0] // CELL_SIZE
                click_y = event.pos[1] // CELL_SIZE
                pygame.draw.rect(win, (255, 255, 255), (click_x*CELL_SIZE, click_y*CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)
                maze[click_x][click_y] = Cell(50)

    if pygame.time.get_ticks() - last_move > 500:
        last_move = pygame.time.get_ticks()

        p = find_path((x, y), e)
        if len(p) > 1:
            try:
                x, y = p[1]
            except:
                p = [z for z in p if z]
                x, y = p[1]

    pygame.draw.rect(win, (255, 255, 255), pygame.Rect(x*CELL_SIZE+pad, y*CELL_SIZE+pad, CELL_SIZE-(pad*2), CELL_SIZE-(pad*2)))

    pygame.display.update()

pygame.quit()