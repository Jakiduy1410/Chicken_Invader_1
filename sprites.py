# =============================================================================
# FILE: sprites.py
# MÔ TẢ: Định nghĩa các Sprite (đối tượng đồ họa) của game.
#         Mỗi class kế thừa từ pygame.sprite.Sprite để tận dụng hệ thống
#         Group & Collision detection tích hợp sẵn của Pygame.
#
# PHÂN CÔNG TEAM:
#   - Class Player  → Dev phụ trách nhân vật người chơi
#   - Class Enemy   → Dev phụ trách AI & đội hình gà
#   - Class Bullet  → Dev phụ trách hệ thống đạn & hiệu ứng
# =============================================================================

import pygame
from pathlib import Path
from settings import *

ASSETS_IMAGES_DIR = Path(__file__).resolve().parent / "assets" / "image"


def _load_sprite_sheet_frames(sheet_name, frame_width, frame_height, frame_count, row=0, scale=1.0):
    """
    Cắt frame từ sprite sheet theo hàng và có thể phóng to/thu nhỏ.
    """
    sheet_path = ASSETS_IMAGES_DIR / sheet_name
    if not sheet_path.exists():
        return []

    try:
        sheet = pygame.image.load(str(sheet_path)).convert_alpha()
    except pygame.error:
        return []

    frames = []
    for i in range(frame_count):
        # Tạo surface gốc cho 1 frame
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (i * frame_width, row * frame_height, frame_width, frame_height))
        
        # Nếu có scale, phóng to frame này lên
        if scale != 1.0:
            new_w = int(frame_width * scale)
            new_h = int(frame_height * scale)
            frame = pygame.transform.scale(frame, (new_w, new_h))
            
        frames.append(frame)
    return frames


def _build_player_fallback_frames():
    """
    Tạo 3 frame máy bay giả lập hiệu ứng xịt lửa.
    """
    flame_lengths = [8, 14, 10]
    frames = []
    for flame_len in flame_lengths:
        frame = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(frame, COLOR_GREEN, (8, 15, PLAYER_WIDTH - 16, 22), border_radius=4)
        pygame.draw.polygon(frame, COLOR_GREEN, [
            (PLAYER_WIDTH // 2, 0),
            (10, 22),
            (PLAYER_WIDTH - 10, 22)
        ])
        pygame.draw.polygon(frame, COLOR_DARK_GREEN, [
            (PLAYER_WIDTH // 2, 0),
            (10, 22),
            (PLAYER_WIDTH - 10, 22)
        ], 2)
        pygame.draw.circle(frame, COLOR_WHITE, (PLAYER_WIDTH // 2, 18), 6)
        # Flame động ở phía đuôi: chỉ đổi phần hiển thị, không ảnh hưởng rect.
        pygame.draw.polygon(frame, COLOR_ORANGE, [
            (PLAYER_WIDTH // 2 - 6, PLAYER_HEIGHT - 2),
            (PLAYER_WIDTH // 2 + 6, PLAYER_HEIGHT - 2),
            (PLAYER_WIDTH // 2, PLAYER_HEIGHT + flame_len - 2)
        ])
        frames.append(frame)
    return frames


def _build_enemy_fallback_frames(enemy_type="chick_1", width=ENEMY_WIDTH, height=ENEMY_HEIGHT):
    """
    Tạo 3 frame gà giả lập hiệu ứng vỗ cánh.
    """
    body_color_map = {
        "chick_1": (220, 200, 40),
        "chick_2": (255, 160, 40),
        "chick_3": (220, 70, 60),
        "chick_4": (170, 50, 140),
        "boss": (120, 120, 255),
    }
    border_color_map = {
        "chick_1": (160, 140, 20),
        "chick_2": (170, 90, 20),
        "chick_3": (130, 30, 30),
        "chick_4": (110, 25, 90),
        "boss": (60, 60, 200),
    }
    body_color = body_color_map.get(enemy_type, COLOR_RED)
    border_color = border_color_map.get(enemy_type, COLOR_DARK_RED)

    wing_offsets = [0, -3, 2]
    frames = []
    for wing_offset in wing_offsets:
        frame = pygame.Surface((width, height), pygame.SRCALPHA)

        pygame.draw.ellipse(frame, body_color,
                            (2, 8, width - 4, height - 10))
        pygame.draw.circle(frame, body_color,
                           (width // 2, 8), 10)
        pygame.draw.circle(frame, COLOR_WHITE,
                           (width // 2 - 3, 6), 3)
        pygame.draw.circle(frame, COLOR_WHITE,
                           (width // 2 + 3, 6), 3)
        pygame.draw.circle(frame, COLOR_BLACK,
                           (width // 2 - 3, 6), 1)
        pygame.draw.circle(frame, COLOR_BLACK,
                           (width // 2 + 3, 6), 1)
        pygame.draw.polygon(frame, COLOR_ORANGE, [
            (width // 2, 12),
            (width // 2 - 4, 16),
            (width // 2 + 4, 16)
        ])
        pygame.draw.ellipse(frame, border_color,
                            (2, 8, width - 4, height - 10), 2)

        # 2 cánh vỗ lên/xuống theo frame.
        pygame.draw.ellipse(
            frame, border_color,
            (0, 16 + wing_offset, 10, 12)
        )
        pygame.draw.ellipse(
            frame, border_color,
            (width - 10, 16 + wing_offset, 10, 12)
        )
        frames.append(frame)
    return frames


# =============================================================================
# CLASS: Player
# MÔ TẢ: Đại diện cho máy bay của người chơi.
#         Xử lý: di chuyển ngang, bắn đạn, giới hạn biên màn hình.
# =============================================================================
class Player(pygame.sprite.Sprite):

    def __init__(self):
        """
        Khởi tạo Player.
        - Tạo placeholder hình học đơn giản thay cho ảnh thật.
        - Đặt vị trí xuất phát ở giữa-đáy màn hình.
        - Thiết lập biến cooldown để giới hạn tốc độ bắn.
        """
        super().__init__()

        # Ưu tiên sprite sheet; nếu chưa có asset thì fallback về frame vẽ tay.
        self.frames = _load_sprite_sheet_frames(
            sheet_name="player_sheet.png",
            frame_width=PLAYER_WIDTH,
            frame_height=PLAYER_HEIGHT,
            frame_count=3,
            row=0,
            scale=PLAYER_SCALE
        )
        if not self.frames:
            # Fallback nếu không có ảnh: vẽ bằng code và scale lên
            self.frames = _build_player_fallback_frames()
            if PLAYER_SCALE != 1.0:
                new_w = int(PLAYER_WIDTH * PLAYER_SCALE)
                new_h = int(PLAYER_HEIGHT * PLAYER_SCALE)
                self.frames = [pygame.transform.scale(f, (new_w, new_h)) for f in self.frames]
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.animation_interval = 90  # ms/frame
        self.last_frame_update = pygame.time.get_ticks()

        # --- Thiết lập vị trí ban đầu ---
        self.rect = self.image.get_rect()
        self.rect.centerx = PLAYER_START_X
        self.rect.bottom  = PLAYER_START_Y

        # --- Biến cooldown: tránh người chơi spam đạn liên tục ---
        # Lưu thời điểm lần bắn gần nhất (milliseconds)
        self._last_shot_time = 0

    def update(self):
        """
        Gọi mỗi frame. Xử lý:
        1. Đọc phím bấm để di chuyển trái/phải.
        2. Giới hạn Player không vượt ra ngoài biên màn hình.
        (Bắn đạn được xử lý riêng qua handle_shoot() để tách biệt logic)
        """
        keys = pygame.key.get_pressed()

        # Di chuyển sang TRÁI khi nhấn phím mũi tên trái
        if keys[pygame.K_LEFT]:
            self.rect.x -= PLAYER_SPEED

        # Di chuyển sang PHẢI khi nhấn phím mũi tên phải
        if keys[pygame.K_RIGHT]:
            self.rect.x += PLAYER_SPEED

        # --- Giới hạn biên màn hình ---
        # Không cho Player đi ra ngoài cạnh trái
        if self.rect.left < 0:
            self.rect.left = 0
        # Không cho Player đi ra ngoài cạnh phải
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

        # Chỉ đổi frame hiển thị bằng self.image, không đụng rect/di chuyển.
        now = pygame.time.get_ticks()
        if now - self.last_frame_update >= self.animation_interval:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def apply_powerup(self, p_type):
        """
        Kích hoạt hiệu ứng của vật phẩm tăng sức mạnh.
        """
        now = pygame.time.get_ticks()
        duration = POWERUP_DURATION

        if p_type == "pierce":
            self.pierce_expire_time = now + duration
        elif p_type == "triple_shot":
            self.triple_shot_expire_time = now + duration
            # Xung đột: triple_shot ghi đè double_shot (tuỳ chọn thiết kế)
            self.double_shot_expire_time = 0
        elif p_type == "double_shot":
            self.double_shot_expire_time = now + duration
            # Xung đột: double_shot ghi đè triple_shot
            self.triple_shot_expire_time = 0
        elif p_type == "rapid_fire":
            self.rapid_fire_expire_time = now + duration
        elif p_type == "shield":
            self.shield_expire_time = now + duration
            self.has_shield = True
        elif p_type == "cursed":
            # Bùa hại: không bắn được trong 3 giây
            self.cursed_expire_time = now + 3000

    def handle_shoot(self, all_sprites, bullets_group):
        """
        Kiểm tra phím Space và tạo viên đạn mới nếu cooldown đã hết.

        Tham số:
            all_sprites  (pygame.sprite.Group): Group chứa TẤT CẢ sprite — để render.
            bullets_group (pygame.sprite.Group): Group riêng cho đạn — để detect collision.

        Trả về: None
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE]:
            now = pygame.time.get_ticks()  # Thời gian hiện tại (ms)

            # Chỉ bắn nếu đã qua thời gian cooldown
            if now - self._last_shot_time > BULLET_COOLDOWN:
                self._last_shot_time = now  # Cập nhật thời điểm bắn

                # Tạo viên đạn tại vị trí trung tâm phía trên Player
                bullet = Bullet(self.rect.centerx, self.rect.top)

                # Thêm vào cả hai group để render và kiểm tra va chạm
                all_sprites.add(bullet)
                bullets_group.add(bullet)


# =============================================================================
# CLASS: Enemy
# MÔ TẢ: Đại diện cho một con gà trong đội hình.
#         Không tự di chuyển — chuyển động được điều phối bởi EnemyFleet trong
#         game_logic.py để toàn đội hình di chuyển đồng bộ.
# =============================================================================
class Enemy(pygame.sprite.Sprite):

    def __init__(self, x, y, enemy_type="chick_1", hp=1):
        """
        Khởi tạo một con gà tại vị trí lưới (x, y).

        Tham số:
            x (int): Tọa độ X tâm sprite trên màn hình.
            y (int): Tọa độ Y tâm sprite trên màn hình.
        """
        super().__init__()
        self.enemy_type = enemy_type
        self.max_hp = hp
        self.hp = hp

        # Xác định kích thước và scale dựa trên loại enemy
        w = BOSS_WIDTH if enemy_type == "boss" else ENEMY_WIDTH
        h = BOSS_HEIGHT if enemy_type == "boss" else ENEMY_HEIGHT
        scale = BOSS_SCALE if enemy_type == "boss" else 1.0

        self.frames = _load_sprite_sheet_frames(
            sheet_name=f"{enemy_type}_sheet.png",
            frame_width=w,
            frame_height=h,
            frame_count=3,
            row=0,
            scale=scale
        ) or _build_enemy_fallback_frames(
            enemy_type=enemy_type, 
            width=int(w * scale), 
            height=int(h * scale)
        )
        import random
        self.frame_index = random.randint(0, len(self.frames) - 1)
        self.image = self.frames[self.frame_index]
        self.animation_interval = 100 if enemy_type == "boss" else 140  # ms/frame
        self.last_frame_update = pygame.time.get_ticks()

        # --- Thiết lập vị trí ---
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
        self.target_y = y  # Lưu tọa độ Y mục tiêu (để làm hiệu ứng bay xuống)

    def update(self):
        """
        Gọi mỗi frame.
        - Xử lý animation frame.
        """
        now = pygame.time.get_ticks()
        if now - self.last_frame_update >= self.animation_interval:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def take_damage(self, amount=1):
        """
        Giảm máu Enemy.
        Trả về True nếu Enemy đã chết.
        """
        self.hp -= amount
        if self.hp <= 0:
            self.kill()
            return True
        return False


# =============================================================================
# CLASS: Bullet
# MÔ TẢ: Đại diện cho một viên đạn do Player bắn ra.
#         Tự động bay lên và tự xóa khi ra khỏi màn hình (tối ưu RAM).
# =============================================================================
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y):
        """
        Khởi tạo viên đạn tại vị trí (x, y) — thường là đầu nòng súng Player.

        Tham số:
            x (int): Tọa độ X tâm viên đạn.
            y (int): Tọa độ Y đỉnh viên đạn (đặt tại mũi máy bay).
        """
        super().__init__()

        # --- Tạo placeholder hình viên đạn: hình chữ nhật màu vàng ---
        self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA)
        # Thân đạn
        pygame.draw.rect(self.image, COLOR_YELLOW,
                         (0, 0, BULLET_WIDTH, BULLET_HEIGHT), border_radius=2)
        # Hiệu ứng sáng: dải trắng mỏng ở giữa
        pygame.draw.rect(self.image, COLOR_WHITE,
                         (BULLET_WIDTH // 2 - 1, 1, 1, BULLET_HEIGHT - 4))

        # --- Thiết lập vị trí: đặt viên đạn tại miệng nòng súng ---
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom  = y  # Đáy đạn = đỉnh Player (đạn bay lên)

    def update(self):
        """
        Gọi mỗi frame.
        - Di chuyển đạn lên phía trên màn hình.
        - Tự động xóa khỏi game khi vượt qua cạnh trên (tối ưu bộ nhớ RAM).
        """
        # Bay lên: giảm tọa độ Y (trục Y trong Pygame tăng từ trên xuống dưới)
        self.rect.y -= BULLET_SPEED

        # --- Xóa đạn khỏi tất cả Group khi ra khỏi màn hình ---
        # kill() tự động remove khỏi mọi Group mà Sprite đang thuộc về
        if self.rect.bottom < 0:
            self.kill()  # Giải phóng bộ nhớ — QUAN TRỌNG để tránh memory leak


# =============================================================================
# CLASS: Egg
# MÔ TẢ: Đại diện cho một quả trứng do Enemy thả ra.
#         Tự động bay xuống và tự xóa khi ra khỏi màn hình.
# =============================================================================
class Egg(pygame.sprite.Sprite):

    def __init__(self, x, y):
        """
        Khởi tạo quả trứng tại vị trí (x, y) — thường là dưới chân Enemy.

        Tham số:
            x (int): Tọa độ X tâm quả trứng.
            y (int): Tọa độ Y đỉnh quả trứng (đặt tại chân gà).
        """
        super().__init__()

        # --- Tạo placeholder hình quả trứng: hình elip màu trắng ---
        self.image = pygame.Surface((EGG_WIDTH, EGG_HEIGHT), pygame.SRCALPHA)
        # Thân trứng: elip trắng
        pygame.draw.ellipse(self.image, COLOR_WHITE,
                            (0, 0, EGG_WIDTH, EGG_HEIGHT))
        # Viền ngoài: elip xám nhạt
        pygame.draw.ellipse(self.image, (200, 200, 200),
                            (0, 0, EGG_WIDTH, EGG_HEIGHT), 1)

        # --- Thiết lập vị trí: đặt trứng tại chân gà ---
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top     = y  # Đỉnh trứng = đáy Enemy (trứng bay xuống)

    def update(self):
        """
        Gọi mỗi frame.
        - Di chuyển trứng xuống phía dưới màn hình.
        - Tự động xóa khỏi game khi vượt qua cạnh dưới.
        """
        # Bay xuống: tăng tọa độ Y
        self.rect.y += EGG_SPEED

        # --- Xóa trứng khỏi tất cả Group khi ra khỏi màn hình ---
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()