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
from settings import *


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

        # --- Tạo placeholder Surface hình tam giác (máy bay đơn giản) ---
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT), pygame.SRCALPHA)
        # Vẽ thân tàu: hình chữ nhật xanh lá
        pygame.draw.rect(self.image, COLOR_GREEN, (8, 15, PLAYER_WIDTH - 16, 22), border_radius=4)
        # Vẽ mũi tàu: tam giác nhọn
        pygame.draw.polygon(self.image, COLOR_GREEN, [
            (PLAYER_WIDTH // 2, 0),
            (10, 22),
            (PLAYER_WIDTH - 10, 22)
        ])
        # Vẽ viền ngoài cho dễ nhìn
        pygame.draw.polygon(self.image, COLOR_DARK_GREEN, [
            (PLAYER_WIDTH // 2, 0),
            (10, 22),
            (PLAYER_WIDTH - 10, 22)
        ], 2)
        # Vẽ buồng lái: hình tròn nhỏ ở giữa
        pygame.draw.circle(self.image, COLOR_WHITE, (PLAYER_WIDTH // 2, 18), 6)

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

    def __init__(self, x, y):
        """
        Khởi tạo một con gà tại vị trí lưới (x, y).

        Tham số:
            x (int): Tọa độ X tâm sprite trên màn hình.
            y (int): Tọa độ Y tâm sprite trên màn hình.
        """
        super().__init__()

        # --- Tạo placeholder hình con gà đơn giản ---
        self.image = pygame.Surface((ENEMY_WIDTH, ENEMY_HEIGHT), pygame.SRCALPHA)

        # Thân gà: hình elip đỏ
        pygame.draw.ellipse(self.image, COLOR_RED,
                            (2, 8, ENEMY_WIDTH - 4, ENEMY_HEIGHT - 10))
        # Đầu gà: hình tròn nhỏ hơn ở trên
        pygame.draw.circle(self.image, COLOR_RED,
                           (ENEMY_WIDTH // 2, 8), 10)
        # Mắt gà: chấm trắng nhỏ
        pygame.draw.circle(self.image, COLOR_WHITE,
                           (ENEMY_WIDTH // 2 - 3, 6), 3)
        pygame.draw.circle(self.image, COLOR_WHITE,
                           (ENEMY_WIDTH // 2 + 3, 6), 3)
        # Con ngươi: chấm đen
        pygame.draw.circle(self.image, COLOR_BLACK,
                           (ENEMY_WIDTH // 2 - 3, 6), 1)
        pygame.draw.circle(self.image, COLOR_BLACK,
                           (ENEMY_WIDTH // 2 + 3, 6), 1)
        # Mỏ gà: tam giác màu cam nhỏ
        pygame.draw.polygon(self.image, COLOR_ORANGE, [
            (ENEMY_WIDTH // 2, 12),
            (ENEMY_WIDTH // 2 - 4, 16),
            (ENEMY_WIDTH // 2 + 4, 16)
        ])
        # Viền ngoài thân
        pygame.draw.ellipse(self.image, COLOR_DARK_RED,
                            (2, 8, ENEMY_WIDTH - 4, ENEMY_HEIGHT - 10), 2)

        # --- Thiết lập vị trí ---
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery  = y

    def update(self):
        """
        Gọi mỗi frame.
        Hiện tại Enemy không tự cập nhật — chuyển động ngang/dọc do EnemyFleet
        trong game_logic.py điều khiển trực tiếp lên rect.
        Dev có thể thêm animation hoặc AI riêng tại đây sau này.
        """
        pass  # Placeholder — mở rộng sau


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
