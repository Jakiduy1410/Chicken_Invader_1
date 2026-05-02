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
import math
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
        
        # Pre-calculate masks for each frame to enable pixel-perfect collision
        self.masks = [pygame.mask.from_surface(f) for f in self.frames]
        self.mask = self.masks[self.frame_index]

        # --- Thiết lập vị trí ban đầu ---
        self.rect = self.image.get_rect()
        self.rect.centerx = PLAYER_START_X
        self.rect.bottom  = PLAYER_START_Y

        # --- Biến cooldown: tránh người chơi spam đạn liên tục ---
        # Lưu thời điểm lần bắn gần nhất (milliseconds)
        self._last_shot_time = 0 

        # --- Trạng thái Power-up ---
        self.pierce_expire_time = 0
        self.triple_shot_expire_time = 0
        self.double_shot_expire_time = 0
        self.rapid_fire_expire_time = 0
        self.shield_expire_time = 0
        self.cursed_expire_time = 0 # Thời gian kẹt súng
        self.has_shield = False # Chỉ dùng để quyết định có vẽ hiệu ứng khiên hay không
        
        # Load shield frames (3 frames as requested)
        self.shield_frames = _load_sprite_sheet_frames(
            sheet_name="shield_player.png",
            frame_width=PLAYER_WIDTH,
            frame_height=PLAYER_HEIGHT,
            frame_count=3,
            row=0,
            scale=PLAYER_SCALE
        )
        self.shield_frame_index = 0
        self.shield_animation_interval = 100 # ms/frame
        self.last_shield_update = pygame.time.get_ticks()

        self.base_image = self.image.copy()  # Lưu ảnh gốc để vẽ đè hiệu ứng


    def update(self):
        """
        Gọi mỗi frame. Xử lý:
        1. Đọc phím bấm để di chuyển trái/phải, lên/xuống.
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

        # Di chuyển LÊN / XUỐNG
        if keys[pygame.K_UP]:
            self.rect.y -= PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            self.rect.y += PLAYER_SPEED

        # --- Giới hạn biên màn hình ---
        # Không cho Player đi ra ngoài cạnh trái
        if self.rect.left < 0:
            self.rect.left = 0
        # Không cho Player đi ra ngoài cạnh phải
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Chỉ chặn biên màn hình, không chặn vùng di chuyển
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT

        # --- Xử lý thời gian hiệu lực của PowerUp (ví dụ: 10 giây) ---
        now = pygame.time.get_ticks()
        # Cập nhật trạng thái `has_shield` dựa trên bộ đếm giờ
        if now > self.shield_expire_time:
            self.has_shield = False
            
        # Khôi phục ảnh gốc
        self.image = self.base_image.copy()
        
        # Hiệu ứng nhấp nháy khi bất tử
        if self.has_shield: # Nhấp nháy khi có khiên
            if (now // 150) % 2 == 0:
                self.image.set_alpha(100)
                
        # Vẽ hiệu ứng khiên bảo vệ
        if self.has_shield and self.shield_frames:
            # Animation cho khiên
            if now - self.last_shield_update >= self.shield_animation_interval:
                self.last_shield_update = now
                self.shield_frame_index = (self.shield_frame_index + 1) % len(self.shield_frames)
            
            # Blit shield frame lên ảnh player
            shield_img = self.shield_frames[self.shield_frame_index]
            self.image.blit(shield_img, (0, 0))


        # Chỉ đổi frame hiển thị bằng self.image, không đụng rect/di chuyển.
        now = pygame.time.get_ticks()
        if now - self.last_frame_update >= self.animation_interval:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]
            self.mask = self.masks[self.frame_index]

    def apply_powerup(self, p_type):
        """
        Kích hoạt hiệu ứng của vật phẩm tăng sức mạnh.
        """
        now = pygame.time.get_ticks()
        duration = POWERUP_DURATION_BOOST

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
            duration_shield = POWERUP_DURATION_SHIELD
            self.shield_expire_time = now + duration_shield
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
        # Ghi chú: Trạng thái bảo vệ (bất tử/khiên) không ảnh hưởng đến khả năng bắn của Player.
        # Nếu gặp lỗi không bắn được, vui lòng kiểm tra lại input hoặc các logic khác.
        keys = pygame.key.get_pressed()

        now = pygame.time.get_ticks()
        if now < self.cursed_expire_time:
            return  # Đang bị bùa hại kẹt súng, không thể bắn

        if keys[pygame.K_SPACE]:
            # Xác định cooldown hiện tại (bắn nhanh hay thường)
            cooldown = RAPID_FIRE_COOLDOWN if now < self.rapid_fire_expire_time else BULLET_COOLDOWN

            # Chỉ bắn nếu đã qua thời gian cooldown
            if now - self._last_shot_time > cooldown:
                self._last_shot_time = now  # Cập nhật thời điểm bắn

                # Kiểm tra các buff đang kích hoạt
                is_pierce = now < self.pierce_expire_time
                has_triple = now < self.triple_shot_expire_time
                has_double = now < self.double_shot_expire_time
                
                b_type = "pierce" if is_pierce else "normal"
                
                # Tạo danh sách đạn sẽ bắn
                bullets_to_spawn = []
                
                if has_triple:
                    bullets_to_spawn.extend([
                        Bullet(self.rect.centerx, self.rect.top, bullet_type=b_type),
                        Bullet(self.rect.centerx, self.rect.top, speed_x=-3, bullet_type=b_type),
                        Bullet(self.rect.centerx, self.rect.top, speed_x=3, bullet_type=b_type)
                    ])
                if has_double:
                    bullets_to_spawn.extend([
                        Bullet(self.rect.centerx - 10, self.rect.top, bullet_type=b_type),
                        Bullet(self.rect.centerx + 10, self.rect.top, bullet_type=b_type)
                    ])
                if not has_triple and not has_double:
                    bullets_to_spawn.append(Bullet(self.rect.centerx, self.rect.top, bullet_type=b_type))
                    
                for b in bullets_to_spawn:
                    all_sprites.add(b)
                    bullets_group.add(b)


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

        # --- Logic tấn công cho Boss ---
        if enemy_type == "boss":
            self.state = "normal"
            self.attack_timer = pygame.time.get_ticks()
            self.attack_cooldown = 4000  # 4 giây bắn 1 lần
            self.charge_duration = 1000  # 1 giây tụ lực
            self.telegraph_duration = 800 # 0.8 giây cảnh báo (Step 1)
            self.fire_duration = 1500    # 1.5 giây bắn chưởng (Step 2)

            
            # Load hiệu ứng (27.png: tụ lực)
            self.normal_frames = self.frames # Lưu lại animation gốc
            self.charging_effect_frames = _load_sprite_sheet_frames("27.png", 40, 40, 3, scale=BOSS_SCALE)
            self.firing_effect_frames = [] # Đã dùng step 2.png trong lớp Laser
            self.effect_frame_index = 0
            self.last_effect_update = pygame.time.get_ticks()
            
            self.laser = None





    def update(self, all_sprites=None, lasers_group=None):
        """
        Gọi mỗi frame.
        - Xử lý animation frame.
        - Xử lý logic tấn công nếu là Boss.
        """
        now = pygame.time.get_ticks()
        
        if self.enemy_type == "boss":
            self._update_boss_logic(now, all_sprites, lasers_group)
        
        if now - self.last_frame_update >= self.animation_interval:
            self.last_frame_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index].copy()
            
            # Nếu đang tấn công, vẽ thêm hiệu ứng đè lên boss
            if self.enemy_type == "boss" and self.state in ["charging", "firing"]:
                self._draw_attack_effect(now)


    def _update_boss_logic(self, now, all_sprites, lasers_group):
        """Logic trạng thái của Boss: Normal -> Charging -> Firing"""
        if self.state == "normal":
            if now - self.attack_timer > self.attack_cooldown:
                self.state = "charging"
                self.attack_timer = now
                self.effect_frame_index = 0
        
        elif self.state == "charging":
            if now - self.attack_timer > self.charge_duration:
                self.state = "telegraphing"
                self.attack_timer = now
                # Tạo Laser Step 1 (Cảnh báo)
                if all_sprites is not None and lasers_group is not None:
                    self.laser = Laser(self)
                    self.laser.set_step(1)
                    all_sprites.add(self.laser)
                    lasers_group.add(self.laser)
        
        elif self.state == "telegraphing":
            if now - self.attack_timer > self.telegraph_duration:
                self.state = "firing"
                self.attack_timer = now
                self.effect_frame_index = 0
                # Chuyển Laser sang Step 2 (Bắn thật)

                if self.laser:
                    self.laser.set_step(2)
        
        elif self.state == "firing":
            if now - self.attack_timer > self.fire_duration:
                self.state = "normal"
                self.attack_timer = now
                if self.laser:

                    self.laser.kill()
                    self.laser = None


    def _draw_attack_effect(self, now):
        """
        (Private) Vẽ hiệu ứng tụ lực/bắn chưởng đè lên boss.
        Vị trí: Ở phía dưới (đít) của con boss.
        """
        effect_frames = []
        if self.state == "charging":
            effect_frames = self.charging_effect_frames
        elif self.state == "firing":
            effect_frames = self.firing_effect_frames
            
        if not effect_frames:
            return

        # Cập nhật animation hiệu ứng
        if now - self.last_effect_update > 100:
            self.last_effect_update = now
            self.effect_frame_index = (self.effect_frame_index + 1) % len(effect_frames)
        
        # Blit hiệu ứng vào phía dưới của con boss
        eff_img = effect_frames[self.effect_frame_index]
        # Căn giữa ngang (cộng thêm offset 10px sang phải cho cân)
        pos_x = (self.image.get_width() - eff_img.get_width()) // 2 + 10
        pos_y = self.image.get_height() - eff_img.get_height() - 10
        self.image.blit(eff_img, (pos_x, pos_y))





    def take_damage(self, amount=1):
        """
        Giảm máu Enemy.
        Trả về True nếu Enemy đã chết.
        """
        self.hp -= amount
        if self.hp <= 0:
            if self.enemy_type == "boss" and self.laser:
                self.laser.kill()
            self.kill()
            return True
        return False


# =============================================================================
# CLASS: Laser
# MÔ TẢ: Tia laze do Boss bắn ra, gây sát thương cho Player.
# =============================================================================
class Laser(pygame.sprite.Sprite):
    def __init__(self, owner):
        super().__init__()
        self.owner = owner

        self.width = 100
        self.height = SCREEN_HEIGHT
        
        # Load ảnh laser từ assets
        self.image_step1 = None
        self.image_step2 = None
        
        path1 = ASSETS_IMAGES_DIR / "step 1.png"
        path2 = ASSETS_IMAGES_DIR / "step 2.png"
        
        if path1.exists():
            self.image_step1 = pygame.image.load(str(path1)).convert_alpha()
        if path2.exists():
            self.image_step2 = pygame.image.load(str(path2)).convert_alpha()

        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        self.step = 1
        self.is_deadly = False
        self._draw_laser()
        self.update()

    def set_step(self, step):
        self.step = step
        self._draw_laser()

    def _draw_laser(self):
        """Sử dụng ảnh từ assets để hiển thị laser"""
        if self.step == 1:
            self.is_deadly = False
            if self.image_step1:
                self.image = self.image_step1
            else:
                # Fallback nếu thiếu file
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.line(self.image, (255, 0, 0, 100), (self.width//2, 0), (self.width//2, self.height), 2)
        else:
            self.is_deadly = True
            if self.image_step2:
                self.image = self.image_step2
            else:
                # Fallback
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(self.image, (255, 255, 255), (self.width//2 - 10, 0, 20, self.height))



    def update(self):
        # Tia laze luôn đi theo vị trí X của Boss
        if self.owner.alive():
            # Cộng thêm offset 10px sang phải để cân với tâm của boss
            self.rect.centerx = self.owner.rect.centerx + 10
            # Điều chỉnh vị trí Y để laze không bị đè lên chân/mình gà

            # Đẩy điểm bắt đầu của laze xuống thấp hơn một chút (sát mép dưới của "cục đỏ")
            eff_h = 100 # 40 * 2.5
            # Thay vì bắt đầu từ tâm (eff_h // 2), ta bắt đầu gần đáy (eff_h - 20)
            start_y_offset = self.owner.rect.height - 25 # Đẩy xuống sát đáy sprite boss
            self.rect.top = self.owner.rect.top + start_y_offset
        else:
            self.kill()





# =============================================================================
# CLASS: Bullet
# MÔ TẢ: Đại diện cho một viên đạn do Player bắn ra.
#         Tự động bay lên và tự xóa khi ra khỏi màn hình (tối ưu RAM).
# =============================================================================
class Bullet(pygame.sprite.Sprite):

    def __init__(self, x, y, speed_x=0, bullet_type="normal"):
        """
        Khởi tạo viên đạn tại vị trí (x, y) — thường là đầu nòng súng Player.

        Tham số:
            x (int): Tọa độ X tâm viên đạn.
            y (int): Tọa độ Y đỉnh viên đạn (đặt tại mũi máy bay).
            speed_x (float): Vận tốc đạn đi theo chiều ngang (cho đạn toả).
            bullet_type (str): "normal", "strong", "missile"
        """
        super().__init__()
        self.speed_x = speed_x
        self.bullet_type = bullet_type
        self.health = 1  # Mặc định đạn có 1 "máu", trúng là biến mất

        # Load bullet image based on type
        sheet_name = "bullet_pierce.png" if self.bullet_type == "pierce" else "bullet.png"
        # Scale down the 40x40 images to fit the game better
        scale = 0.5 if self.bullet_type == "pierce" else 0.35
        
        # Load frames (tick = 1)
        self.frames = _load_sprite_sheet_frames(
            sheet_name=sheet_name,
            frame_width=40, # Kích thước gốc trong file là 40x40
            frame_height=40,
            frame_count=1,
            row=0,
            scale=scale
        )

        
        if self.frames:
            self.image = self.frames[0]
        else:
            # Fallback if image not found
            if self.bullet_type == "pierce":
                # Đạn xuyên: to hơn, màu đỏ, có 2 "máu"
                self.health = 2
                self.image = pygame.Surface((BULLET_WIDTH * 1.5, BULLET_HEIGHT * 1.5), pygame.SRCALPHA)
                pygame.draw.rect(self.image, COLOR_RED,
                                 (0, 0, self.image.get_width(), self.image.get_height()), border_radius=4)
            else:
                # Đạn thường: màu vàng
                self.image = pygame.Surface((BULLET_WIDTH, BULLET_HEIGHT), pygame.SRCALPHA) # Đạn thường
                pygame.draw.rect(self.image, COLOR_YELLOW,
                                 (0, 0, BULLET_WIDTH, BULLET_HEIGHT), border_radius=2)
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
        self.rect.x += self.speed_x

        # --- Xóa đạn khỏi tất cả Group khi ra khỏi màn hình ---
        if self.rect.bottom < 0 or self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
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
        """
        super().__init__()

        # --- Load sprite sheets ---
        # Trứng bình thường (Asset hiện tại là 40x40, chỉ có 1 frame)
        self.normal_frames = _load_sprite_sheet_frames(
            sheet_name="egg_sheet.png",
            frame_width=EGG_WIDTH,
            frame_height=EGG_HEIGHT,
            frame_count=1,
            row=0,
            scale=0.75
        )
        
        # Hiệu ứng bể trứng (Asset hiện tại là 40x40, chỉ có 1 frame)
        self.break_frames = _load_sprite_sheet_frames(
            sheet_name="egg_break_sheet.png",
            frame_width=EGG_WIDTH,
            frame_height=EGG_HEIGHT,
            frame_count=1,
            row=0,
            scale=0.75
        )

        # Fallback nếu không load được ảnh
        if not self.normal_frames:
            self.normal_frames = [self._create_fallback_egg()]
        if not self.break_frames:
            self.break_frames = [self._create_fallback_break()]

        self.frames = self.normal_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        
        self.is_breaking = False
        self.animation_interval = 150  # ms/frame
        self.break_duration = 500      # Trứng vỡ hiện trong 500ms nếu chỉ có 1 frame
        self.break_start_time = 0
        self.last_frame_update = pygame.time.get_ticks()

        # Pre-calculate masks for pixel-perfect collision
        self.normal_masks = [pygame.mask.from_surface(f) for f in self.normal_frames]
        self.break_masks = [pygame.mask.from_surface(f) for f in self.break_frames]
        self.masks = self.normal_masks
        self.mask = self.masks[self.frame_index]

        # --- Thiết lập vị trí ---
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top     = y

    def _create_fallback_egg(self):
        """Tạo hình trứng giả lập nếu thiếu file ảnh."""
        surf = pygame.Surface((EGG_WIDTH, EGG_HEIGHT), pygame.SRCALPHA)
        pygame.draw.ellipse(surf, COLOR_WHITE, (4, 4, EGG_WIDTH - 8, EGG_HEIGHT - 8))
        pygame.draw.ellipse(surf, (200, 200, 200), (4, 4, EGG_WIDTH - 8, EGG_HEIGHT - 8), 1)
        return surf

    def _create_fallback_break(self):
        """Tạo hình bể trứng giả lập."""
        surf = pygame.Surface((EGG_WIDTH, EGG_HEIGHT), pygame.SRCALPHA)
        pygame.draw.arc(surf, COLOR_WHITE, (4, 4, EGG_WIDTH - 8, EGG_HEIGHT - 8), 0, 3.14, 2)
        return surf

    def update(self):
        """
        Gọi mỗi frame.
        - Nếu đang rơi: di chuyển xuống và kiểm tra chạm đáy.
        - Nếu chạm đáy: chuyển sang trạng thái 'breaking'.
        - Nếu đang break: chạy hết animation rồi biến mất.
        """
        now = pygame.time.get_ticks()

        if not self.is_breaking:
            # Di chuyển xuống
            self.rect.y += EGG_SPEED
            
            # Animation khi đang rơi (nếu có > 1 frame)
            if now - self.last_frame_update >= self.animation_interval:
                self.last_frame_update = now
                if len(self.frames) > 1:
                    self.frame_index = (self.frame_index + 1) % len(self.frames)
                    self.image = self.frames[self.frame_index]
                    self.mask = self.masks[self.frame_index]

            # Kiểm tra chạm đáy màn hình
            if self.rect.bottom >= SCREEN_HEIGHT:
                self.rect.bottom = SCREEN_HEIGHT # Dừng lại ở đáy
                self.is_breaking = True
                self.frames = self.break_frames
                self.masks = self.break_masks
                self.frame_index = 0
                self.break_start_time = now
                self.last_frame_update = now
                self.image = self.frames[self.frame_index]
                self.mask = self.masks[self.frame_index]
        else:
            # Xử lý animation bể trứng
            if len(self.frames) > 1:
                if now - self.last_frame_update >= self.animation_interval:
                    self.last_frame_update = now
                    self.frame_index += 1
                    if self.frame_index >= len(self.frames):
                        self.kill()
                    else:
                        self.image = self.frames[self.frame_index]
                        self.mask = self.masks[self.frame_index]
            else:
                # Nếu chỉ có 1 frame break, giữ nó hiện ra một lúc
                if now - self.break_start_time >= self.break_duration:
                    self.kill()

# =============================================================================
# CLASS: Explosion
# MÔ TẢ: Hiệu ứng nổ gồm nhiều frame khi Player va chạm trực tiếp với gà/trứng.
# =============================================================================
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        # Tạo 6 frame cho hiệu ứng nổ (Vàng -> Cam -> Đỏ -> Xám)
        colors = [COLOR_WHITE, COLOR_YELLOW, COLOR_ORANGE, COLOR_RED, (100, 100, 100), (50, 50, 50)]
        for i in range(6):
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            radius = 10 + i * 5
            pygame.draw.circle(surf, colors[i], (30, 30), radius)
            if i < 4:
                pygame.draw.circle(surf, COLOR_WHITE, (30, 30), radius // 2)
            self.frames.append(surf)

        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50  # Tốc độ chuyển frame (ms)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]
                self.rect = self.image.get_rect(center=self.rect.center)


# =============================================================================
# CLASS: ShieldSprite
# MÔ TẢ: Hiệu ứng vòng bảo vệ hỗ trợ hiển thị cho Player.
# =============================================================================
class ShieldSprite(pygame.sprite.Sprite):
    def __init__(self, target):
        super().__init__()
        self.target = target
        self.frames = _load_sprite_sheet_frames(
            sheet_name="shield_player.png",
            frame_width=PLAYER_WIDTH,
            frame_height=PLAYER_HEIGHT,
            frame_count=3,
            row=0,
            scale=PLAYER_SCALE
        )
        self.frame_index = 0
        self.image = self.frames[self.frame_index] if self.frames else pygame.Surface((0,0))
        self.animation_interval = 100
        self.last_update = pygame.time.get_ticks()

        self.rect = self.image.get_rect(center=self.target.rect.center)

    def update(self):
        if hasattr(self.target, 'has_shield') and self.target.has_shield:
            self.rect.center = self.target.rect.center
            # Animation (tick = 3)
            now = pygame.time.get_ticks()
            if now - self.last_update >= self.animation_interval:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
        else:
            self.kill()



# =============================================================================
# CLASS: PowerUp
# MÔ TẢ: Đại diện cho một vật phẩm tăng sức mạnh (boost) rơi từ trên xuống.
#         Tự động bay xuống và tự xóa khi ra khỏi màn hình.
# =============================================================================
class PowerUp(pygame.sprite.Sprite):

    def __init__(self, x, y, p_type):
        """
        Khởi tạo vật phẩm tăng sức mạnh tại vị trí (x, y).

        Tham số:
            x (int): Tọa độ X tâm vật phẩm.
            y (int): Tọa độ Y đỉnh vật phẩm.
            p_type (str): Loại vật phẩm (key trong POWERUP_TYPES).
        """
        super().__init__()
        self.type = p_type
        
        # Mapping từ loại powerup sang tên file ảnh (Dùng hộp quà màu sắc)
        POWERUP_IMAGES = {
            "pierce":      "red.png",
            "triple_shot": "green.png",
            "shield":      "15.png",    # Giả định 15.png là màu vàng (Yellow)
            "rapid_fire":  "purple.png",
            "double_shot": "pink.png",
            "cursed":      "black.png"
        }

        
        image_name = POWERUP_IMAGES.get(p_type)
        self.frames = _load_sprite_sheet_frames(
            sheet_name=image_name,
            frame_width=40, # Kích thước gốc trong file là 40x40
            frame_height=40,
            frame_count=1, # tick = 1
            row=0,
            scale=1.0
        )

        if self.frames:
            self.original_image = pygame.transform.scale(self.frames[0], (POWERUP_WIDTH, POWERUP_HEIGHT))
            self.image = self.original_image.copy()
        else:
            # Fallback nếu không load được ảnh
            self.image = pygame.Surface((POWERUP_WIDTH, POWERUP_HEIGHT), pygame.SRCALPHA)
            box_color = POWERUP_TYPES.get(p_type, COLOR_WHITE)
            ribbon_color = COLOR_WHITE
            pygame.draw.rect(self.image, box_color, (0, 4, POWERUP_WIDTH, POWERUP_HEIGHT - 4))
            pygame.draw.rect(self.image, ribbon_color, (POWERUP_WIDTH // 2 - 2, 4, 4, POWERUP_HEIGHT - 4))
            pygame.draw.rect(self.image, ribbon_color, (0, POWERUP_HEIGHT // 2, POWERUP_WIDTH, 4))
            pygame.draw.circle(self.image, ribbon_color, (POWERUP_WIDTH // 2 - 5, 4), 5)
            pygame.draw.circle(self.image, ribbon_color, (POWERUP_WIDTH // 2 + 5, 4), 5)
            self.original_image = self.image.copy()

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

        # --- Biến phục vụ chuyển động lượn sóng và animation ---
        self.base_x = x
        self.wave_angle = 0

    def update(self):

        """
        Gọi mỗi frame. Di chuyển rơi dọc, lượn sóng ngang, chạy animation nhịp đập 
        và tự xóa khi ra khỏi màn hình.
        """
        # 1. Di chuyển rơi dọc
        self.rect.y += POWERUP_SPEED

        # 2. Chuyển động lượn sóng ngang (Sine wave)
        self.wave_angle += 0.05
        self.rect.x = self.base_x + int(math.sin(self.wave_angle) * 30)
        
        # 3. Animation nhịp đập (Pulsing Effect)
        scale_factor = 1.0 + math.sin(self.wave_angle * 3) * 0.1
        new_size = (int(POWERUP_WIDTH * scale_factor), int(POWERUP_HEIGHT * scale_factor))
        self.image = pygame.transform.scale(self.original_image, new_size)
        
        # Giữ nguyên tâm điểm của vật phẩm sau khi thay đổi kích thước
        self.rect = self.image.get_rect(center=self.rect.center)

        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
