from config.utils import *
import pygame
from config.config import *
from config.constans import *
from model.model import *

WIDTH = SCREEN_WIDTH
TOP_UI_HEIGHT = 50
BOTTOM_UI_HEIGHT = 50
TOTAL_RIGHT_PANEL = 350   # panel bên phải
WIN_HEIGHT = WIDTH + TOP_UI_HEIGHT + BOTTOM_UI_HEIGHT + 15
TOTAL_WIDTH = WIDTH + TOTAL_RIGHT_PANEL

try:
    logo_path = assets_dir() / "logo.png"
    icon_surf = pygame.image.load(logo_path)
    pygame.display.set_icon(icon_surf)
except Exception as e:
    print("Không load được icon:", e)

#cònig cho cua so
WIN = pygame.display.set_mode((TOTAL_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Tim Duong Ve Nha - Hill Climbing")