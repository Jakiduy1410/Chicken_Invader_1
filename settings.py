# =============================================================================
# FILE: settings.py
# MÔ TẢ: Chứa toàn bộ hằng số cấu hình cho game Chicken Invaders.
#         Mọi thành viên trong team khi cần thay đổi thông số (tốc độ, màu sắc,
#         kích thước màn hình...) đều chỉ cần chỉnh sửa tại file này.
# NGƯỜI PHỤ TRÁCH: [Tên thành viên phụ trách cấu hình]
# =============================================================================

# --- CẤU HÌNH MÀN HÌNH ---
SCREEN_WIDTH  = 900   # Chiều rộng cửa sổ game (pixel)
SCREEN_HEIGHT = 700   # Chiều cao cửa sổ game (pixel)
TITLE         = "Chicken Invaders - Team Project"  # Tiêu đề cửa sổ
FPS           = 60    # Số khung hình mỗi giây (Frames Per Second)

# --- BẢNG MÀU (RGB) ---
# Sử dụng các hằng số màu thay vì hardcode để dễ thay đổi theme sau này
COLOR_BLACK      = (0,   0,   0)    # Màu nền
COLOR_WHITE      = (255, 255, 255)  # Màu chữ thông thường
COLOR_GREEN      = (0,   220, 80)   # Màu Player (máy bay)
COLOR_RED        = (220, 50,  50)   # Màu Enemy (gà)
COLOR_YELLOW     = (255, 220, 0)    # Màu Bullet (đạn)
COLOR_DARK_GREEN = (0,   150, 50)   # Màu viền Player
COLOR_DARK_RED   = (150, 20,  20)   # Màu viền Enemy
COLOR_ORANGE     = (255, 140, 0)    # Màu chữ Score / UI

# --- CẤU HÌNH PLAYER (Máy bay người chơi) ---
PLAYER_WIDTH      = 50    # Chiều rộng sprite Player (pixel)
PLAYER_HEIGHT     = 40    # Chiều cao sprite Player (pixel)
PLAYER_SPEED      = 6     # Tốc độ di chuyển ngang (pixel/frame)
PLAYER_START_X    = SCREEN_WIDTH // 2   # Vị trí X xuất phát (giữa màn hình)
PLAYER_START_Y    = SCREEN_HEIGHT - 70  # Vị trí Y xuất phát (gần đáy màn hình)

# --- CẤU HÌNH BULLET (Đạn) ---
BULLET_WIDTH  = 5     # Chiều rộng viên đạn (pixel)
BULLET_HEIGHT = 14    # Chiều cao viên đạn (pixel)
BULLET_SPEED  = 10    # Tốc độ đạn bay lên (pixel/frame, giá trị dương = đi lên)
BULLET_COOLDOWN = 300 # Thời gian hồi chiêu bắn (milliseconds) — tránh spam đạn

# --- CẤU HÌNH EGG (Trứng gà) ---
EGG_WIDTH  = 12     # Chiều rộng trứng (pixel)
EGG_HEIGHT = 12    # Chiều cao trứng (pixel)
EGG_SPEED  = 5     # Tốc độ trứng bay xuống (pixel/frame)
EGG_DROP_COUNT = 6 # Số lượng trứng thả mỗi lượt (khoảng 6 con)

# --- CẤU HÌNH ENEMY (Đàn gà) ---
ENEMY_WIDTH   = 80    # Chiều rộng sprite Enemy (pixel)
ENEMY_HEIGHT  = 80    # Chiều cao sprite Enemy (pixel)
BOSS_WIDTH    = 100   # Chiều rộng khung hình trong sheet
BOSS_HEIGHT   = 100   # Chiều cao khung hình trong sheet
BOSS_SCALE    = 2.5   # Hệ số phóng to Boss (Chỉnh cái này để Boss to lên)
ENEMY_SPEED_X = 1.5   # Tốc độ di chuyển ngang ban đầu (pixel/frame)
ENEMY_DROP_Y  = 20    # Khoảng cách hạ xuống khi chạm biên (pixel)

# 4 loại gà con theo máu + 1 boss
ENEMY_HP_BY_TYPE = {
    "chick_1": 1,
    "chick_2": 2,
    "chick_3": 3,
    "chick_4": 4,
    "boss": 20,
}

# --- CẤU HÌNH ĐỘI HÌNH GÀ (Grid Formation) ---
ENEMY_ROWS      = 3   # Số hàng gà
ENEMY_COLS      = 8   # Số cột gà
ENEMY_H_SPACING = 75  # Khoảng cách ngang giữa các con gà (pixel)
ENEMY_V_SPACING = 60  # Khoảng cách dọc giữa các con gà (pixel)
ENEMY_GRID_TOP  = 60  # Vị trí Y của hàng gà đầu tiên tính từ đỉnh màn hình

# --- CẤU HÌNH LEVEL / SÓNG (Wave) ---
SPEED_INCREMENT = 0.4  # Mức tăng tốc độ gà sau mỗi wave mới
MAX_WAVES       = 5    # Số wave tối đa trước khi game kết thúc (có thể mở rộng)

# --- CẤU HÌNH ĐIỂM SỐ ---
SCORE_PER_KILL = 100  # Điểm thưởng khi tiêu diệt 1 con gà