from .Algorithm.SteepestAscent import *
from config.utils import *
import pygame
import random
from .Algorithm.Simple import *
from .Algorithm.Stochastic import *
from .Algorithm.SidewaysMoves import *
from .Algorithm.RandomRestart import *
from config.config import *
from model.model import Node
from config.constans import *
from config.layout import *


def root(win=WIN, width=WIDTH):

    delay = DELAY
    max_restart = MAX_RESTART

    ROWS = conf.ROW
    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    started = False
    message = ""

    grid_surf = pygame.Surface((width, width))

    button_texts = ["Simple", "Steepest Ascent", "Stochastic", "Random Restart", "Random map"]
    button_count = len(button_texts)

    margin = 20
    spacing = 15
    button_height = 40
    button_y = TOP_UI_HEIGHT + 10 + width + (BOTTOM_UI_HEIGHT - button_height) // 2

    available = TOTAL_WIDTH - 2 * margin
    button_width = (available - spacing * (button_count - 1)) // button_count
    if button_width < 60:
        button_width = 60

    total_buttons_width = button_count * button_width + (button_count - 1) * spacing
    start_x = margin + max(0, (available - total_buttons_width) // 2)

    buttons = []
    for i in range(button_count):
        x = start_x + i * (button_width + spacing)
        buttons.append(pygame.Rect(x, button_y, button_width, button_height))

    button_colors = [BUTTON] * button_count

    # --- Input fields trên panel phải ---
    controls_x = width + 25
    controls_y = TOP_UI_HEIGHT + 20
    input_labels = ["Max restart:", "Delay:"]
    input_texts = ["", ""]
    input_width = 200
    input_height = 30
    input_gap = 12
    input_rects = []
    for i in range(len(input_labels)):
        rx = controls_x + 100
        ry = controls_y + 100 + i * (input_height + input_gap)
        input_rects.append(pygame.Rect(rx, ry, input_width, input_height))

    apply_rect = pygame.Rect(
        controls_x + 80,
        controls_y + 100 + len(input_labels) * (input_height + input_gap) + 8,
        100,
        36,
    )
    active_input = None

    # --- hàm vẽ ---
    def update_grid_surf():
        grid_surf.fill(WHITE)
        for row in grid:
            for node in row:
                node.draw(grid_surf)
        draw_grid_lines(grid_surf, ROWS, width)

    def redraw_all():
        WIN.fill(BG_COLOR)
        # message phía trên
        if message:
            text_surf = FONT.render(message, True, BLACK)
            text_rect = text_surf.get_rect(center=(width // 2, TOP_UI_HEIGHT // 2))
            win.blit(text_surf, text_rect)

        # vẽ lưới chính
        win.blit(grid_surf, (0, TOP_UI_HEIGHT))

        # panel phải
        pygame.draw.rect(win, BG_COLOR, (width, TOP_UI_HEIGHT, TOTAL_RIGHT_PANEL, width))

        controls_text = [
            "Controls:",
            "  Left Click: Set Start, End, or draw Walls",
            "  Right Click: Delete a cell",
            "  Press C: Clear the entire map",
        ]
        for i, line in enumerate(controls_text):
            color = BLACK
            text_surf = FONT.render(line, True, color)
            win.blit(text_surf, (controls_x, controls_y + i * 28))

        # --- cách ra 1 đoạn rồi thêm tiêu đề Settings ---
        settings_title_y = controls_y + len(controls_text) * 28 + 40
        title_surf = FONT.render("Settings:", True, (0, 0, 0))
        win.blit(title_surf, (controls_x, settings_title_y))

        # --- vẽ label + input ---
        for i, label in enumerate(input_labels):
            label_surf = FONT.render(label, True, BLACK)
            label_y = settings_title_y + 30 + i * (input_height + input_gap)
            win.blit(label_surf, (controls_x, label_y + 5))

            rect = input_rects[i]
            rect.y = label_y  # cập nhật vị trí vẽ theo tiêu đề
            pygame.draw.rect(win, WHITE, rect)
            border_col = (0, 120, 215) if active_input == i else BLACK
            pygame.draw.rect(win, border_col, rect, 2)
            txt_surf = FONT.render(input_texts[i], True, BLACK)
            win.blit(txt_surf, (rect.x + 6, rect.y + (rect.height - txt_surf.get_height()) // 2))

        # nút Apply
        apply_rect.y = settings_title_y + 30 + len(input_labels) * (input_height + input_gap) + 8
        draw_button(win, apply_rect, "Apply", BUTTON)

        # nút thuật toán
        for i, rect in enumerate(buttons):
            draw_button(win, rect, button_texts[i], button_colors[i])
        pygame.display.update()

    def algo_draw():
        update_grid_surf()
        win.blit(grid_surf, (0, TOP_UI_HEIGHT))
        pygame.display.update()

    update_grid_surf()
    redraw_all()

    # --- vòng lặp chính ---
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if started:
                continue

            # --- xử lý click input + apply ---
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                clicked_input = None
                for i, rect in enumerate(input_rects):
                    if rect.collidepoint(pos):
                        clicked_input = i
                        break
                if clicked_input is not None:
                    active_input = clicked_input
                    continue

                if apply_rect.collidepoint(pos):
                    try:
                        v1 = int(input_texts[0].strip())
                    except ValueError:
                        v1 = MAX_RESTART  # fallback về constant

                    try:
                        v2 = int(input_texts[1].strip())
                    except ValueError:
                        v2 = DELAY  # fallback về constant

                    max_restart = v1
                    delay = v2
                    message = f"Applied: max_restart={max_restart}, delay={delay}"
                    active_input = None
                    continue

                active_input = None

            # --- nhập phím vào input ---
            if event.type == pygame.KEYDOWN and active_input is not None:
                if event.key == pygame.K_BACKSPACE:
                    input_texts[active_input] = input_texts[active_input][:-1]
                elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    if active_input < len(input_texts) - 1:
                        active_input += 1
                    else:
                        active_input = None
                else:
                    ch = event.unicode
                    if ch.isprintable() and len(input_texts[active_input]) < 40:
                        input_texts[active_input] += ch

            # xử lý nhấp chuột trái trong lưới và nút thuật toán
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
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
                elif pos[1] >= TOP_UI_HEIGHT + width:
                    for i, rect in enumerate(buttons):
                        if rect.collidepoint(pos):
                            algo_name = button_texts[i]

                            if algo_name == "Random map":
                                grid = make_grid(ROWS, width)
                                density = conf.DENSITY
                                for r in grid:
                                    for node in r:
                                        if random.random() < density:
                                            node.make_wall()
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

                            if not start or not end:
                                message = "Vui long dat start va end truoc khi chay thuat toan."
                                redraw_all()
                                break

                            started = True
                            message = ""
                            redraw_all()

                            for r in grid:
                                for node in r:
                                    node.update_neighbors(grid)

                            found = False
                            current_node = Node(-1, -1, 0, 0, is_null=True)
                            current_heuristic = 0

                            if algo_name == "Stochastic":
                                found, current_heuristic, current_node, message = Stochastic(algo_draw, grid, start, end, delay=delay)
                            elif algo_name == "Random Restart":
                                found, current_heuristic, current_node, message = RandomRestart(algo_draw, grid, start, end, delay=delay, max_restarts=max_restart)
                            elif algo_name == "Simple":
                                found, current_heuristic, current_node, message = Simple(algo_draw, grid, start, end, delay=delay)
                            elif algo_name == "Steepest Ascent":
                                found, current_heuristic, current_node, message = Steepest_Ascent(algo_draw, grid, start, end, delay=delay)

                            if not found:
                                node_x, node_y = current_node.get_pos()
                                if message == "":
                                    message = f"Bi mat ket tai ({node_x + 1},{node_y + 1}) va heuristic hien tai la {current_heuristic}"
                            else:
                                message = f"Da tim thay nha voi {algo_name}!"
                            started = False
                            break

            # xử lý nhấp chuột phải
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

            # bàn phím C để clear
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
                    message = "Da reset ban do."

        update_grid_surf()
        redraw_all()

    pygame.quit()
