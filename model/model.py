import random
from config.constans import *
import pygame
from pathlib import Path
from typing import Optional, Dict, List, Tuple

# --- cấu hình ảnh ---
_ASSET_FILES: Dict[str, object] = {
    'start': 'character-bg.png',
    'end': 'home.png',
    'wall_variants': ['grass.png', 'tree.png', 'rock.jpg', 'human-angry.png','hole.png'],
    'wall': 'wall.png',
    'open': 'mark.png',
    'path': 'foot.png',
    'closed': 'EndOfPath.png',
    'flag': 'flag.png'
}

_raw_images: Dict[str, Optional[pygame.Surface]] = {}
_scaled_cache: Dict[str, Dict[int, pygame.Surface]] = {}


def assets_dir() -> Path:
    """Thư mục assets"""
    return Path(__file__).parent.parent / 'assets'


def _load_raw_image_file(filename: str) -> Optional[pygame.Surface]:
    """Load và cache ảnh thô theo filename."""
    if filename in _raw_images:
        return _raw_images[filename]

    path = assets_dir() / filename
    try:
        surf = pygame.image.load(str(path))
        try:
            surf = surf.convert_alpha()
        except Exception:
            surf = surf.convert()
        _raw_images[filename] = surf
        return surf
    except Exception:
        _raw_images[filename] = None
        return None


def _resolve_filename(key_or_filename: str) -> Optional[str]:
    val = _ASSET_FILES.get(key_or_filename)
    if isinstance(val, str):
        return val
    if isinstance(val, list) and val:
        return val[0]
    return key_or_filename


def _get_scaled_image(key_or_filename: str, size: int) -> Optional[pygame.Surface]:
    filename = _resolve_filename(key_or_filename)
    if filename is None:
        return None

    if filename not in _scaled_cache:
        _scaled_cache[filename] = {}
    if size in _scaled_cache[filename]:
        return _scaled_cache[filename][size]

    raw = _load_raw_image_file(filename)
    if raw is None:
        return None
    try:
        scaled = pygame.transform.smoothscale(raw, (size, size))
    except Exception:
        scaled = pygame.transform.scale(raw, (size, size))
    _scaled_cache[filename][size] = scaled
    return scaled


class Node:
    def __init__(self, row: int, col: int, width: int, total_rows: int, is_null: bool = False):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors: List["Node"] = []
        self.width = width
        self.total_rows = total_rows
        self._is_null = is_null
        self.wall_filename: Optional[str] = None

    def get_pos(self) -> Tuple[int, int]:
        return self.row, self.col

    # --- trạng thái ---
    def is_wall(self) -> bool:
        return self.color == BLACK

    def is_flag(self) -> bool:
        return self.color == YELLOW # flag có màu vàng

    def is_start(self) -> bool:
        return self.color == BLUE

    def is_end(self) -> bool:
        return self.color == GREEN

    def is_open(self) -> bool:
        return self.color == ORANGE

    def is_path(self) -> bool:
        return self.color == PURPLE

    def is_closed(self) -> bool:
        return self.color == RED

    # --- thay đổi trạng thái ---
    def reset(self) -> None:
        self.color = WHITE
        self.wall_filename = None

    def make_start(self) -> None:
        self.color = BLUE

    def make_closed(self) -> None:
        self.color = RED

    def make_open(self) -> None:
        self.color = ORANGE

    def make_wall(self) -> None:
        self.color = BLACK
        variants = _ASSET_FILES.get('wall_variants')
        if isinstance(variants, list) and variants:
            self.wall_filename = random.choice(variants)
        else:
            fallback = _ASSET_FILES.get('wall')
            self.wall_filename = fallback if isinstance(fallback, str) else None

    def make_end(self) -> None:
        self.color = GREEN

    def make_path(self) -> None:
        self.color = PURPLE
        self.wall_filename = None

    def make_flag(self) -> None:
        self.color = YELLOW
        self.wall_filename = None

    def draw(self, win: pygame.Surface) -> None:
        # start
        if self.is_start():
            surf = _get_scaled_image('start', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, BLUE, (self.x, self.y, self.width, self.width))
            return

        # end
        if self.is_end():
            surf = _get_scaled_image('end', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, GREEN, (self.x, self.y, self.width, self.width))
            return

        # wall
        if self.is_wall():
            key = self.wall_filename or 'wall'
            surf = _get_scaled_image(key, self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.width))
            return

        # flag
        if self.is_flag():
            surf = _get_scaled_image('flag', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, BLACK, (self.x, self.y, self.width, self.width))
            return

        # closed
        if self.is_closed():
            surf = _get_scaled_image('closed', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, RED, (self.x, self.y, self.width, self.width))
            return

        # open
        if self.is_open():
            surf = _get_scaled_image('open', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, ORANGE, (self.x, self.y, self.width, self.width))
            return

        # path
        if self.is_path():
            surf = _get_scaled_image('path', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, PURPLE, (self.x, self.y, self.width, self.width))
            return
        
        if self.is_path():
            surf = _get_scaled_image('path', self.width)
            if surf:
                win.blit(surf, (self.x, self.y))
                return
            pygame.draw.rect(win, PURPLE, (self.x, self.y, self.width, self.width))
            return

        # mặc định
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid: List[List["Node"]]) -> None:
        self.neighbors = []
        # trên
        if self.row > 0 and not grid[self.row - 1][self.col].is_wall():
            self.neighbors.append(grid[self.row - 1][self.col])
        # trái
        if self.col > 0 and not grid[self.row][self.col - 1].is_wall():
            self.neighbors.append(grid[self.row][self.col - 1])
        # phải
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_wall():
            self.neighbors.append(grid[self.row][self.col + 1])
        # dưới
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_wall():
            self.neighbors.append(grid[self.row + 1][self.col])

    def __lt__(self, other: "Node") -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Node) and self.row == other.row and self.col == other.col

    def __hash__(self) -> int:
        return hash((self.row, self.col))


def scale_img(img: pygame.Surface, size: int) -> pygame.Surface:
    try:
        return pygame.transform.smoothscale(img, (size, size))
    except Exception:
        return pygame.transform.scale(img, (size, size))
