from model.model import Node
from config.constans import *
import pygame
#heuristic
def h(p1, p2):
    # Manhattan distance
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if not current.is_start():
            current.make_path()
        draw()

# Hàm tiện ích
def h(p1, p2):
    # heuristic Manhattan
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        if not current.is_start():
            current.make_path()
        draw()

def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

def draw_grid_lines(win, rows, width):
    gap = width // rows
    for i in range(rows + 1):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
    for j in range(rows + 1):
        pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))
    pygame.draw.rect(win, GREY, (0, 0, width, width), 2)

def get_clicked_pos(pos, rows, width):
    gap = width // rows
    x, y = pos
    row = y // gap
    col = x // gap
    return row, col

pygame.font.init()
FONT = pygame.font.SysFont(None, 24)
def draw_button(win, rect, text, color):
    pygame.draw.rect(win, color, rect, border_radius=6)
    text_surf = FONT.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=rect.center)
    win.blit(text_surf, text_rect)
