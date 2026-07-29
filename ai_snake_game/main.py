from collections import deque
import json
import math
import os
import pygame
import pygame_gui
import random
import sys

GRID_COLS, GRID_ROWS = 40, 30
INITIAL_WIDTH, INITIAL_HEIGHT = 800, 600
FPS, FOOD_COUNT = 60, 2

COLOR_BG_MENU = (18, 18, 18)
COLOR_TEXT_MENU = (255, 255, 255)
COLOR_TEXT_MENU_ACCENT = (0, 235, 235)
COLOR_TEXT_MENU_SUBTLE = (180, 190, 200)

COLOR_BG_PLAYING = (11, 12, 16)
COLOR_GRID_EVEN = (16, 15, 27)
COLOR_GRID_ODD = (21, 19, 36)
COLOR_GRID_LINE = (55, 30, 85)
COLOR_BORDER = (255, 0, 140)

COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY, COLOR_SNAKE_GLOW = (50, 255, 120), (20, 220, 80), (20, 255, 100)
COLOR_AI_HEAD, COLOR_AI_BODY, COLOR_AI_GLOW = (0, 255, 255), (0, 180, 255), (0, 220, 255)
COLOR_FOOD, COLOR_FOOD_GLOW = (255, 10, 120), (255, 20, 150)

COLOR_TEXT_HUD, COLOR_TEXT_GLOW, COLOR_VICTORY = (235, 245, 255), (190, 40, 255), (80, 255, 130)

STATE_WELCOME, STATE_NAME_ENTRY = "WELCOME", "NAME_ENTRY"
STATE_DIFFICULTY_SELECT, STATE_PLAYING, STATE_GAME_OVER = "DIFFICULTY_SELECT", "PLAYING", "GAME_OVER"
DIFF_EASY, DIFF_MEDIUM, DIFF_HARD = "EASY", "MEDIUM", "HARD"
WINNER_NONE, WINNER_PLAYER, WINNER_AI = "NONE", "PLAYER", "AI"

DIFFICULTY_CONFIGS = {
    DIFF_EASY: {"move_interval": 150, "winning_score": 7, "ai_flaw": 0.40, "title": "EASY",
                "desc": "<b>EASY MODE:</b><br>Slower Snake Speed (150ms). The AI makes frequent mistakes (40% flaw chance). Race to 7 points."},
    DIFF_MEDIUM: {"move_interval": 120, "winning_score": 10, "ai_flaw": 0.20, "title": "MEDIUM",
                  "desc": "<b>MEDIUM MODE:</b><br>Standard Speed (120ms). The AI occasionally miscalculates (20% flaw chance). Race to 10 points."},
    DIFF_HARD: {"move_interval": 90, "winning_score": 15, "ai_flaw": 0.10, "title": "HARD",
                "desc": "<b>HARD MODE:</b><br>Fast Cyber Speed (90ms). Aggressive BFS pathfinding (10% flaw chance). Race to 15 points."}
}

def ensure_theme_file(filepath):
    theme_dict = {
        "defaults": {
            "font": {"name": "Consolas", "size": "22", "bold": "1"},
            "colours": {
                "normal_bg": "#1F1F1F", "hovered_bg": "#333333", "disabled_bg": "#121212",
                "selected_bg": "#3C3C3C", "active_bg": "#4A4A4A", "normal_text": "#FFFFFF",
                "hovered_text": "#00FFFF", "selected_text": "#00FFFF", "disabled_text": "#787884",
                "normal_border": "#555555", "hovered_border": "#00FFFF", "disabled_border": "#282832",
                "selected_border": "#00FFFF", "active_border": "#00FFFF"
            }
        },
        "button": {
            "font": {"name": "Consolas", "size": "24", "bold": "1"},
            "colours": {"normal_bg": "#2A2A2A", "hovered_bg": "#3A3A3A", "active_bg": "#4A4A4A", "normal_text": "#FFFFFF", "hovered_text": "#00FFFF", "normal_border": "#555555", "hovered_border": "#00FFFF"},
            "misc": {"border_width": "3", "shadow_width": "0", "shape": "rounded_rectangle", "shape_corner_radius": "10"}
        },
        "text_entry_line": {
            "font": {"name": "Consolas", "size": "28", "bold": "1"},
            "colours": {"normal_bg": "#1A1A1A", "selected_bg": "#2A2A2A", "normal_text": "#FFFFFF", "selected_text": "#00FFFF", "normal_border": "#666666", "selected_border": "#00FFFF"},
            "misc": {"border_width": "3", "shadow_width": "0", "shape": "rounded_rectangle", "shape_corner_radius": "8"}
        },
        "text_box": {
            "font": {"name": "Consolas", "size": "22", "bold": "0"},
            "colours": {"normal_bg": "#181818", "normal_text": "#FFFFFF", "normal_border": "#444444"},
            "misc": {"border_width": "2", "shadow_width": "0", "shape": "rounded_rectangle", "shape_corner_radius": "10"}
        }
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(theme_dict, f, indent=2)

class AISnake:
    def __init__(self, start_gx, start_gy):
        self.reset(start_gx, start_gy)

    def reset(self, start_gx, start_gy):
        self.body = [(start_gx, start_gy), (start_gx + 1, start_gy), (start_gx + 2, start_gy)]
        self.previous_body = list(self.body)

    def get_next_move(self, player_body, food_list, ai_flaw_chance):
        head = self.body[0]
        obstacles = set(self.body) | set(player_body)
        if random.random() < ai_flaw_chance:
            safe_neighbors = [(head[0] + dx, head[1] + dy) for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]
                              if 0 <= head[0] + dx < GRID_COLS and 0 <= head[1] + dy < GRID_ROWS and (head[0] + dx, head[1] + dy) not in obstacles]
            if safe_neighbors:
                return random.choice(safe_neighbors)
        queue = deque([(head, [])])
        visited = {head}
        while queue:
            current, path = queue.popleft()
            if current in food_list:
                return path[0] if path else head
            gx, gy = current
            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = gx + dx, gy + dy
                neighbor = (nx, ny)
                if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and neighbor not in visited and (neighbor not in obstacles or neighbor in food_list):
                    visited.add(neighbor)
                    queue.append((neighbor, path + [neighbor]))
        safe_moves = []
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            nx, ny = head[0] + dx, head[1] + dy
            neighbor = (nx, ny)
            if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and neighbor not in obstacles:
                min_dist = min(abs(nx - fx) + abs(ny - fy) for fx, fy in food_list)
                safe_moves.append((min_dist, neighbor))
        if safe_moves:
            safe_moves.sort(key=lambda x: x[0])
            return safe_moves[0][1]
        return (head[0] + 1, head[1])

def get_board_layout(window_width, window_height):
    tile_size = max(4, min(window_width // GRID_COLS, window_height // GRID_ROWS))
    board_w, board_h = GRID_COLS * tile_size, GRID_ROWS * tile_size
    return tile_size, (window_width - board_w) // 2, (window_height - board_h) // 2, board_w, board_h

def draw_clean_text(surface, font, text, text_color, center_pos):
    main_surf = font.render(text, True, text_color)
    rect = main_surf.get_rect(center=center_pos)
    surface.blit(main_surf, rect)
    return rect

def draw_grid(surface, offset_x, offset_y, tile_size, board_width, board_height):
    board_rect = pygame.Rect(offset_x, offset_y, board_width, board_height)
    pygame.draw.rect(surface, COLOR_GRID_EVEN, board_rect)
    for y in range(GRID_ROWS):
        for x in range(GRID_COLS):
            if (x + y) % 2 == 1:
                pygame.draw.rect(surface, COLOR_GRID_ODD, (offset_x + x * tile_size, offset_y + y * tile_size, tile_size, tile_size))
    pygame.draw.rect(surface, COLOR_BORDER, board_rect, width=2)

def draw_glowing_rect(surface, color, glow_rgb, rect_tuple, border_radius=4):
    x, y, w, h = rect_tuple
    glow_pad = max(2, w // 6)
    glow_surf = pygame.Surface((w + glow_pad * 2, h + glow_pad * 2), pygame.SRCALPHA)
    pygame.draw.rect(glow_surf, (*glow_rgb, 55), (0, 0, w + glow_pad * 2, h + glow_pad * 2), border_radius=border_radius + 2)
    surface.blit(glow_surf, (x - glow_pad, y - glow_pad))
    pygame.draw.rect(surface, color, (x, y, w, h), border_radius=border_radius)

def draw_glowing_text(surface, font, text, text_color, glow_color, center_pos):
    for dx in (-1, 1):
        for dy in (-1, 1):
            glow_surf = font.render(text, True, glow_color)
            surface.blit(glow_surf, glow_surf.get_rect(center=(center_pos[0] + dx * 2, center_pos[1] + dy * 2)))
    main_surf = font.render(text, True, text_color)
    rect = main_surf.get_rect(center=center_pos)
    surface.blit(main_surf, rect)
    return rect

def draw_glowing_food(surface, fx, fy, offset_x, offset_y, tile_size):
    center_x = offset_x + fx * tile_size + tile_size // 2
    center_y = offset_y + fy * tile_size + tile_size // 2
    radius = max(3, int(tile_size * 0.38))
    pygame.draw.circle(surface, (180, 15, 95), (center_x, center_y), int(radius * 1.45))
    pygame.draw.circle(surface, COLOR_FOOD, (center_x, center_y), radius)
    pygame.draw.circle(surface, (255, 200, 225), (center_x - 1, center_y - 1), max(1, int(radius * 0.4)))

def draw_hud(surface, font, player_name, player_score, ai_score, diff_name, winning_score, offset_x, offset_y, board_width):
    hud_height = 36
    hud_y = max(5, offset_y - hud_height - 6) if offset_y >= 45 else 8
    banner = pygame.Surface((board_width, hud_height), pygame.SRCALPHA)
    banner.fill((10, 10, 25, 175))
    surface.blit(banner, (offset_x, hud_y))
    p_text = font.render(f"{player_name.upper()}: {player_score} / {winning_score}", True, COLOR_SNAKE_HEAD)
    surface.blit(p_text, p_text.get_rect(midleft=(offset_x + 15, hud_y + hud_height // 2)))
    div_text = font.render(f"[{diff_name}]", True, COLOR_BORDER)
    surface.blit(div_text, div_text.get_rect(center=(offset_x + board_width // 2, hud_y + hud_height // 2)))
    a_text = font.render(f"AI: {ai_score} / {winning_score}", True, COLOR_AI_HEAD)
    surface.blit(a_text, a_text.get_rect(midright=(offset_x + board_width - 15, hud_y + hud_height // 2)))

def get_random_food_position(occupied_cells):
    while True:
        gx, gy = random.randrange(0, GRID_COLS), random.randrange(0, GRID_ROWS)
        if (gx, gy) not in occupied_cells:
            return gx, gy

def reset_round_state():
    start_gx, start_gy = GRID_COLS // 4, GRID_ROWS // 2
    player_body = [(start_gx, start_gy), (start_gx - 1, start_gy), (start_gx - 2, start_gy)]
    ai_snake = AISnake(3 * GRID_COLS // 4, GRID_ROWS // 2)
    food_list = []
    occupied = set(player_body) | set(ai_snake.body)
    while len(food_list) < FOOD_COUNT:
        food_list.append(get_random_food_position(occupied | set(food_list)))
    return player_body, list(player_body), ai_snake, 1, 0, food_list, 0, 0, pygame.time.get_ticks(), [], WINNER_NONE

def setup_ui_for_state(state, ui_manager, width, height, player_name="", current_diff=DIFF_MEDIUM, selected_diff_idx=1):
    ui_manager.clear_and_reset()
    elements = {}
    if state == STATE_WELCOME:
        elements["btn_start"] = pygame_gui.elements.UIButton(pygame.Rect((width - 300) // 2, height // 2 + 55, 300, 70), 'START ARENA', manager=ui_manager)
    elif state == STATE_NAME_ENTRY:
        elements["entry_line"] = pygame_gui.elements.UITextEntryLine(pygame.Rect((width - 400) // 2, height // 2 - 15, 400, 60), manager=ui_manager)
        elements["entry_line"].set_text(player_name)
        elements["btn_continue"] = pygame_gui.elements.UIButton(pygame.Rect((width - 260) // 2, height // 2 + 70, 260, 65), 'CONTINUE', manager=ui_manager)
    elif state == STATE_DIFFICULTY_SELECT:
        btn_w, btn_h, gap = 230, 60, 25
        start_x, base_y = (width - (btn_w * 3 + gap * 2)) // 2, height // 2 - 95
        elements["btn_easy"] = pygame_gui.elements.UIButton(pygame.Rect(start_x, base_y, btn_w, btn_h), "> EASY <" if selected_diff_idx == 0 else "EASY", manager=ui_manager)
        elements["btn_medium"] = pygame_gui.elements.UIButton(pygame.Rect(start_x + btn_w + gap, base_y, btn_w, btn_h), "> MEDIUM <" if selected_diff_idx == 1 else "MEDIUM", manager=ui_manager)
        elements["btn_hard"] = pygame_gui.elements.UIButton(pygame.Rect(start_x + (btn_w + gap) * 2, base_y, btn_w, btn_h), "> HARD <" if selected_diff_idx == 2 else "HARD", manager=ui_manager)
        elements["desc_box"] = pygame_gui.elements.UITextBox(DIFFICULTY_CONFIGS[current_diff]["desc"], pygame.Rect((width - 740) // 2, base_y + btn_h + 25, 740, 125), manager=ui_manager)
        elements["btn_start_game"] = pygame_gui.elements.UIButton(pygame.Rect((width - 300) // 2, base_y + btn_h + 170, 300, 65), 'START GAME', manager=ui_manager)
    elif state == STATE_GAME_OVER:
        btn_w, btn_h, gap = 220, 60, 20
        start_x, base_y = (width - (btn_w * 3 + gap * 2)) // 2, height // 2 + 75
        elements["btn_play_again"] = pygame_gui.elements.UIButton(pygame.Rect(start_x, base_y, btn_w, btn_h), 'PLAY AGAIN', manager=ui_manager)
        elements["btn_diff"] = pygame_gui.elements.UIButton(pygame.Rect(start_x + btn_w + gap, base_y, btn_w, btn_h), 'DIFFICULTY', manager=ui_manager)
        elements["btn_menu"] = pygame_gui.elements.UIButton(pygame.Rect(start_x + (btn_w + gap) * 2, base_y, btn_w, btn_h), 'MAIN MENU', manager=ui_manager)
    return elements

def run_game():
    pygame.init()
    pygame.display.set_caption("AI-Enhanced Snake - Competition Edition")
    theme_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "theme.json")
    ensure_theme_file(theme_path)
    screen = pygame.display.set_mode((INITIAL_WIDTH, INITIAL_HEIGHT), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    ui_manager = pygame_gui.UIManager((INITIAL_WIDTH, INITIAL_HEIGHT), theme_path)
    font_small = pygame.font.SysFont("Consolas", 22, bold=True)
    font_medium = pygame.font.SysFont("Consolas", 28, bold=True)
    font_xl = pygame.font.SysFont("Consolas", 42, bold=True)
    font_large = pygame.font.SysFont("Consolas", 52, bold=True)
    is_fullscreen, windowed_size = False, (INITIAL_WIDTH, INITIAL_HEIGHT)
    game_state, player_name, selected_diff_idx, current_difficulty = STATE_WELCOME, "", 1, DIFF_MEDIUM
    ui_elements = setup_ui_for_state(game_state, ui_manager, INITIAL_WIDTH, INITIAL_HEIGHT, player_name, current_difficulty, selected_diff_idx)
    (player_body, previous_player_body, ai_snake, current_dir_x, current_dir_y,
     food_list, player_score, ai_score, last_move_time, input_queue, winner) = reset_round_state()

    while True:
        time_delta = clock.tick(FPS) / 1000.0
        now = pygame.time.get_ticks()
        cfg = DIFFICULTY_CONFIGS[current_difficulty]
        move_interval, winning_score, ai_flaw = cfg["move_interval"], cfg["winning_score"], cfg["ai_flaw"]

        for event in pygame.event.get():
            ui_manager.process_events(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.VIDEORESIZE and not is_fullscreen:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                windowed_size = (event.w, event.h)
                ui_manager.set_window_resolution((event.w, event.h))
                ui_elements = setup_ui_for_state(game_state, ui_manager, event.w, event.h, player_name, current_difficulty, selected_diff_idx)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    is_fullscreen = not is_fullscreen
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if is_fullscreen else pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                    ui_manager.set_window_resolution(screen.get_size())
                    ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                elif event.key in (pygame.K_ESCAPE, pygame.K_q) and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    pygame.quit()
                    sys.exit()
                elif game_state == STATE_NAME_ENTRY and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    entry_widget = ui_elements.get("entry_line")
                    if entry_widget:
                        player_name = entry_widget.get_text().strip() or "PLAYER"
                        game_state = STATE_DIFFICULTY_SELECT
                        ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                elif game_state == STATE_DIFFICULTY_SELECT:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        selected_diff_idx = max(0, selected_diff_idx - 1)
                        current_difficulty = [DIFF_EASY, DIFF_MEDIUM, DIFF_HARD][selected_diff_idx]
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selected_diff_idx = min(2, selected_diff_idx + 1)
                        current_difficulty = [DIFF_EASY, DIFF_MEDIUM, DIFF_HARD][selected_diff_idx]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        game_state = STATE_PLAYING
                        ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                        (player_body, previous_player_body, ai_snake, current_dir_x, current_dir_y,
                         food_list, player_score, ai_score, last_move_time, input_queue, winner) = reset_round_state()
                elif game_state == STATE_PLAYING:
                    ref_dx, ref_dy = input_queue[-1] if input_queue else (current_dir_x, current_dir_y)
                    new_dir = None
                    if (event.key in (pygame.K_UP, pygame.K_w)) and ref_dy == 0:
                        new_dir = (0, -1)
                    elif (event.key in (pygame.K_DOWN, pygame.K_s)) and ref_dy == 0:
                        new_dir = (0, 1)
                    elif (event.key in (pygame.K_LEFT, pygame.K_a)) and ref_dx == 0:
                        new_dir = (-1, 0)
                    elif (event.key in (pygame.K_RIGHT, pygame.K_d)) and ref_dx == 0:
                        new_dir = (1, 0)
                    if new_dir and len(input_queue) < 2:
                        input_queue.append(new_dir)
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                if game_state == STATE_WELCOME and event.ui_element == ui_elements.get("btn_start"):
                    game_state = STATE_NAME_ENTRY
                    ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                elif game_state == STATE_NAME_ENTRY and event.ui_element == ui_elements.get("btn_continue"):
                    entry_widget = ui_elements.get("entry_line")
                    if entry_widget:
                        player_name = entry_widget.get_text().strip() or "PLAYER"
                    game_state = STATE_DIFFICULTY_SELECT
                    ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                elif game_state == STATE_DIFFICULTY_SELECT:
                    if event.ui_element == ui_elements.get("btn_easy"):
                        selected_diff_idx, current_difficulty = 0, DIFF_EASY
                    elif event.ui_element == ui_elements.get("btn_medium"):
                        selected_diff_idx, current_difficulty = 1, DIFF_MEDIUM
                    elif event.ui_element == ui_elements.get("btn_hard"):
                        selected_diff_idx, current_difficulty = 2, DIFF_HARD
                    elif event.ui_element == ui_elements.get("btn_start_game"):
                        game_state = STATE_PLAYING
                        ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                        (player_body, previous_player_body, ai_snake, current_dir_x, current_dir_y,
                         food_list, player_score, ai_score, last_move_time, input_queue, winner) = reset_round_state()
                elif game_state == STATE_GAME_OVER:
                    if event.ui_element == ui_elements.get("btn_play_again"):
                        game_state = STATE_PLAYING
                        ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                        (player_body, previous_player_body, ai_snake, current_dir_x, current_dir_y,
                         food_list, player_score, ai_score, last_move_time, input_queue, winner) = reset_round_state()
                    elif event.ui_element == ui_elements.get("btn_diff"):
                        game_state = STATE_DIFFICULTY_SELECT
                        ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
                    elif event.ui_element == ui_elements.get("btn_menu"):
                        game_state = STATE_WELCOME
                        ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)

        if game_state == STATE_DIFFICULTY_SELECT:
            btn_easy, btn_medium, btn_hard = ui_elements.get("btn_easy"), ui_elements.get("btn_medium"), ui_elements.get("btn_hard")
            desc_box = ui_elements.get("desc_box")
            if btn_easy and btn_medium and btn_hard:
                btn_easy.set_text("> EASY <" if selected_diff_idx == 0 else "EASY")
                btn_medium.set_text("> MEDIUM <" if selected_diff_idx == 1 else "MEDIUM")
                btn_hard.set_text("> HARD <" if selected_diff_idx == 2 else "HARD")
            if desc_box and btn_easy and btn_medium and btn_hard:
                hovered_text = None
                if btn_easy.hovered:
                    hovered_text = DIFFICULTY_CONFIGS[DIFF_EASY]["desc"]
                elif btn_medium.hovered:
                    hovered_text = DIFFICULTY_CONFIGS[DIFF_MEDIUM]["desc"]
                elif btn_hard.hovered:
                    hovered_text = DIFFICULTY_CONFIGS[DIFF_HARD]["desc"]
                target_text = hovered_text if hovered_text else f"<b>SELECTED ({current_difficulty}):</b><br>" + DIFFICULTY_CONFIGS[current_difficulty]["desc"]
                if desc_box.html_text != target_text:
                    desc_box.set_text(target_text)

        if game_state == STATE_PLAYING and now - last_move_time >= move_interval:
            last_move_time = now
            previous_player_body = list(player_body)
            ai_snake.previous_body = list(ai_snake.body)
            if input_queue:
                current_dir_x, current_dir_y = input_queue.pop(0)
            player_head = player_body[0]
            new_player_head = (player_head[0] + current_dir_x, player_head[1] + current_dir_y)
            new_ai_head = ai_snake.get_next_move(player_body, food_list, ai_flaw)

            player_dead = (new_player_head[0] < 0 or new_player_head[0] >= GRID_COLS or new_player_head[1] < 0 or new_player_head[1] >= GRID_ROWS or
                           new_player_head in player_body or new_player_head in ai_snake.body or new_player_head == new_ai_head)
            ai_dead = (new_ai_head[0] < 0 or new_ai_head[0] >= GRID_COLS or new_ai_head[1] < 0 or new_ai_head[1] >= GRID_ROWS or
                       new_ai_head in ai_snake.body or new_ai_head in player_body or new_player_head == new_ai_head)

            if player_dead or ai_dead:
                winner = WINNER_AI if player_dead else WINNER_PLAYER
                game_state = STATE_GAME_OVER
                ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)
            else:
                player_body.insert(0, new_player_head)
                if new_player_head in food_list:
                    player_score += 1
                    previous_player_body.append(previous_player_body[-1])
                    food_list.remove(new_player_head)
                else:
                    player_body.pop()
                ai_snake.body.insert(0, new_ai_head)
                if new_ai_head in food_list:
                    ai_score += 1
                    ai_snake.previous_body.append(ai_snake.previous_body[-1])
                    food_list.remove(new_ai_head)
                else:
                    ai_snake.body.pop()
                while len(food_list) < FOOD_COUNT:
                    food_list.append(get_random_food_position(set(player_body) | set(ai_snake.body) | set(food_list)))
                if player_score >= winning_score or ai_score >= winning_score:
                    winner = WINNER_PLAYER if player_score >= winning_score else WINNER_AI
                    game_state = STATE_GAME_OVER
                    ui_elements = setup_ui_for_state(game_state, ui_manager, screen.get_width(), screen.get_height(), player_name, current_difficulty, selected_diff_idx)

        ui_manager.update(time_delta)
        window_width, window_height = screen.get_size()
        tile_size, offset_x, offset_y, board_w, board_h = get_board_layout(window_width, window_height)

        if game_state == STATE_WELCOME:
            screen.fill(COLOR_BG_MENU)
            draw_clean_text(screen, font_xl, "Symbiosis Institute of Technology, Nagpur", COLOR_TEXT_MENU_ACCENT, (window_width // 2, window_height // 2 - 110))
            draw_clean_text(screen, font_medium, "Name: Nitin Sah  |  PRN: 26070521143  |  Section: C", COLOR_TEXT_MENU, (window_width // 2, window_height // 2 - 40))
            draw_clean_text(screen, font_small, "AI-Enhanced Snake Competition Edition  |  Press [F] Fullscreen", COLOR_TEXT_MENU_SUBTLE, (window_width // 2, window_height - 35))
        elif game_state == STATE_NAME_ENTRY:
            screen.fill(COLOR_BG_MENU)
            draw_clean_text(screen, font_large, "ENTER YOUR NAME", COLOR_TEXT_MENU_ACCENT, (window_width // 2, window_height // 2 - 95))
            draw_clean_text(screen, font_small, "Type your name and click continue (or press ENTER):", COLOR_TEXT_MENU, (window_width // 2, window_height // 2 - 40))
        elif game_state == STATE_DIFFICULTY_SELECT:
            screen.fill(COLOR_BG_MENU)
            draw_clean_text(screen, font_large, "SELECT DIFFICULTY", COLOR_TEXT_MENU_ACCENT, (window_width // 2, window_height // 2 - 180))
            selected_btn = ui_elements.get(["btn_easy", "btn_medium", "btn_hard"][selected_diff_idx])
            if selected_btn:
                pulse = (math.sin(pygame.time.get_ticks() * 0.006) + 1.0) * 0.5
                pad = int(3 + pulse * 6)
                rect = selected_btn.rect.inflate(pad * 2, pad * 2)
                glow_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
                pygame.draw.rect(glow_surf, (int(255 * pulse), int(255 * (1 - pulse)), int(255 * (0.55 + 0.45 * (1 - pulse))), 160), glow_surf.get_rect(), width=3, border_radius=14)
                screen.blit(glow_surf, rect.topleft)
            draw_clean_text(screen, font_small, "Use Mouse or WASD/Arrows to select  |  Click START GAME to enter", COLOR_TEXT_MENU_SUBTLE, (window_width // 2, window_height // 2 - 130))
        elif game_state in (STATE_PLAYING, STATE_GAME_OVER):
            screen.fill(COLOR_BG_PLAYING)
            draw_grid(screen, offset_x, offset_y, tile_size, board_w, board_h)
            progress = min(1.0, max(0.0, (now - last_move_time) / move_interval)) if game_state == STATE_PLAYING else 1.0
            padding = max(1, tile_size // 10)
            draw_size = max(1, tile_size - padding * 2)
            corner_radius = max(2, tile_size // 4)

            for fx, fy in food_list:
                draw_glowing_food(screen, fx, fy, offset_x, offset_y, tile_size)
            for index, curr_pos in enumerate(player_body):
                prev_pos = previous_player_body[min(index, len(previous_player_body) - 1)]
                lerp_gx = prev_pos[0] + (curr_pos[0] - prev_pos[0]) * progress
                lerp_gy = prev_pos[1] + (curr_pos[1] - prev_pos[1]) * progress
                color = COLOR_SNAKE_HEAD if index == 0 else COLOR_SNAKE_BODY
                draw_glowing_rect(screen, color, COLOR_SNAKE_GLOW, (offset_x + lerp_gx * tile_size + padding, offset_y + lerp_gy * tile_size + padding, draw_size, draw_size), border_radius=corner_radius)
            for index, curr_pos in enumerate(ai_snake.body):
                prev_pos = ai_snake.previous_body[min(index, len(ai_snake.previous_body) - 1)]
                lerp_gx = prev_pos[0] + (curr_pos[0] - prev_pos[0]) * progress
                lerp_gy = prev_pos[1] + (curr_pos[1] - prev_pos[1]) * progress
                color = COLOR_AI_HEAD if index == 0 else COLOR_AI_BODY
                draw_glowing_rect(screen, color, COLOR_AI_GLOW, (offset_x + lerp_gx * tile_size + padding, offset_y + lerp_gy * tile_size + padding, draw_size, draw_size), border_radius=corner_radius)

            draw_hud(screen, font_small, player_name, player_score, ai_score, current_difficulty, winning_score, offset_x, offset_y, board_w)
            if game_state == STATE_GAME_OVER:
                overlay = pygame.Surface((window_width, window_height))
                overlay.set_alpha(190)
                overlay.fill((10, 10, 15))
                screen.blit(overlay, (0, 0))
                draw_glowing_text(screen, font_large, f"{player_name.upper()} WINS!" if winner == WINNER_PLAYER else "AI WINS!", COLOR_VICTORY if winner == WINNER_PLAYER else COLOR_AI_HEAD, COLOR_TEXT_GLOW if winner == WINNER_PLAYER else COLOR_BORDER, (window_width // 2, window_height // 2 - 60))
                score_text = font_small.render(f"Final Score ->  {player_name}: {player_score} / {winning_score}   |   AI: {ai_score} / {winning_score}", True, COLOR_TEXT_HUD)
                screen.blit(score_text, score_text.get_rect(center=(window_width // 2, window_height // 2 + 10)))

        ui_manager.draw_ui(screen)
        pygame.display.flip()

if __name__ == "__main__":
    run_game()
