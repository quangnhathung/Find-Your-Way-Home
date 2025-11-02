import pygame
from config.utils import *

def Simple(draw, grid, start, end, delay=75):
    """
    Simple Hill Climbing:
    - Chọn neighbor đầu tiên có h(neighbor, end) < h(current, end)
    - Trả về True nếu tìm thấy end, False nếu mắc kẹt hoặc thoát
    """
    came_from = {}
    current = start
    visited = {start}
    current_h = h(start.get_pos(), end.get_pos())
    print("Leo đồi đơn giản...")

    while True:
        # xử lý sự kiện (để có thể đóng cửa sổ)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, current_h, current

        # nếu đã tới đích
        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True, current_h, current

        # tìm neighbor đầu tiên tốt hơn (heuristic nhỏ hơn)
        found_better = False
        for neighbor in current.neighbors:
            if neighbor in visited or neighbor.is_wall():
                continue

            neighbor_h = h(neighbor.get_pos(), end.get_pos())
            if neighbor_h < current_h:
                # chuyển sang neighbor này
                came_from[neighbor] = current
                current = neighbor
                visited.add(current)
                current_h = neighbor_h

                if current != end:
                    current.make_open()
                found_better = True
                break  # đơn giản: lấy ngay neighbor đầu tiên tốt hơn

        # nếu không có neighbor nào tốt hơn => mắc kẹt
        if not found_better:
            current.make_closed()
            draw()
            return False, current_h, current

        # vẽ và chờ 1 khoảng
        draw()
        pygame.time.wait(delay)
