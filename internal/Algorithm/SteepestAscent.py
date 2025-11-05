import pygame
import random
from config.utils import *

def Steepest_Ascent(draw, grid, start, end, delay=75):
    message = ""
    came_from = {}
    current = start
    path_nodes = {start}
    current_h = h(start.get_pos(), end.get_pos())
    print("Leo đồi cực dốc...")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, current_h, current, message

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True, current_h, current, message

        # tìm neighbor có heuristic nhỏ nhất
        best_neighbors = []
        min_h = current_h

        for neighbor in current.neighbors:
            if neighbor not in path_nodes and not neighbor.is_wall():
                neighbor_h = h(neighbor.get_pos(), end.get_pos())
                if neighbor_h < min_h:
                    min_h = neighbor_h
                    best_neighbors = [neighbor]  # reset danh sách
                elif neighbor_h == min_h:
                    best_neighbors.append(neighbor)  # thêm nếu bằng min_h

        # không có neighbor tốt hơn → mắc kẹt
        if not best_neighbors:
            current.make_closed()
            draw()
            return False, current_h, current, message

        # 🔀 chọn ngẫu nhiên 1 neighbor trong các ứng viên tốt nhất
        best_neighbor = random.choice(best_neighbors)

        came_from[best_neighbor] = current
        current = best_neighbor
        path_nodes.add(current)
        current_h = min_h

        if current != end:
            current.make_open()

        draw()
        pygame.time.wait(delay)
