# file: main.py
from .Algorithm.SteepestAscent import *
from config.utils import *
import pygame
import random
from .Algorithm.Simple import *
from .Algorithm.Stochastic import *
from .Algorithm.SidewaysMoves import *
from config.config import *
from model.model import Node
from config.constans import *

# ----- Cấu hình chung -----
conf = Config()
WIDTH = conf.SCREEN_WIDTH  # kích thước vùng lưới (vuông)
TOP_UI_HEIGHT = 50
BOTTOM_UI_HEIGHT = 50
TOTAL_RIGHT_PANEL = 350   # panel bên phải (không vẽ lưới vào đây)
WIN_HEIGHT = WIDTH + TOP_UI_HEIGHT + BOTTOM_UI_HEIGHT + 15
TOTAL_WIDTH = WIDTH + TOTAL_RIGHT_PANEL

try:
    icon_surf = pygame.image.load('./assets/logo.png')
    pygame.display.set_icon(icon_surf)
except Exception as e:
    print("Không load được icon:", e)

#cònig cho cua so
WIN = pygame.display.set_mode((TOTAL_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Tim Duong Ve Nha - Hill Climbing")


def root(win=WIN, width=WIDTH):
    ROWS = conf.ROW
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    started = False
    message = ""

    # Surface riêng cho lưới (chỉ vùng lưới)
    grid_surf = pygame.Surface((width, width))

    # --- Các nút điều khiển (trải đều trên TOTAL_WIDTH với gap cố định) ---
    button_texts = ["Stochastic", "Sideways", "Simple", "Steepest Ascent", "Random map"]
    button_count = len(button_texts)

    # tham số bố cục
    margin = 20                # khoảng cách trái/phải
    spacing = 15         # khoảng cách giữa các nút
    button_height = 40
    button_y = TOP_UI_HEIGHT + 10 + width + (BOTTOM_UI_HEIGHT - button_height) // 2

    # tính button_width theo công thức: (available_space - gaps) / n
    available = TOTAL_WIDTH - 2 * margin
    button_width = (available - spacing * (button_count - 1)) // button_count
    if button_width < 60:     # đảm bảo nút không quá nhỏ
        button_width = 60

    # tạo rect cho từng nút, trải đều và căn giữa hàng nếu cần
    total_buttons_width = button_count * button_width + (button_count - 1) * spacing
    start_x = margin + max(0, (available - total_buttons_width) // 2)

    buttons = []
    for i in range(button_count):
        x = start_x + i * (button_width + spacing)
        buttons.append(pygame.Rect(x, button_y, button_width, button_height))

    button_colors = [BUTTON] * button_count

    # --- Các hàm vẽ ---
    def update_grid_surf():
        grid_surf.fill(WHITE)
        for row in grid:
            for node in row:
                node.draw(grid_surf)
        draw_grid_lines(grid_surf, ROWS, width)

    def redraw_all():
        WIN.fill(BG_COLOR)
        # message phía trên (center trên vùng lưới)
        if message:
            text_surf = FONT.render(message, True, BLACK)
            text_rect = text_surf.get_rect(center=(width // 2, TOP_UI_HEIGHT // 2))
            win.blit(text_surf, text_rect)
        # vẽ lưới chính (vị trí 0, TOP_UI_HEIGHT)
        win.blit(grid_surf, (0, TOP_UI_HEIGHT))
        # panel phải (hiện trắng, bạn có thể vẽ thông tin ở đây)
        pygame.draw.rect(win, BG_COLOR, (width, TOP_UI_HEIGHT, TOTAL_RIGHT_PANEL, width))

        controls_x = width + 25
        controls_y = TOP_UI_HEIGHT + 20
        line_spacing = 28

        controls_text = [
            "Controls:",
            "  Left Click: Set Start, End, or draw Walls",
            "  Right Click: Delete a cell",
            "  Press C: Clear the entire map",
        ]
        for i, line in enumerate(controls_text):
            color = BLACK
            text_surf = FONT.render(line, True, color)
            win.blit(text_surf, (controls_x, controls_y + i * line_spacing))

        # vẽ các nút phía dưới
        for i, rect in enumerate(buttons):
            draw_button(win, rect, button_texts[i], button_colors[i])
        pygame.display.update()

    def algo_draw():
        update_grid_surf()
        win.blit(grid_surf, (0, TOP_UI_HEIGHT))
        pygame.display.update()

    update_grid_surf()
    redraw_all()

    # ---------- Vòng event ----------
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            # xử lý nhấp chuột trái
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                # click trong vùng lưới (tránh phần panel phải)
                if TOP_UI_HEIGHT <= pos[1] < TOP_UI_HEIGHT + width and pos[0] < width:
                    adjusted_pos = (pos[0], pos[1] - TOP_UI_HEIGHT)
                    row, col = get_clicked_pos(adjusted_pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        node = grid[row][col]
                        if not start and node != end:
                            start = node
                            start.make_start()
                        elif not end and node != start:
                            end = node
                            end.make_end()
                        elif node != end and node != start:
                            node.make_wall()

                # click xuống vùng nút (phía dưới)
                elif pos[1] >= TOP_UI_HEIGHT + width:
                    for i, rect in enumerate(buttons):
                        if rect.collidepoint(pos):
                            algo_name = button_texts[i]

                            # Random map: không cần start/end
                            if algo_name == "Random map":
                                # tạo lưới mới và set wall ngẫu nhiên
                                grid = make_grid(ROWS, width)
                                density = 0.25  # tỷ lệ tường (tùy chỉnh)
                                for r in grid:
                                    for node in r:
                                        if random.random() < density:
                                            node.make_wall()
                                # giữ start/end trước đó (nếu có) -> reset chúng trên grid mới
                                if start:
                                    start = grid[start.row][start.col]
                                    start.make_start()
                                if end:
                                    end = grid[end.row][end.col]
                                    end.make_end()
                                message = "Da tao random map."
                                update_grid_surf()
                                redraw_all()
                                break

                            # Các thuật toán cần start và end
                            if not start or not end:
                                message = "Vui long dat start va end truoc khi chay thuat toan."
                                redraw_all()
                                break

                            # chạy thuật toán
                            started = True
                            message = ""
                            
                            redraw_all()
                            for r in grid:
                                for node in r:
                                    node.update_neighbors(grid)

                            found = False
                            current_node = Node(-1, -1, 0, 0, is_null=True);
                            current_heuristic = 0;

                            if algo_name == "Stochastic":
                                found, current_heuristic, current_node = Stochastic(algo_draw, grid, start, end)
                            elif algo_name == "Sideways":
                                found, current_heuristic, current_node = Sideways(algo_draw, grid, start, end)
                            elif algo_name == "Simple":
                                found, current_heuristic, current_node = Simple(algo_draw, grid, start, end)
                            elif algo_name == "Steepest Ascent":
                                found, current_heuristic, current_node = Steepest_Ascent(algo_draw, grid, start, end)

                            if not found:
                                node_x, node_y =  current_node.get_pos();
                                message = f"Bi mat ket tai ({node_x +1},{node_y +1}) va heuristic hien tai la {current_heuristic}"
                            else:
                                message = f"Da tim thay nha voi {algo_name}!"
                            started = False
                            break

            # xử lý nhấp chuột phải -> reset node (chỉ vùng lưới)
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                if TOP_UI_HEIGHT <= pos[1] < TOP_UI_HEIGHT + width and pos[0] < width:
                    adjusted_pos = (pos[0], pos[1] - TOP_UI_HEIGHT)
                    row, col = get_clicked_pos(adjusted_pos, ROWS, width)
                    if 0 <= row < ROWS and 0 <= col < ROWS:
                        node = grid[row][col]
                        node.reset()
                        if node == start:
                            start = None
                        elif node == end:
                            end = None

            # bàn phím
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                    message = "Da reset ban do."

        update_grid_surf()
        redraw_all()

    pygame.quit()