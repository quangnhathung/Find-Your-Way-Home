from .config import Config

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

conf = Config()
#game screen
WIDTH = 800

#element color
RED = (255, 0, 0)       # Đã duyệt (bị kẹt)
GREEN = (0, 255, 0)     # "Nhà" (End)
BLUE = (0, 0, 255)      # "Bạn" (Start)
WHITE = (255, 255, 255) # Nền trắng
BLACK = (0, 0, 0)       # Tường (Barrier)
PURPLE = (128, 0, 128)  # Đường đi (Path)
ORANGE = (255, 165, 0)  # Đang dò
GREY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
BUTTON = hex_to_rgb("#A7C7E7")
BG_COLOR = hex_to_rgb(conf.BG_COLOR)
YELLOW = hex_to_rgb("#F0DB18")

#game parameter

MAX_SIDEWAY_MOVE = conf.SidewaysMoves
SCREEN_WIDTH = conf.SCREEN_WIDTH
MATRIX = conf.ROW
BG_COLOR= conf.BG_COLOR
DENSITY= conf.DENSITY
MAX_RESTART = conf.MAX_RESTART
DELAY = conf.DELAY