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


# helper: check whether `maybe_ancestor` is in the ancestor chain of `node`
def is_ancestor(node, maybe_ancestor, came_from) -> bool:
    """Return True if maybe_ancestor appears in the chain of parents starting from node."""
    cur = node
    seen = set()
    while True:
        parent = came_from.get(cur, None)
        if parent is None:
            return False
        if parent == maybe_ancestor:
            return True
        # cycle guard
        if parent in seen:
            return False
        seen.add(parent)
        cur = parent

def reconstruct_path(came_from, current, draw):
    """
    Robust reconstruct: walk backward from `current` (usually end) and mark all parents as path.
    - If a parent is flagged, clear flag visuals before making path.
    - If a parent is already path, re-mark it and continue.
    - Stop when parent is missing or parent is start or a cycle is detected.
    """
    visited = set()
    node = current

    while True:
        parent = came_from.get(node, None)
        if parent is None:
            # reached node without a parent -> stop
            break

        # detect cycle
        if parent in visited:
            break
        visited.add(parent)

        # if parent is start, we don't color the start as path; stop after stepping to it
        if parent.is_start():
            break

        # clear flag visual if necessary so path will be shown
        if parent.is_flag():
            # prefer a reset() method if available; otherwise clear file & color
            try:
                parent.reset()
            except Exception:
                try:
                    parent.wall_filename = None
                except Exception:
                    pass

        # ensure path always overwrites previous visuals
        try:
            parent.make_path()
        except Exception:
            try:
                parent.color = PURPLE
                if hasattr(parent, "wall_filename"):
                    parent.wall_filename = None
            except Exception:
                pass

        draw()

        # continue walking
        node = parent


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
