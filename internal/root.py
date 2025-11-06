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

# thêm import cho plotting & delay nhẹ
import matplotlib.pyplot as plt
import time


def root(win=WIN, width=WIDTH):

    delay = DELAY
    max_restart = MAX_RESTART

    ROWS = conf.ROW
    density = getattr(conf, "DENSITY", 0.3)

    grid = make_grid(ROWS, width)
    start = None
    end = None
    run = True
    started = False
    message = ""

    grid_surf = pygame.Surface((width, width))

    # thêm "Run Experiments" vào danh sách nút
    button_texts = ["Simple", "Steepest Ascent", "Stochastic", "Random Restart", "Random map", "Run Experiments"]
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
    # thêm Density và Matrix (rows)
    input_labels = ["Max restart:", "Delay:", "Density:", "Matrix (rows):"]
    # khởi tạo hiển thị mặc định bằng giá trị hiện tại để người dùng biết
    input_texts = [str(MAX_RESTART), str(DELAY), str(density), str(ROWS)]
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

    # --- HÀM CHẠY THỬ NGHIỆM ---
    def run_experiments(runs_per_algo=100, show_plot=True):
        """
        Chạy nhiều lần (runs_per_algo) cho mỗi thuật toán.
        Trả về dict successes: {algo_name: success_count}
        """
        nonlocal message, started, max_restart, delay, ROWS, density

        # lưu vị trí start/end hiện tại (nếu người dùng đã đặt trên UI)
        orig_start_pos = (start.row, start.col) if start else None
        orig_end_pos = (end.row, end.col) if end else None

        algos = [
            ("Simple", Simple),
            ("Steepest Ascent", Steepest_Ascent),
            ("Stochastic", Stochastic),
            ("Random Restart", RandomRestart),
        ]

        successes = {name: 0 for name, _ in algos}

        # helper: kiểm tra node có phải wall không (tương thích nhiều implement)
        def node_is_wall(n):
            try:
                # nếu class có method is_wall()
                return n.is_wall()
            except Exception:
                # fallback: kiểm tra thuộc tính phổ biến
                return bool(getattr(n, "is_wall", False) or getattr(n, "wall", False) or getattr(n, "isWall", False))

        # vẽ im lặng (không update pygame) để truyền vào thuật toán
        def silent_draw():
            return

        pygame.display.set_caption("Running experiments... (please wait)")
        redraw_all()

        # dùng density hiện tại (từ input)
        for name, func in algos:
            for i in range(runs_per_algo):
                # tạo grid mới cho mỗi lần chạy
                trial_grid = make_grid(ROWS, width)

                # random walls theo density hiện tại
                for r in trial_grid:
                    for node in r:
                        if random.random() < density:
                            node.make_wall()

                # chọn start / end
                def pick_free_node():
                    # random chọn ô không phải wall
                    attempts = 0
                    while True:
                        rr = random.randrange(ROWS)
                        cc = random.randrange(ROWS)
                        n = trial_grid[rr][cc]
                        if not node_is_wall(n):
                            return n
                        attempts += 1
                        if attempts > ROWS * ROWS * 2:
                            # fallback: trả node bất kỳ nếu mọi ô đều là wall (hiếm)
                            return n

                if orig_start_pos:
                    s_row, s_col = orig_start_pos
                    # nếu vị trí vượt quá ROWS mới, cố clamp
                    s_row = min(s_row, ROWS - 1)
                    s_col = min(s_col, ROWS - 1)
                    s_node = trial_grid[s_row][s_col]
                else:
                    s_node = pick_free_node()
                s_node.make_start()

                if orig_end_pos:
                    e_row, e_col = orig_end_pos
                    e_row = min(e_row, ROWS - 1)
                    e_col = min(e_col, ROWS - 1)
                    e_node = trial_grid[e_row][e_col]
                else:
                    e_node = pick_free_node()
                    while e_node == s_node:
                        e_node = pick_free_node()
                e_node.make_end()

                # cập nhật neighbors
                for r in trial_grid:
                    for node in r:
                        node.update_neighbors(trial_grid)

                # gọi thuật toán (delay=0 cho nhanh)
                try:
                    if name == "Random Restart":
                        found, _, _, _ = func(silent_draw, trial_grid, s_node, e_node, delay=0, max_restarts=max_restart)
                    else:
                        found, _, _, _ = func(silent_draw, trial_grid, s_node, e_node, delay=0)
                except Exception as exc:
                    found = False
                    print(f"[Experiment error] {name} run {i}: {exc}")

                if found:
                    successes[name] += 1

            # nhẹ pause để hệ thống ổn định
            time.sleep(0.02)

        pygame.display.set_caption("Experiments finished")
        redraw_all()

        # tính phần trăm
        names = [n for n, _ in algos]
        counts = [successes[n] for n in names]
        pcts = [c * 100.0 / runs_per_algo for c in counts]

        if show_plot:
            plt.figure(figsize=(8, 5))
            bars = plt.bar(names, pcts)
            plt.ylim(0, 100)
            plt.ylabel("Success rate (%)")
            plt.title(f"Success rate — {runs_per_algo} runs per algorithm")
            for i, v in enumerate(pcts):
                plt.text(i, v + 1.5, f"{counts[i]}/{runs_per_algo}\n{v:.1f}%", ha="center", fontsize=9)
            plt.tight_layout()
            plt.show()

        return successes

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
                    # parse và apply 4 inputs: max_restart, delay, density, rows
                    try:
                        v1 = int(input_texts[0].strip())
                    except Exception:
                        v1 = max_restart  # fallback về current

                    try:
                        v2 = int(input_texts[1].strip())
                    except Exception:
                        v2 = delay  # fallback về current

                    try:
                        v3 = float(input_texts[2].strip())
                        # clamp density vào [0,1]
                        if v3 < 0:
                            v3 = 0.0
                        if v3 > 1:
                            v3 = 1.0
                    except Exception:
                        v3 = density  # fallback về current

                    try:
                        v4 = int(input_texts[3].strip())
                        if v4 < 2:
                            v4 = 2
                        if v4 > 200:
                            v4 = 200
                    except Exception:
                        v4 = ROWS  # fallback

                    # apply giá trị
                    max_restart = v1
                    delay = v2
                    density = v3

                    if v4 != ROWS:
                        ROWS = v4
                        grid = make_grid(ROWS, width)
                        if start:
                            if start.row < ROWS and start.col < ROWS:
                                start = grid[start.row][start.col]
                                start.make_start()
                            else:
                                start = None
                        if end:
                            if end.row < ROWS and end.col < ROWS:
                                end = grid[end.row][end.col]
                                end.make_end()
                            else:
                                end = None

                    message = f"Applied: max_restart={max_restart}, delay={delay}, density={density}, nodes={ROWS*ROWS}"
                    active_input = None
                    update_grid_surf()
                    redraw_all()
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
                    if ch.isprintable() and len(input_texts[active_input]) < 80:
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
                                for r in grid:
                                    for node in r:
                                        if random.random() < density:
                                            node.make_wall()
                                if start:
                                    if start.row < ROWS and start.col < ROWS:
                                        start = grid[start.row][start.col]
                                        start.make_start()
                                    else:
                                        start = None
                                if end:
                                    if end.row < ROWS and end.col < ROWS:
                                        end = grid[end.row][end.col]
                                        end.make_end()
                                    else:
                                        end = None
                                message = "Random map."
                                update_grid_surf()
                                redraw_all()
                                break

                            if algo_name == "Run Experiments":
                                started = True
                                redraw_all()
                                try:
                                    results = run_experiments(runs_per_algo=100, show_plot=True)
                                    #message = "Experiments done: " + ", ".join([f"{k}: {v}/72" for k, v in results.items()])
                                except Exception as e:
                                    message = f"Error running experiments: {e}"
                                started = False
                                redraw_all()
                                break

                            if not start or not end:
                                message = "Vui lòng đặt start và end trước khi chạy thuật toán."
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
                                    message = f"Bi mac ket tai ({node_x + 1},{node_y + 1}), heuristic hien tai la {current_heuristic}"
                            else:
                                message = f"Đã tìm thấy nha với {algo_name}!"
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
