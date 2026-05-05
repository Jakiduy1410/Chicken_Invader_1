# FILE: settings.py - Cấu hình hệ thống game.


# --- CẤU HÌNH MÀN HÌNH ---
SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 700
TITLE         = "Chicken Invaders - Team Project"
FPS           = 60

# --- BẢNG MÀU (RGB) ---
COLOR_BLACK      = (0,   0,   0)
COLOR_WHITE      = (255, 255, 255)
COLOR_GREEN      = (0,   220, 80)
COLOR_RED        = (220, 50,  50)
COLOR_YELLOW     = (255, 220, 0)
COLOR_DARK_GREEN = (0,   150, 50)
COLOR_DARK_RED   = (150, 20,  20)
COLOR_ORANGE     = (255, 140, 0)
COLOR_PURPLE     = (128, 0, 128)
COLOR_PINK       = (255, 105, 180)
COLOR_BLUE       = (0, 150, 255)
COLOR_LIGHT_BLUE = (173, 216, 230)
COLOR_GREY       = (80,  80,  80)

# --- CẤU HÌNH PLAYER ---
PLAYER_WIDTH      = 50
PLAYER_HEIGHT     = 40
PLAYER_SCALE      = 1.5
PLAYER_SPEED      = 6
PLAYER_START_X    = SCREEN_WIDTH // 2
PLAYER_START_Y    = SCREEN_HEIGHT - 70

# --- CẤU HÌNH BULLET ---
BULLET_WIDTH  = 5
BULLET_HEIGHT = 14
BULLET_SPEED  = 10
BULLET_COOLDOWN = 300
RAPID_FIRE_COOLDOWN = 100
BULLET_DAMAGE = 1
BULLET_PIERCE_DAMAGE = 2

# --- CẤU HÌNH EGG ---
EGG_WIDTH  = 40
EGG_HEIGHT = 40
EGG_SPEED  = 3
EGG_DROP_COUNT = 3
EGG_DROP_CHANCE = 0.7

# --- CẤU HÌNH POWER-UP ---
POWERUP_WIDTH  = 30
POWERUP_HEIGHT = 30
POWERUP_SPEED  = 4
POWERUP_DROP_RATE = 0.15
POWERUP_DURATION_BOOST = 7000
POWERUP_DURATION_SHIELD = 10000

POWERUP_TYPES = {
    "pierce":      COLOR_RED,
    "triple_shot": COLOR_GREEN,
    "shield":      COLOR_YELLOW,
    "rapid_fire":  COLOR_PURPLE,
    "double_shot": COLOR_PINK,
    "cursed":      COLOR_GREY
}

# --- CẤU HÌNH ENEMY ---
ENEMY_WIDTH   = 80
ENEMY_HEIGHT  = 80
BOSS_WIDTH    = 100
BOSS_HEIGHT   = 100
BOSS_SCALE    = 2.5
ENEMY_SPEED_X = 1.5
ENEMY_DROP_Y  = 10

# 4 loại gà con theo máu + 1 boss
ENEMY_HP_BY_TYPE = {
    "chick_1": 1,
    "chick_2": 2,
    "chick_3": 3,
    "chick_4": 4,
    "boss": 200,
}

# --- ĐỘI HÌNH GÀ ---
ENEMY_ROWS      = 3
ENEMY_COLS      = 8
ENEMY_H_SPACING = 75
ENEMY_V_SPACING = 60
ENEMY_GRID_TOP  = 60

# --- CẤU HÌNH LEVEL / SÓNG (Wave) ---
SPEED_INCREMENT = 0.4  # Mức tăng tốc độ gà sau mỗi wave mới
MAX_WAVES       = 5    # Số wave tối đa trước khi game kết thúc (có thể mở rộng)

# --- CẤU HÌNH ĐIỂM SỐ ---
SCORE_PER_KILL = 100  # Điểm thưởng khi tiêu diệt 1 con gà