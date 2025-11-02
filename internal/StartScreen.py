# start_screen.py
import pygame
from config.utils import hex_to_rgb

# Nếu root.py không import start_screen, import trực tiếp các biến từ root
# Nếu bạn gặp lỗi circular import, di chuyển import bên trong nút START (xem chú thích trên).
from .root import root as root_func, WIN, TOTAL_WIDTH, WIN_HEIGHT

pygame.font.init()

def fade_out(surface, duration_ms=400, color=(0,0,0)):
    """Fade out mượt bằng overlay đen tăng dần alpha."""
    clock = pygame.time.Clock()
    overlay = pygame.Surface((TOTAL_WIDTH, WIN_HEIGHT))
    steps = max(6, duration_ms // 16)  # ~60FPS
    for i in range(steps + 1):
        alpha = int(255 * (i / steps))
        overlay.fill(color)
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))
        pygame.display.update()
        clock.tick(60)

def start_screen():
    """Hiển thị màn hình bắt đầu hoàn chỉnh với background, nút, hover và fade transition."""
    # --- Thử load ảnh nền ---
    try:
        bg_img = pygame.image.load("./assets/logo.png").convert_alpha()
        bg_img = pygame.transform.smoothscale(bg_img, (TOTAL_WIDTH, WIN_HEIGHT))
    except Exception:
        try:
            bg_img = pygame.image.load("./assets/logo.png").convert_alpha()
            bg_img = pygame.transform.smoothscale(bg_img, (TOTAL_WIDTH, WIN_HEIGHT))
        except Exception as e:
            print("Không thể load ảnh nền:", e)
            bg_img = None

    # --- Fonts & colors ---
    FONT_TITLE = pygame.font.SysFont("Poppins", 52)
    FONT_BTN = pygame.font.SysFont("Poppins", 28, bold=True)

    BG_COLOR = (245, 242, 234)
    BTN_COLOR = hex_to_rgb("#A4C8E1")
    BTN_HOVER = hex_to_rgb("#8BBBD6")
    TEXT_COLOR = hex_to_rgb("#4B2E05")

    # --- Rect nút (căn giữa màn hình) ---
    btn_w, btn_h = 260, 64
    start_rect = pygame.Rect(TOTAL_WIDTH//2 - btn_w//2, WIN_HEIGHT//2 - 40, btn_w, btn_h)
    exit_rect = pygame.Rect(TOTAL_WIDTH//2 - btn_w//2, WIN_HEIGHT//2 + 40 + 10, btn_w, btn_h)

    clock = pygame.time.Clock()
    running = True
    while running:
        # --- Vẽ background ---
        if bg_img:
            WIN.blit(bg_img, (0, 0))
            # overlay mờ tối để chữ nổi bật hơn
            overlay = pygame.Surface((TOTAL_WIDTH, WIN_HEIGHT), flags=pygame.SRCALPHA)
            overlay.fill((0,0,0,100))  # alpha 100/255
            WIN.blit(overlay, (0, 0))
        else:
            WIN.fill(BG_COLOR)

        # --- Tiêu đề với shadow ---
        title_text = "FIND YOUR WAY HOME"
        title = FONT_TITLE.render(title_text, True, hex_to_rgb("#FFFFFF"))
        shadow = FONT_TITLE.render(title_text, True, (255,255,255))
        title_x = TOTAL_WIDTH//2 - title.get_width()//2
        title_y = 80
        WIN.blit(shadow, (title_x + 2, title_y + 2))
        WIN.blit(title, (title_x, title_y))

        # --- Vẽ nút (hover effect + viền trắng) ---
        mouse = pygame.mouse.get_pos()
        for rect, label in ((start_rect, "START"), (exit_rect, "EXIT")):
            is_hover = rect.collidepoint(mouse)
            color = BTN_HOVER if is_hover else BTN_COLOR

            # shadow phía dưới cho cảm giác nổi
            shadow_rect = rect.copy()
            shadow_rect.move_ip(0, 6)
            s = pygame.Surface((rect.w, rect.h), flags=pygame.SRCALPHA)
            s.fill((0,0,0,40))
            WIN.blit(s, shadow_rect.topleft)

            # main rect + viền
            pygame.draw.rect(WIN, color, rect, border_radius=14)
            pygame.draw.rect(WIN, (255,255,255), rect, 2, border_radius=14)

            # label
            txt = FONT_BTN.render(label, True, TEXT_COLOR)
            WIN.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))

        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    # Fade out rồi gọi root() để vào game chính
                    fade_out(WIN, duration_ms=360)
                    # Nếu root_func chưa import được do circular import, bạn có thể import ở đây:
                    # from .root import root as root_func
                    root_func(WIN, width=TOTAL_WIDTH - 350)  # Gọi root, truyền tham số nếu cần
                    return  # sau khi root() thoát, không quay lại menu
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    raise SystemExit

        pygame.display.update()
        clock.tick(60)
