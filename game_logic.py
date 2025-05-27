# pacman/game_logic.py
from heapq import heappush, heappop
import random
from .constants import ROWS, COLS, WARP_ROW, GHOST_SPAWN, RESPAWN_DELAY, POWER_MODE_DELAY, MAZES, BLUE, RED, PINK, ORANGE

def heuristic(a, b):
    base_dist = abs(a[0] - b[0]) + abs(a[1] - b[1])
    if a[0] == WARP_ROW and b[0] == WARP_ROW:
        warp_dist = min(abs(a[1] - b[1]), abs(a[1] - 0) + abs(b[1] - (COLS-1)) + 1, abs(a[1] - (COLS-1)) + abs(b[1] - 0) + 1)
        return min(base_dist, warp_dist)
    return base_dist

def is_path_safe(pacman_pos, target, ghosts, maze, safe_dist=4):
    """Check if the straight-line path to the target is safe from ghosts."""
    for ghost in ghosts:
        if not ghost["eaten"] and ghost["respawn_timer"] == 0:
            ghost_pos = ghost["pos"]
            # Approximate straight-line path by checking points between Pac-Man and target
            for t in range(1, 11):
                t = t / 10
                interp_row = pacman_pos[0] + t * (target[0] - pacman_pos[0])
                interp_col = pacman_pos[1] + t * (target[1] - pacman_pos[1])
                interp_pos = (interp_row, interp_col)
                dist_to_ghost = heuristic(interp_pos, ghost_pos)
                if dist_to_ghost < safe_dist:
                    print(f"Path to {target} is unsafe: ghost at {ghost_pos} too close (dist={dist_to_ghost})")
                    return False
    return True

def a_star(start, goal, maze, ghosts, power_mode):
    open_set = []
    heappush(open_set, (0, start))
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}
    while open_set:
        current = heappop(open_set)[1]
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]
        neighbors = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            neighbor = (current[0] + dr, current[1] + dc)
            if 0 <= neighbor[0] < ROWS and 0 <= neighbor[1] < COLS and maze[neighbor[0]][neighbor[1]] != 1:
                ghost_penalty = 0
                if not power_mode:
                    for ghost in ghosts:
                        if not ghost["eaten"] and ghost["respawn_timer"] == 0:
                            dist_to_ghost = heuristic(neighbor, tuple(ghost["pos"]))
                            if dist_to_ghost < 4:  # Increased radius
                                ghost_penalty += 100  # Increased penalty
                neighbors.append((neighbor, 1 + ghost_penalty))
        if abs(current[0] - WARP_ROW) <= 2:
            if current[1] == 0 or heuristic(current, (WARP_ROW, 0)) <= 2:
                neighbors.append(((WARP_ROW, COLS-1), 0.1))
                print(f"Added warp path to [7, {COLS-1}] from {current}")
            if current[1] == COLS-1 or heuristic(current, (WARP_ROW, COLS-1)) <= 2:
                neighbors.append(((WARP_ROW, 0), 0.1))
                print(f"Added warp path to [7, 0] from {current}")
        for neighbor, cost in neighbors:
            tentative_g_score = g_score[current] + cost
            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                heappush(open_set, (f_score[neighbor], neighbor))
    print(f"No path from {start} to {goal}")
    return None

def find_target(pacman_pos, maze, ghosts, power_mode, power_timer):
    nearest_ghost_dist = float('inf')
    nearest_ghost_pos = None
    ghost_count_within_5 = 0
    for ghost in ghosts:
        if not ghost["eaten"] and ghost["respawn_timer"] == 0:
            dist = heuristic(pacman_pos, ghost["pos"])
            if dist < nearest_ghost_dist:
                nearest_ghost_dist = dist
                nearest_ghost_pos = ghost["pos"]
            if dist < 5:
                ghost_count_within_5 += 1
    if power_mode:
        min_dist = float('inf')
        target = None
        for ghost in ghosts:
            if not ghost["eaten"] and ghost["respawn_timer"] == 0:
                dist = heuristic(pacman_pos, ghost["pos"])
                if dist < min_dist:
                    min_dist = dist
                    target = tuple(ghost["pos"])
        if target:
            print(f"Chasing ghost at {target} in power mode")
            return target
    if not power_mode and (nearest_ghost_dist < 4 or ghost_count_within_5 >= 2):
        min_score = float('inf')
        target = None
        for r in range(ROWS):
            for c in range(COLS):
                if maze[r][c] == 3:
                    dist = heuristic(pacman_pos, (r, c))
                    too_close_to_ghost = any(heuristic((r, c), ghost["pos"]) < 1.5 for ghost in ghosts if not ghost["eaten"] and ghost["respawn_timer"] == 0)
                    path_safe = is_path_safe(pacman_pos, (r, c), ghosts, maze)
                    if not too_close_to_ghost and path_safe:
                        score = dist / 2
                        if score < min_score:
                            min_score = score
                            target = (r, c)
        if target:
            print(f"Targeting power pellet at {target} to escape danger")
            return target
        warp_0 = (WARP_ROW, 0)
        warp_29 = (WARP_ROW, COLS-1)
        dist_to_warp_0 = heuristic(warp_0, nearest_ghost_pos)
        dist_to_warp_29 = heuristic(warp_29, nearest_ghost_pos)
        target = warp_0 if dist_to_warp_0 > dist_to_warp_29 else warp_29
        print(f"Fleeing to warp tunnel at {target}, ghost at {nearest_ghost_pos}")
        return target
    min_score = float('inf')
    target = None
    spawn_avoidance_radius = 2 if (power_mode and power_timer < 30) else 1
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] in [2, 3]:
                dist = heuristic(pacman_pos, (r, c))
                too_close_to_ghost = (not power_mode and any(heuristic((r, c), ghost["pos"]) < 4 for ghost in ghosts if not ghost["eaten"] and ghost["respawn_timer"] == 0))
                too_close_to_spawn = heuristic((r, c), GHOST_SPAWN) < spawn_avoidance_radius
                path_safe = is_path_safe(pacman_pos, (r, c), ghosts, maze)
                if not too_close_to_ghost and not too_close_to_spawn and path_safe:
                    score = dist / 2 if maze[r][c] == 3 else dist - (2 if c >= 14 else 0)
                    if score < min_score:
                        min_score = score
                        target = (r, c)
    return target

def move_ghost(ghost, maze, pacman_pos, power_mode):
    if ghost["eaten"] or ghost["respawn_timer"] > 0 or ghost["start_delay"] > 0:
        ghost["start_delay"] = max(0, ghost["start_delay"] - 1)
        return
    if ghost["warp_delay"] > 0:
        ghost["warp_delay"] -= 1
        return
    ghost["move_timer"] += 1
    speed_threshold = 3.6 if ghost["slowdown_timer"] > 0 else 1.65
    if ghost["move_timer"] < speed_threshold:
        return
    ghost["move_timer"] = 0
    if ghost["slowdown_timer"] > 0:
        ghost["slowdown_timer"] -= 1
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    new_row = ghost["pos"][0]
    new_col = ghost["pos"][1]
    if power_mode:
        if not ghost["was_in_power_mode"]:
            move = (-ghost["last_move"][0], -ghost["last_move"][1]) if ghost["last_move"] != (0, 0) else random.choice(directions)
            ghost["was_in_power_mode"] = True
        else:
            valid_directions = [(dr, dc) for dr, dc in directions 
                               if 0 <= new_row + dr < ROWS and 0 <= new_col + dc < COLS 
                               and maze[new_row + dr][new_col + dc] != 1 
                               and (heuristic([new_row + dr, new_col + dc], pacman_pos) <= 8 or random.random() < 0.2)]
            move = random.choice(valid_directions or directions)
    else:
        ghost["was_in_power_mode"] = False
        row_diff = pacman_pos[0] - ghost["pos"][0]
        col_diff = pacman_pos[1] - ghost["pos"][1]
        move = (0, 0)
        if abs(row_diff) > abs(col_diff):
            move = (1 if row_diff > 0 else -1, 0)
        else:
            move = (0, 1 if col_diff > 0 else -1)
        if random.random() < 0.25:
            move = random.choice(directions)
    new_row += move[0]
    new_col += move[1]
    if new_row == WARP_ROW:
        if new_col < 0:
            new_col = COLS - 1
            ghost["warp_delay"] = 22.5
            ghost["slowdown_timer"] = 45
            print(f"Ghost warped from [{new_row}, 0] to [{new_row}, {new_col}]")
        elif new_col >= COLS:
            new_col = 0
            ghost["warp_delay"] = 22.5
            ghost["slowdown_timer"] = 45
            print(f"Ghost warped from [{new_row}, {COLS-1}] to [{new_row}, {new_col}]")
    if 0 <= new_row < ROWS and 0 <= new_col < COLS and maze[new_row][new_col] != 1:
        ghost["pos"][0] = new_row
        ghost["pos"][1] = new_col
        ghost["last_move"] = move

def check_collision(pacman_pos, ghosts, power_mode, score, ghosts_eaten):
    for ghost in ghosts:
        if not ghost["eaten"] and ghost["respawn_timer"] == 0:
            if pacman_pos[0] == ghost["pos"][0] and pacman_pos[1] == ghost["pos"][1]:
                if power_mode:
                    ghost["eaten"] = True
                    ghost["respawn_timer"] = RESPAWN_DELAY
                    ghost["color"] = ghost["base_color"]
                    print(f"Ate ghost at {ghost['pos']} (color: {ghost['color']})")
                    score += 200 * (ghosts_eaten + 1)
                    ghosts_eaten += 1
                    return "eat_ghost", score, ghosts_eaten, True
                else:
                    print(f"Game Over! Collided with ghost at {ghost['pos']}. Score: {score}")
                    return "game_over", score, ghosts_eaten, False
    return None, score, ghosts_eaten, False

def reset_level(current_level):
    maze = [row[:] for row in MAZES[current_level]]
    pacman_pos = [1, 1]
    direction = "RIGHT"
    ghosts = [
        {"pos": [10, 15], "color": RED, "base_color": RED, "eaten": False, "respawn_timer": 0, "move_timer": 0, "start_delay": 0, "last_move": (0, 0), "was_in_power_mode": False, "warp_delay": 0, "slowdown_timer": 0},
        {"pos": [10, 16], "color": PINK, "base_color": PINK, "eaten": False, "respawn_timer": 0, "move_timer": 0, "start_delay": 15, "last_move": (0, 0), "was_in_power_mode": False, "warp_delay": 0, "slowdown_timer": 0},
        {"pos": [11, 15], "color": ORANGE, "base_color": ORANGE, "eaten": False, "respawn_timer": 0, "move_timer": 0, "start_delay": 30, "last_move": (0, 0), "was_in_power_mode": False, "warp_delay": 0, "slowdown_timer": 0},
        {"pos": [11, 16], "color": BLUE, "base_color": BLUE, "eaten": False, "respawn_timer": 0, "move_timer": 0, "start_delay": 45, "last_move": (0, 0), "was_in_power_mode": False, "warp_delay": 0, "slowdown_timer": 0}
    ]
    return maze, pacman_pos, direction, ghosts
