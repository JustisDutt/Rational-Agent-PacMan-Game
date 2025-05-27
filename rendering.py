# pacman/rendering.py
import pygame
import math
from .constants import WIDTH, HEIGHT, CELL_SIZE, OFFSET_X, OFFSET_Y, BLACK, YELLOW, RED, WHITE, BLUE, PURPLE, ROWS, COLS, WARP_ROW

def draw_maze(screen, maze):
    for row in range(ROWS):
        for col in range(COLS):
            x = OFFSET_X + col * CELL_SIZE
            y = OFFSET_Y + row * CELL_SIZE
            if maze[row][col] == 1:
                pygame.draw.rect(screen, BLUE, (x, y, CELL_SIZE, CELL_SIZE))
            elif maze[row][col] == 2:
                pygame.draw.circle(screen, WHITE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 3)
            elif maze[row][col] == 3:
                pygame.draw.circle(screen, WHITE, (x + CELL_SIZE // 2, y + CELL_SIZE // 2), 8)
            if row == WARP_ROW and col in [0, COLS-1]:
                pygame.draw.rect(screen, PURPLE, (x, y, CELL_SIZE, CELL_SIZE))

def draw_pacman(screen, pacman_pos, direction, mouth_open, mouth_timer):
    mouth_timer += 1
    if mouth_timer % 5 == 0:
        mouth_open = not mouth_open
    center_x = OFFSET_X + pacman_pos[1] * CELL_SIZE + CELL_SIZE // 2
    center_y = OFFSET_Y + pacman_pos[0] * CELL_SIZE + CELL_SIZE // 2
    radius = CELL_SIZE // 2
    if mouth_open:
        start_angle = {"RIGHT": 45, "LEFT": 225, "UP": 135, "DOWN": 315}[direction]
        end_angle = start_angle - 90 if direction in ["RIGHT", "DOWN"] else start_angle + 90
        pygame.draw.arc(screen, YELLOW, (center_x - radius, center_y - radius, radius * 2, radius * 2), 
                        math.radians(start_angle), math.radians(end_angle), radius)
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius - 2)
    else:
        pygame.draw.circle(screen, YELLOW, (center_x, center_y), radius)
    return mouth_open, mouth_timer

def draw_ghosts(screen, ghosts):
    for ghost in ghosts:
        if not ghost["eaten"] and ghost["respawn_timer"] == 0:
            pygame.draw.circle(screen, ghost["color"], 
                              (OFFSET_X + ghost["pos"][1] * CELL_SIZE + CELL_SIZE // 2, 
                               OFFSET_Y + ghost["pos"][0] * CELL_SIZE + CELL_SIZE // 2), 
                              CELL_SIZE // 2)

def draw_game_over_screen(screen, score):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    game_over_text = font.render("Game Over", True, RED)
    game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(game_over_text, game_over_rect)
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(score_text, score_rect)

def draw_win_screen(screen, score):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 72)
    win_text = font.render("You Win!", True, YELLOW)
    win_rect = win_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
    screen.blit(win_text, win_rect)
    font = pygame.font.SysFont(None, 48)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(score_text, score_rect)

def draw_hud(screen, score, current_level):
    font = pygame.font.SysFont(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    level_text = font.render(f"Level: {current_level + 1}", True, WHITE)
    screen.blit(score_text, (10, 10))
    screen.blit(level_text, (WIDTH - 100, 10))