import os
from dotenv import load_dotenv


#fall back về mặc định nếu biến đó không có giá trị
def get_env_int(key, default):
    value = os.getenv(key)
    return int(value) if value and value.isdigit() else default

def get_env_float(key, default):
    value = os.getenv(key)
    try:
        return float(value) if value else default
    except ValueError:
        return default

def get_env_str(key, default):
    value = os.getenv(key)
    return value if value else default


class Config:
    def __init__(self):
        # Lấy đường dẫn file .env
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(base_dir, ".env")

        load_dotenv(env_path)

        self.SidewaysMoves = get_env_int("MAX_SIDEWAY_MOVE", 2)
        self.SCREEN_WIDTH = get_env_int("SCREEN_WIDTH", 800)
        self.ROW = get_env_int("MATRIX", 15)
        self.BG_COLOR = get_env_str("BG_COLOR", "#FFFFFF")
        self.DENSITY = get_env_float("DENSITY", 0.5)
        self.MAX_RESTART = get_env_int("MAX_RESTART", 3)
        self.DELAY = get_env_int("DELAY", 50)