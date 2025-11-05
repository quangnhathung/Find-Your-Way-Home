import pygame
import random
from model.model import Node
from config.constans import *
from config.utils import *


def RandomRestart(draw, grid, start, end, delay=400, max_restarts=30):
    """
    Robust Random Restart Hill Climbing (4-direction only).
    - Allow revisiting visited nodes.
    - Do NOT enter flag or wall nodes.
    - When stuck: mark current as flag; if current has no parent but prev exists, set came_from[current]=prev.
    - When choosing new_start, set came_from[new_start] = current (flag) to keep chain.
    - Always overwrite came_from when moving into a node (so reconstruct reflects latest chain).
    Returns: (found: bool, final_h: int, current_node)
    """
    came_from = {}
    current = start
    prev = None
    path_nodes = {start}
    current_h = h(start.get_pos(), end.get_pos())
    restarts = 0

    rows = len(grid)
    cols = len(grid[0])

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    print("Random Restart Hill Climbing (robust)...")

    while restarts < max_restarts:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False, current_h, current

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True, current_h, current

        x, y = current.get_pos()

        # collect only 4-direction neighbors that are not wall/flag
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
                    improvement = current_h - neighbor_h
                    if improvement <= 0:
                        improvement = 1e-6
                    candidates.append(neighbor)
                    weights.append(improvement)

        # stuck -> mark flag and restart from one of 4 neighbors (non-wall, non-flag)
        if not candidates:
            # if current has no parent in came_from but we have prev, link it to avoid breaking chain
            if current not in came_from and prev is not None:
                came_from[current] = prev

            # mark current as flag (visual) so algorithm won't revisit it
            current.make_flag()
            draw()
            pygame.time.wait(delay)

            restarts += 1
            nearby_nodes = []
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    node = grid[nx][ny]
                    # allow revisit visited nodes, but disallow wall/flag
                    if not node.is_wall() and not node.is_flag():
                        nearby_nodes.append(node)

            if not nearby_nodes:
                print(f"No available restart neighbors around ({x},{y}).")
                return False, current_h, current

            new_start = random.choice(nearby_nodes)
            # connect new_start back to current(flag) so chain remains continuous
            came_from[new_start] = current

            # update traversal pointers
            prev = current
            current = new_start
            path_nodes.add(current)
            current_h = h(current.get_pos(), end.get_pos())
            current.make_open()

            pygame.time.wait(delay)
            continue

        # weighted random pick among candidates
        total = sum(weights)
        r = random.random() * total
        upto = 0
        chosen = candidates[-1]
        for cand, w in zip(candidates, weights):
            if upto + w >= r:
                chosen = cand
                break
            upto += w

        # always overwrite came_from for chosen (ensures chain is up-to-date),
        # even if chosen was visited before
        came_from[chosen] = current

        # step forward
        prev = current
        current = chosen
        path_nodes.add(current)
        current_h = h(current.get_pos(), end.get_pos())

        if current != end:
            current.make_open()

        draw()
        pygame.time.wait(delay)

    print("Exceeded max restarts.")
    return False, current_h, current