import pygame
import random
from config.utils import *

def Stochastic(draw, grid, start, end, delay=DELAY):
    """
    Stochastic Hill Climbing:
    - Thu thập tất cả neighbor có h < current_h (tức là tốt hơn).
    - Gán trọng số w = current_h - neighbor_h (mức cải thiện).
    - Chọn ngẫu nhiên 1 neighbor theo phân phối trọng số (weights).
    - Nếu không có neighbor tốt hơn -> mắc kẹt (return False).
    """
    ClearOldPath(grid)
    message = ""
    came_from = {}
    current = start
    path_nodes = {start}
    current_h = h(start.get_pos(), end.get_pos())
    print("Stochastic Hill Climbing...")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, current_h, current, message

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True, current_h, current, message

        # thu thập các neighbor tốt hơn và trọng số cải thiện
        candidates = [] 
        weights = []    

        for neighbor in current.neighbors:
            if neighbor in path_nodes or neighbor.is_wall():
                continue
            neighbor_h = h(neighbor.get_pos(), end.get_pos())
            if neighbor_h < current_h:
                improvement = current_h - neighbor_h
                if improvement <= 0:
                    improvement = 1e-6
                candidates.append(neighbor)
                weights.append(improvement)

        if not candidates:
            current.make_closed()
            draw()
            return False, current_h, current, message

        # chọn ngẫu nhiên theo trọng số (nếu weights là [w1,w2,...])
        try:
            # random.choices trả về list, lấy phần tử đầu
            best_neighbor = random.choices(candidates, weights=weights, k=1)[0]
        except AttributeError:
            # fallback nếu random.choices không có (rất hiếm): chọn theo trọng số thủ công
            total = sum(weights)
            r = random.random() * total
            upto = 0
            best_neighbor = candidates[-1]
            for cand, w in zip(candidates, weights):
                if upto + w >= r:
                    best_neighbor = cand
                    break
                upto += w

        came_from[best_neighbor] = current
        current = best_neighbor
        path_nodes.add(current)
        current_h = h(current.get_pos(), end.get_pos())

        if current != end:
            current.make_open()

        draw()
        pygame.time.wait(delay)
