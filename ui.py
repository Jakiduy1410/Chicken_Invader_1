# =============================================================================
# FILE: ui.py
#
# MÔ TẢ:
#   Thiết kế và vẽ các màn hình (Menu, Leaderboard, Settings, HUD), căn chỉnh layout UI và dùng mock data cho Leaderboard.
# QUY TẮC:
#   - Không hardcode màu/font size → lấy từ settings.py
#   - Chỉ xử lý UI, không chứa logic game
# =============================================================================

import pygame
import settings
import random

# ================= FONT CONFIG =================
FONT_SMALL  = getattr(settings, "FONT_SMALL", 20)
FONT_MEDIUM = getattr(settings, "FONT_MEDIUM", 28)
FONT_LARGE  = getattr(settings, "FONT_LARGE", 44)

_font_cache = {}

def get_font(size):
    if size not in _font_cache:
        _font_cache[size] = pygame.font.SysFont("Courier New", size, bold=True)
    return _font_cache[size]

# ================= TEXT DRAW =================
def draw_text(surface, text, size, color, x, y, center=True):
    font = get_font(size)
    text_surface = font.render(text, True, color)
    rect = text_surface.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    surface.blit(text_surface, rect)

# ================= BUTTON =================
def draw_button(surface, text, rect, color_bg, color_text, is_locked=False):
    mouse_pos = pygame.mouse.get_pos()
    is_hovered = rect.collidepoint(mouse_pos) and not is_locked

    # ===== Hover scale =====
    display_rect = rect.inflate(6, 6) if is_hovered else rect

    # ===== Neon color =====
    neon_color = (0, 255, 255)
    if is_locked:
        neon_color = (100, 100, 100)
    elif text == "QUIT":
        neon_color = (255, 50, 50)

    # ===== Background color =====
    if is_locked:
        bg_color = (30, 30, 30)
    else:
        bg_color = (10, 20, 40) if not is_hovered else (20, 40, 80)

    x, y = display_rect.topleft
    w, h = display_rect.size

    v = 15

    points = [
        (x + v, y), (x + w - v, y),
        (x + w, y + v), (x + w, y + h - v),
        (x + w - v, y + h), (x + v, y + h),
        (x, y + h - v), (x, y + v)
    ]

    # ===== Background =====
    btn_surf = pygame.Surface((w, h), pygame.SRCALPHA).convert_alpha()

    pygame.draw.polygon(
        btn_surf,
        (*bg_color, 200),
        [(p[0] - x, p[1] - y) for p in points]
    )

    surface.blit(btn_surf, (x, y))

    # ===== Border =====
    pygame.draw.polygon(surface, neon_color, points, 2)

    # ===== Highlight corners =====
    highlight = (200, 255, 255) if text != "QUIT" else (255, 200, 200)

    pygame.draw.lines(surface, highlight, False,
        [(x + v + 15, y), (x + v, y), (x, y + v), (x, y + v + 15)], 3)

    pygame.draw.lines(surface, highlight, False,
        [(x + w - v - 15, y + h), (x + w - v, y + h),
         (x + w, y + h - v), (x + w, y + h - v - 15)], 3)

    # ===== Text (FIX FONT HARD CODE nếu muốn sau) =====
    display_text = text
    text_color = highlight
    if is_locked:
        display_text = f"LOCKED"
        text_color = (150, 150, 150)

    draw_text(
        surface,
        display_text,
        28,
        text_color,
        display_rect.centerx,
        display_rect.centery
    )
    
# ================= STAR BACKGROUND =================
class StarBackground:
    def __init__(self, count=50):
        self.stars = [{
            "x": random.randint(0, settings.SCREEN_WIDTH),
            "y": random.randint(0, settings.SCREEN_HEIGHT),
            "speed": random.uniform(0.5, 1.5)
        } for _ in range(count)]

    def update_and_draw(self, surface):
        for star in self.stars:
            star["y"] += star["speed"]

            if star["y"] > settings.SCREEN_HEIGHT:
                star["y"] = 0

            # ✅ dùng màu có sẵn
            pygame.draw.circle(surface, settings.COLOR_WHITE,
                               (int(star["x"]), int(star["y"])), 1)

# ================= MAIN MENU =================
class MainMenuScreen:
    def __init__(self):
        self.stars = StarBackground()

        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2

        self.buttons = {
            "play": pygame.Rect(cx - 120, cy - 80, 240, 60),
            "leaderboard": pygame.Rect(cx - 120, cy + 10, 240, 60),
            "settings": pygame.Rect(cx - 120, cy + 100, 240, 60),
            "quit": pygame.Rect(cx - 120, cy + 190, 240, 60),
        }

    def draw(self, surface):
        surface.fill(settings.COLOR_BLACK)
        self.stars.update_and_draw(surface)

        draw_text(surface, settings.TITLE, FONT_LARGE,
                  settings.COLOR_ORANGE,
                  settings.SCREEN_WIDTH // 2, 120)

        draw_button(surface, "PLAY", self.buttons["play"], settings.COLOR_GREEN, settings.COLOR_BLACK)
        draw_button(surface, "LEADERBOARD", self.buttons["leaderboard"], settings.COLOR_YELLOW, settings.COLOR_BLACK)
        draw_button(surface, "SETTINGS", self.buttons["settings"], settings.COLOR_WHITE, settings.COLOR_BLACK)
        draw_button(surface, "QUIT", self.buttons["quit"], settings.COLOR_RED, settings.COLOR_WHITE)

# ================= LEADERBOARD =================
class LeaderboardScreen:
    def __init__(self):
        self.stars = StarBackground(40)
        self.back_button = pygame.Rect(20, 20, 110, 45)

    def draw(self, surface, scores=None):
        if scores is None:
            scores = []

        surface.fill(settings.COLOR_BLACK)
        self.stars.update_and_draw(surface)

        draw_text(surface, "LEADERBOARD", FONT_LARGE,
                  settings.COLOR_ORANGE,
                  settings.SCREEN_WIDTH // 2, 100)

        draw_button(surface, "BACK", self.back_button,
                    settings.COLOR_RED, settings.COLOR_WHITE)

        start_y = 150
        row_gap = 45

        col_rank = settings.SCREEN_WIDTH * 0.25
        col_name = settings.SCREEN_WIDTH * 0.45
        col_score = settings.SCREEN_WIDTH * 0.68

        draw_text(surface, "RANK", FONT_MEDIUM, settings.COLOR_WHITE, col_rank, start_y)
        draw_text(surface, "NAME", FONT_MEDIUM, settings.COLOR_WHITE, col_name, start_y)
        draw_text(surface, "SCORE", FONT_MEDIUM, settings.COLOR_WHITE, col_score, start_y)

        pygame.draw.line(surface, settings.COLOR_WHITE,
                         (col_rank - 40, start_y + 30),
                         (col_score + 60, start_y + 30), 2)

        for i, (name, score) in enumerate(scores[:10]):
            y = start_y + 85 + (i * row_gap)

            if i == 0:
                color = settings.COLOR_YELLOW   # fake gold
            elif i == 1:
                color = settings.COLOR_WHITE    # fake silver
            elif i == 2:
                color = settings.COLOR_ORANGE   # fake bronze
            else:
                color = settings.COLOR_WHITE

            # Handle various score types (int, string, special symbols)
            if isinstance(score, int):
                score_display = f"{score:,}"
            else:
                score_display = str(score)

            if name == "Bombombuzin":
                score_display = "∞"

            draw_text(surface, f"#{i+1}", FONT_MEDIUM - 5, color, col_rank, y)
            draw_text(surface, str(name), FONT_MEDIUM - 5, settings.COLOR_WHITE, col_name, y)
            draw_text(surface, score_display, FONT_MEDIUM - 5,
                      settings.COLOR_GREEN, col_score, y)

# ================= MODE SELECT =================
class PlayModeScreen:
    def __init__(self):
        # nền sao (giống menu cho đồng bộ)
        self.stars = StarBackground(40)

        cx = settings.SCREEN_WIDTH // 2
        cy = settings.SCREEN_HEIGHT // 2

        self.buttons = {
            "story": pygame.Rect(cx - 120, cy - 40, 240, 60),
            "infinite": pygame.Rect(cx - 120, cy + 50, 240, 60),
            "back": pygame.Rect(20, 20, 110, 45),
        }

    def draw(self, surface, is_unlocked=False):
        # nền + hiệu ứng sao
        surface.fill(settings.COLOR_BLACK)
        self.stars.update_and_draw(surface)

        # title
        draw_text(
            surface,
            "CHOOSE MODE",
            FONT_LARGE,
            settings.COLOR_ORANGE,
            settings.SCREEN_WIDTH // 2,
            120
        )

        # buttons
        draw_button(
            surface,
            "STORY MODE",
            self.buttons["story"],
            settings.COLOR_GREEN,
            settings.COLOR_BLACK
        )

        draw_button(
            surface,
            "INFINITE MODE",
            self.buttons["infinite"],
            settings.COLOR_YELLOW,
            settings.COLOR_BLACK,
            is_locked=not is_unlocked
        )

        draw_button(
            surface,
            "BACK",
            self.buttons["back"],
            settings.COLOR_RED,
            settings.COLOR_WHITE
        )
        
# ================= SETTINGS =================
class SettingsScreen:
    def __init__(self):
        self.stars = StarBackground(30)
        self.back_button = pygame.Rect(20, 20, 110, 45)
        
        cx = settings.SCREEN_WIDTH // 2
        self.buttons = {
            "sfx": pygame.Rect(cx - 150, 200, 300, 55),
            "music": pygame.Rect(cx - 150, 270, 300, 55),
            "difficulty": pygame.Rect(cx - 150, 340, 300, 55),
            "screen": pygame.Rect(cx - 150, 410, 300, 55),
        }

    def draw(self, surface, sfx_on=True, music_on=True, difficulty="NORMAL", screen_mode="WINDOWED"):
        surface.fill(settings.COLOR_BLACK)
        self.stars.update_and_draw(surface)

        draw_text(surface, "SETTINGS", FONT_LARGE,
                  settings.COLOR_ORANGE,
                  settings.SCREEN_WIDTH // 2, 80)

        draw_button(surface, "BACK", self.back_button,
                    settings.COLOR_RED, settings.COLOR_WHITE)

        # Buttons for SFX, Music, Difficulty, Screen Mode
        sfx_text = f"SFX: {'ON' if sfx_on else 'OFF'}"
        music_text = f"MUSIC: {'ON' if music_on else 'OFF'}"
        diff_text = f"DIFF: {difficulty}"
        mode_text = f"MODE: {screen_mode}"

        draw_button(surface, sfx_text, self.buttons["sfx"], 
                    settings.COLOR_BLUE if sfx_on else settings.COLOR_GREY, 
                    settings.COLOR_WHITE)
        
        draw_button(surface, music_text, self.buttons["music"], 
                    settings.COLOR_BLUE if music_on else settings.COLOR_GREY, 
                    settings.COLOR_WHITE)

        draw_button(surface, diff_text, self.buttons["difficulty"], 
                    (100, 50, 150), settings.COLOR_WHITE)

        draw_button(surface, mode_text, self.buttons["screen"], 
                    (50, 150, 150), settings.COLOR_WHITE)

# ================= HUD =================
class HUD:
    def draw(self, surface, score, lives, wave):
        draw_text(surface, f"SCORE: {score}", FONT_SMALL,
                  settings.COLOR_ORANGE, 20, 20, False)
        draw_text(surface, f"LIVES: {lives}", FONT_SMALL,
                  settings.COLOR_GREEN, 20, 50, False)
        draw_text(surface, f"WAVE: {wave}", FONT_SMALL,
                  settings.COLOR_WHITE, 20, 80, False)