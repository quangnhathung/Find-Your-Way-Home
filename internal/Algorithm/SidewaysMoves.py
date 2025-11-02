import pygame
import random
from config.utils import *
from config.config import *

conf = Config()

def Sideways(draw, grid, start, end, delay=75 ):
    """
    Hill Climbing with Sideways Moves:
    - Cho phép di chuyển sang neighbor có cùng heuristic (h = current_h)
      nhưng tối đa `max_sideways_moves` lần liên tiếp.
    - Nếu không có neighbor tốt hơn hoặc hết số lần sideways -> dừng.
    """
    came_from = {}
    current = start
    path_nodes = {start}
    current_h = h(start.get_pos(), end.get_pos())
    max_sideways_moves=conf.SidewaysMoves
    sideways_moves = 0

    print(f"Hill Climbing with Sideways Moves (max {max_sideways_moves})...")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, current_h, current

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True, current_h, current

        # Tìm các neighbor có h <= current_h
        best_neighbors = []
        min_h = current_h

        for neighbor in current.neighbors:
            if neighbor in path_nodes or neighbor.is_wall():
                continue

            neighbor_h = h(neighbor.get_pos(), end.get_pos())

            if neighbor_h < min_h:
                min_h = neighbor_h
                best_neighbors = [neighbor]
            elif neighbor_h == min_h:
                best_neighbors.append(neighbor)

        # Không có neighbor khả thi
        if not best_neighbors:
            current.make_closed()
            draw()
            return False, current_h, current

        # Chọn ngẫu nhiên 1 neighbor trong nhóm tốt nhất
        next_node = random.choice(best_neighbors)

        # Nếu bằng heuristic hiện tại (sideways move)
        if min_h == current_h:
            sideways_moves += 1
            if sideways_moves > max_sideways_moves:
                print("❌ Hết giới hạn sideways moves — mắc kẹt.")
                current.make_closed()
                draw()
                return False, current_h, current
        else:
            sideways_moves = 0  # reset nếu có tiến triển thật

        # Cập nhật trạng thái
        came_from[next_node] = current
        current = next_node
        path_nodes.add(current)
        current_h = min_h

        if current != end:
            current.make_open()

        draw()
        pygame.time.wait(delay)
