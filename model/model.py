from config.constans import *
import pygame
from pathlib import Path
from typing import Optional, Dict

# --- cấu hình ảnh ---
_ASSET_FILES = {
    'start': 'character-bg.png',
    'end': 'home.png',
    'wall': 'wall.png',
    'open': 'mark.png',
    'path': 'foot.png',
    'closed': 'EndOfPath.png'
}

# cache raw images
_raw_images: Dict[str, Optional[pygame.Surface]] = {k: None for k in _ASSET_FILES.keys()}

# cache scaled images
_scaled_cache: Dict[str, Dict[int, pygame.Surface]] = {k: {} for k in _ASSET_FILES.keys()}


def _assets_dir() -> Path:
    return Path(__file__).parent.parent / 'assets'


def _load_raw_image(name: str) -> Optional[pygame.Surface]:
    if _raw_images.get(name) is not None:
        return _raw_images[name]

    filename = _ASSET_FILES.get(name)
    if not filename:
        _raw_images[name] = None
        return None

    path = _assets_dir() / filename
    try:
        surf = pygame.image.load(str(path))
        try:
            surf = surf.convert_alpha()
        except Exception:
            surf = surf.convert()
        _raw_images[name] = surf
        return surf
    except Exception:
        _raw_images[name] = None
        return None


def _get_scaled_image(name: str, size: int) -> Optional[pygame.Surface]:
    if name not in _scaled_cache:
        return None
    if size in _scaled_cache[name]:
        return _scaled_cache[name][size]
    raw = _load_raw_image(name)
    if raw is None:
        return None
    try:
        scaled = pygame.transform.smoothscale(raw, (size, size))
    except Exception:
        scaled = pygame.transform.scale(raw, (size, size))
    _scaled_cache[name][size] = scaled
    return scaled


class Node:
    def __init__(self, row, col, width, total_rows, is_null=False):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self._is_null = is_null

    def get_pos(self):
        return self.row, self.col

    # trạng thái
    def is_wall(self): return self.color == BLACK
    def is_start(self): return self.color == BLUE
    def is_end(self): return self.color == GREEN
    def is_open(self): return self.color == ORANGE
    def is_path(self): return self.color == PURPLE
    def is_closed(self): return self.color == RED  # thêm kiểm tra closed

    def reset(self): self.color = WHITE
    def make_start(self): self.color = BLUE
    def make_closed(self): self.color = RED
    def make_open(self): self.color = ORANGE
    def make_wall(self): self.color = BLACK
    def make_end(self): self.color = GREEN
    def make_path(self): self.color = PURPLE

    def draw(self, win):
        if self.is_start():
            surf = _get_scaled_image('start', self.width)
            if surf: win.blit(surf, (self.x, self.y)); return
            pygame.draw.rect(win, BLUE, (self.x, self.y, self.width, self.width)); return

        if self.is_end():
            surf = _get_scaled_image('end', self.width)
            if surf: win.blit(surf, (self.x, self.y)); return
            pygame.draw.rect(win, GREEN, (self.x, self.y, self.width, self.width)); return

        if self.is_wall():
            surf = _get_scaled_image('wall', self.width)
            if surf: win.blit(surf, (self.x, self.y)); return
            pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.width)); return

        if self.is_closed():  # hiển thị ảnh EndOfPath.jpg
            surf = _get_scaled_image('closed', self.width)
            if surf: win.blit(surf, (self.x, self.y)); return
            pygame.draw.rect(win, RED, (self.x, self.y, self.width, self.width)); return

        if self.is_open():
            surf = _get_scaled_image('open', self.width)
            if surf: win.blit(surf, (self.x, self.y)); return
            pygame.draw.rect(win, ORANGE, (self.x, self.y, self.width, self.width)); return

        if self.is_path():
            surf = _get_scaled_image('path', self.width)
            if surf: win.blit(surf, (self.x, self.y)); return
            pygame.draw.rect(win, PURPLE, (self.x, self.y, self.width, self.width)); return

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall():
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall():
            self.neighbors.append(grid[self.row][self.col - 1])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall():
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall():
            self.neighbors.append(grid[self.row + 1][self.col])

    def __lt__(self, other): return False
    def __eq__(self, other): return isinstance(other, Node) and self.row == other.row and self.col == other.col
    def __hash__(self): return hash((self.row, self.col))


def scale_img(img: pygame.Surface, size: int) -> pygame.Surface:
    try:
        return pygame.transform.smoothscale(img, (size, size))
    except Exception:
        return pygame.transform.scale(img, (size, size))
