
# main.py
import pygame
from pacman.constants import WIDTH, HEIGHT, MAZES, POWER_MODE_DELAY, END_SCREEN_DELAY, BLUE, BLACK, WARP_ROW, ROWS, COLS
from pacman.rendering import draw_maze, draw_pacman, draw_ghosts, draw_game_over_screen, draw_win_screen, draw_hud
from pacman.game_logic import a_star, find_target, move_ghost, check_collision, reset_level, heuristic

def is_path_still_safe(path, ghosts, safe_dist=3):
    """Check if the remaining path is still safe from ghosts."""
    for pos in path:
        for ghost in ghosts:
            if not ghost["eaten"] and ghost["respawn_timer"] == 0:
                dist_to_ghost = heuristic(pos, ghost["pos"])
                if dist_to_ghost < safe_dist:
                    print(f"Path unsafe: ghost at {ghost['pos']} too close to path position {pos} (dist={dist_to_ghost})")
                    return False
    return True

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    # Initialize game state
    current_level = 0
    maze, pacman_pos, direction, ghosts = reset_level(current_level)
    score = 0
    power_mode = False
    power_timer = 0
    ghosts_eaten = 0
    game_state = "playing"
    end_screen_timer = 0
    path = []
    recalculate_path = True
    move_timer = 0
    mouth_open = True
    mouth_timer = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if game_state == "game_over":
            draw_game_over_screen(screen, score)
            end_screen_timer += 1
            if end_screen_timer >= END_SCREEN_DELAY:
                running = False
            pygame.display.flip()
            clock.tick(15)
            continue
        elif game_state == "win":
            draw_win_screen(screen, score)
            end_screen_timer += 1
            if end_screen_timer >= END_SCREEN_DELAY:
                running = False
            pygame.display.flip()
            clock.tick(15)
            continue

        if game_state == "playing":
            # Recalculate path if needed or if the current path becomes unsafe
            if path and not power_mode:
                if not is_path_still_safe(path, ghosts):
                    print("Path became unsafe, recalculating...")
                    path = []
                    recalculate_path = True

            if recalculate_path or not path or pacman_pos == list(path[-1]):
                target = find_target(pacman_pos, maze, ghosts, power_mode, power_timer)
                if target:
                    path = a_star(tuple(pacman_pos), target, maze, ghosts, power_mode) or []
                recalculate_path = False

            move_timer += 1
            delay = POWER_MODE_DELAY if power_mode else 0.9
            if path and move_timer >= delay:
                next_pos = list(path[0])
                if not power_mode:
                    for ghost in ghosts:
                        if not ghost["eaten"] and ghost["respawn_timer"] == 0:
                            if heuristic(pacman_pos, ghost["pos"]) < 1.5:
                                print(f"Ghost too close at {ghost['pos']}, recalculating path")
                                recalculate_path = True
                                path = []
                                break
                if path:
                    if next_pos[0] == WARP_ROW:
                        if next_pos[1] < 0:
                            next_pos[1] = COLS - 1
                            print(f"Pac-Man warped from [{next_pos[0]}, 0] to [{next_pos[0]}, {next_pos[1]}]")
                        elif next_pos[1] >= COLS:
                            next_pos[1] = 0
                            print(f"Pac-Man warped from [{next_pos[0]}, {COLS-1}] to [{next_pos[0]}, {next_pos[1]}]")
                    if next_pos[0] < pacman_pos[0]:
                        direction = "UP"
                    elif next_pos[0] > pacman_pos[0]:
                        direction = "DOWN"
                    elif next_pos[1] < pacman_pos[1]:
                        direction = "LEFT"
                    elif next_pos[1] > pacman_pos[1]:
                        direction = "RIGHT"
                    pacman_pos[0], pacman_pos[1] = next_pos
                    path.pop(0)
                    move_timer = 0
                    collision, score, ghosts_eaten, recalculate_path = check_collision(pacman_pos, ghosts, power_mode, score, ghosts_eaten)
                    if collision == "game_over":
                        game_state = "game_over"
                        continue
                    elif collision == "eat_ghost":
                        recalculate_path = True
            if maze[pacman_pos[0]][pacman_pos[1]] == 2:
                maze[pacman_pos[0]][pacman_pos[1]] = 0
                score += 10
            elif maze[pacman_pos[0]][pacman_pos[1]] == 3:
                maze[pacman_pos[0]][pacman_pos[1]] = 0
                score += 50
                power_mode = True
                power_timer = 60
                for ghost in ghosts:
                    if not ghost["eaten"] and ghost["respawn_timer"] == 0:
                        ghost["color"] = BLUE
                recalculate_path = True
            all_cleared = all(maze[r][c] not in [2, 3] for r in range(ROWS) for c in range(COLS))
            if all_cleared:
                current_level += 1
                if current_level < len(MAZES):
                    print(f"Level {current_level + 1} Start! Score: {score}")
                    maze, pacman_pos, direction, ghosts = reset_level(current_level)
                    power_mode = False
                    power_timer = 0
                    ghosts_eaten = 0
                    path = []
                    recalculate_path = True
                    move_timer = 0
                else:
                    print(f"You Win All Levels! Final Score: {score}")
                    game_state = "win"
            for ghost in ghosts:
                if ghost["respawn_timer"] > 0:
                    ghost["respawn_timer"] -= 1
                    if ghost["respawn_timer"] == 0:
                        ghost["eaten"] = False
                        ghost["pos"] = [10, 15]
                        ghost["color"] = BLUE if power_mode else ghost["base_color"]
                else:
                    move_ghost(ghost, maze, pacman_pos, power_mode)
                    collision, score, ghosts_eaten, recalculate = check_collision(pacman_pos, ghosts, power_mode, score, ghosts_eaten)
                    if collision == "game_over":
                        game_state = "game_over"
                        continue
                    elif collision == "eat_ghost":
                        recalculate_path = True
            if power_mode:
                power_timer -= 1
                if power_timer <= 0:
                    power_mode = False
                    ghosts_eaten = 0
                    for ghost in ghosts:
                        if ghost["respawn_timer"] == 0:
                            ghost["color"] = ghost["base_color"]
                        ghost["was_in_power_mode"] = False
                    recalculate_path = True

        screen.fill(BLACK)
        draw_maze(screen, maze)
        mouth_open, mouth_timer = draw_pacman(screen, pacman_pos, direction, mouth_open, mouth_timer)
        draw_ghosts(screen, ghosts)
        draw_hud(screen, score, current_level)
        pygame.display.flip()
        clock.tick(15)

    pygame.quit()

if __name__ == "__main__":
    main()
