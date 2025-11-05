import pygame
import random
from model.model import Node
from config.constans import *
from config.utils import *


def RandomRestart(draw, grid, start, end, delay=DELAY, max_restarts=MAX_RESTART):
    """
    Random Restart Hill Climbing (đơn giản, không kiểm tra chu kỳ, không vẽ lại đường).
    Khi bị kẹt thì đánh dấu flag và restart từ một ô lân cận không phải tường hoặc flag.
    """

    message=""
    ClearOldPath(grid)
    current = start
    prev = None
    current_h = h(start.get_pos(), end.get_pos())
    restarts = 0

    rows = len(grid)
    cols = len(grid[0])

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    print("Random Restart Hill Climbing...")

    while restarts < max_restarts:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, current_h, current, message

        if current == end:
            end.make_end()
            return True, current_h, current, message

        x, y = current.get_pos()

        # Thu thập hàng xóm có heuristic nhỏ hơn (không phải tường/flag)
        candidates = []
        weights = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < rows and 0 <= ny < cols:
                neighbor = grid[nx][ny]
                if neighbor.is_wall() or neighbor.is_flag():
                    continue
                neighbor_h = h(neighbor.get_pos(), end.get_pos())
                if neighbor_h < current_h:
                    candidates.append(neighbor)
                    weights.append(max(1e-6, current_h - neighbor_h))

        # Nếu bị kẹt → đánh dấu flag và restart
        if not candidates:
            current.make_flag()
            draw()
            pygame.time.wait(delay)

            restarts += 1
            nearby_nodes = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    node = grid[nx][ny]
                    if not node.is_wall() and not node.is_flag():
                        nearby_nodes.append(node)

            if not nearby_nodes:
                message = f"khong co node nao tot hon ({x},{y}). h = {current_h}"
                return False, current_h, current, message

            new_start = random.choice(nearby_nodes)
            current = new_start
            current_h = h(current.get_pos(), end.get_pos())
            current.make_path()
            pygame.time.wait(delay)
            continue

        # Chọn ngẫu nhiên có trọng số trong candidates
        total = sum(weights)
        r = random.random() * total
        upto = 0
        chosen = candidates[-1]
        for cand, w in zip(candidates, weights):
            if upto + w >= r:
                chosen = cand
                break
            upto += w

        # Bước tới ô mới
        prev = current
        current = chosen
        current_h = h(current.get_pos(), end.get_pos())

        if current != end:
            current.make_path()

        draw()
        pygame.time.wait(delay)

    message = "Vuot qua so lan khoi tao lai!"
    return False, current_h, current, message
