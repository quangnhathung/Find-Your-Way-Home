import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        # Lấy đường dẫn file .env
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(base_dir, ".env")

        load_dotenv(env_path)

        self.SidewaysMoves = int(os.getenv("MAX_SIDEWAY_MOVE", 2))
        self.SCREEN_WIDTH = int(os.getenv("SCREEN_WIDTH", 800))
        self.ROW = int(os.getenv("MATRIX", 15))
        self.BG_COLOR = os.getenv("BG_COLOR", "FFFFFF")
        self.DENSITY = float(os.getenv("DENSITY", 0.8))
