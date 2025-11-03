import pygame
from config.utils import hex_to_rgb
from config.layout import *
from model.model import *

pygame.font.init()

def fade_out(surface, duration_ms=1000, color=(0, 0, 0)):
    clock = pygame.time.Clock()
    overlay = pygame.Surface((TOTAL_WIDTH, WIN_HEIGHT))
    steps = max(6, duration_ms // 16)
    for i in range(steps + 1):
        alpha = int(255 * (i / steps))
        overlay.fill(color)
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))
        pygame.display.update()
        clock.tick(60)


def start_screen():
    try:
        bg_path = assets_dir() / "banner.png"
        bg_img = pygame.image.load(str(bg_path)).convert_alpha()
        bg_img = pygame.transform.smoothscale(bg_img, (TOTAL_WIDTH, WIN_HEIGHT))
    except Exception as e:
        print("Không thể load ảnh nền:", e)
        bg_img = None

    FONT_TITLE = pygame.font.SysFont("Poppins", 52)
    FONT_BTN = pygame.font.SysFont("Poppins", 28, bold=True)

    BG_COLOR = (245, 242, 234)
    BTN_COLOR = hex_to_rgb("#A4C8E1")
    BTN_HOVER = hex_to_rgb("#8BBBD6")
    TEXT_COLOR = hex_to_rgb("#4B2E05")

    btn_w, btn_h = 260, 64
    start_rect = pygame.Rect(TOTAL_WIDTH // 2 - btn_w // 2, WIN_HEIGHT // 2 - 40, btn_w, btn_h)
    exit_rect = pygame.Rect(TOTAL_WIDTH // 2 - btn_w // 2, WIN_HEIGHT // 2 + 50, btn_w, btn_h)

    clock = pygame.time.Clock()
    running = True
    while running:
        # Nền
        if bg_img:
            WIN.blit(bg_img, (0, 0))
            overlay = pygame.Surface((TOTAL_WIDTH, WIN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 100))
            WIN.blit(overlay, (0, 0))
        else:
            WIN.fill(BG_COLOR)

        # Tiêu đề
        title_text = "FIND YOUR WAY HOME"
        title = FONT_TITLE.render(title_text, True, (255, 255, 255))
        shadow = FONT_TITLE.render(title_text, True, (0, 0, 0))
        title_x = TOTAL_WIDTH // 2 - title.get_width() // 2
        title_y = 80
        WIN.blit(shadow, (title_x + 3, title_y + 3))
        WIN.blit(title, (title_x, title_y))

        # Vẽ nút
        mouse = pygame.mouse.get_pos()
        for rect, label in ((start_rect, "START"), (exit_rect, "EXIT")):
            hover = rect.collidepoint(mouse)
            color = BTN_HOVER if hover else BTN_COLOR

            # đổ bóng
            shadow_rect = rect.copy()
            shadow_rect.move_ip(0, 6)
            shadow_surface = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            shadow_surface.fill((0, 0, 0, 40))
            WIN.blit(shadow_surface, shadow_rect.topleft)

            # nút chính + viền
            pygame.draw.rect(WIN, color, rect, border_radius=14)
            pygame.draw.rect(WIN, (255, 255, 255), rect, 2, border_radius=14)

            txt = FONT_BTN.render(label, True, TEXT_COLOR)
            WIN.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_rect.collidepoint(event.pos):
                    fade_out(WIN, 360)
                    running = False 
                elif exit_rect.collidepoint(event.pos):
                    pygame.quit()
                    raise SystemExit

        pygame.display.update()
        clock.tick(60)
