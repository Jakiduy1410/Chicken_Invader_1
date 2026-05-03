# =============================================================================
# FILE: game_logic.py
# MÔ TẢ: Trung tâm điều phối logic game — "bộ não" của toàn bộ project.
#         Class Game quản lý: vòng lặp chính, đội hình gà (EnemyFleet),
#         va chạm, điểm số, chuyển Wave, và trạng thái Game Over / Win.
#
# PHÂN CÔNG TEAM:
#   - Class EnemyFleet → Dev phụ trách đội hình & chuyển động gà
#   - Class Game       → Dev phụ trách va chạm, level, và UI điểm số
# =============================================================================

import pygame
import sys
import random
from pathlib import Path
from settings import *
from sprites import Player, Enemy, Bullet, Egg, PowerUp
from backend import AudioManager, get_top_scores, save_score, is_story_finished, save_progress
from level import get_wave_pattern
import ui


# Đường dẫn tới thư mục ảnh
ASSETS_IMAGES_DIR = Path(__file__).resolve().parent / "assets" / "image"

# =============================================================================
# GAME STATES
# =============================================================================
STATE_MENU        = "MENU"
STATE_PLAY_MODE   = "PLAY_MODE"
STATE_PLAYING     = "PLAYING"
STATE_LEADERBOARD = "LEADERBOARD"
STATE_SETTINGS    = "SETTINGS"



# =============================================================================
# CLASS: EnemyFleet
# MÔ TẢ: Quản lý toàn bộ đội hình gà (grid formation).
#         Điều phối chuyển động đồng bộ: ngang → chạm biên → hạ xuống → đổi chiều.
# =============================================================================
class EnemyFleet:
    def __init__(self, all_sprites_group, enemies_group, eggs_group, wave=1):
        """
        Khởi tạo đội hình gà dạng lưới (rows × cols).

        Tham số:
            all_sprites_group (pygame.sprite.Group): Group chứa tất cả sprite để render.
            enemies_group     (pygame.sprite.Group): Group riêng cho Enemy để detect collision.
            eggs_group        (pygame.sprite.Group): Group riêng cho Egg để detect collision.
        """
        # Tham chiếu đến các Group bên ngoài (không tạo mới để tránh mất liên kết)
        self.all_sprites = all_sprites_group
        self.enemies     = enemies_group
        self.eggs        = eggs_group

        # Hướng di chuyển ngang: +1 = sang phải, -1 = sang trái
        self.direction = 1

        # Tốc độ hiện tại — có thể tăng theo wave
        self.speed_x = ENEMY_SPEED_X
        self.v_direction = 1 # 1 = xuống, -1 = lên (cho logic bật lại)
        self.last_egg_drop_time = 0 # Thời điểm thả trứng gần nhất
        self.boss_initial_y = 100 # Vị trí ban đầu mặc định của Boss

        # Tạo đội hình lần đầu
        self.wave = wave
        coords = get_wave_pattern(self.wave)
        self._spawn_fleet(pattern_coords=coords)

    def _spawn_fleet(self, pattern_coords=None):
        """
        Sinh đội hình gà.
        - Nếu pattern_coords được cung cấp (từ level.py), dùng tọa độ đó.
        - Nếu không (mặc định), tự tính lưới hoặc sinh Boss.
        """
        # 1. Nếu có tọa độ từ level.py, dùng luôn cho gà con
        # Offset để cả đội hình "bay xuống" đồng bộ
        spawn_offset_y = -450 
        
        # Tốc độ trượt: Wave 2 chậm hơn (1.5), các wave khác 3.0
        wave_slide_speed = 1.5 if self.wave == 2 else 3.0

        if pattern_coords:
            for i, (px, py) in enumerate(pattern_coords):
                type_cycle = ["chick_1", "chick_2", "chick_3", "chick_4"]
                enemy_type = type_cycle[i % len(type_cycle)]
                hp = ENEMY_HP_BY_TYPE[enemy_type]
                # Gà được tạo ở vị trí (px, py - offset) nhưng có target là (px, py)
                enemy = Enemy(px, py + spawn_offset_y, enemy_type=enemy_type, hp=hp, slide_speed=wave_slide_speed)
                enemy.target_y = py
                self.all_sprites.add(enemy)
                self.enemies.add(enemy)
            return

        # 2. Logic dự phòng hoặc cho Boss
        boss_render_h = int(BOSS_HEIGHT * BOSS_SCALE)
        
        if self.wave == MAX_WAVES:
            current_grid_top = -150 
            boss_offset_y = boss_render_h + 20
        else:
            current_grid_top = ENEMY_GRID_TOP
            boss_offset_y = 0

        # Nếu không có pattern từ level.py, sinh 1 boss ở wave cuối
        if self.wave == MAX_WAVES:
            final_boss_y = current_grid_top + (boss_render_h // 2)
            self.boss_initial_y = final_boss_y
            boss = Enemy(
                SCREEN_WIDTH // 2,
                final_boss_y + spawn_offset_y, # Cũng áp dụng offset cho boss
                enemy_type="boss",
                hp=ENEMY_HP_BY_TYPE["boss"],
                slide_speed=3.0 # Boss bay xuống bình thường
            )
            boss.target_y = final_boss_y
            self.all_sprites.add(boss)
            self.enemies.add(boss)
        else:
            # Fallback lưới nếu level.py trả về [] (không nên xảy ra trừ khi cấu hình sai)
            total_grid_width  = (ENEMY_COLS - 1) * ENEMY_H_SPACING
            start_x = (SCREEN_WIDTH - total_grid_width) // 2
            for row in range(ENEMY_ROWS):
                for col in range(ENEMY_COLS):
                    x = start_x + col * ENEMY_H_SPACING
                    y = current_grid_top + row * ENEMY_V_SPACING
                    enemy = Enemy(x, y + spawn_offset_y, enemy_type="chick_1", hp=1)
                    enemy.target_y = y
                    self.all_sprites.add(enemy)
                    self.enemies.add(enemy)

    def spawn_reinforcements(self, boss_rect=None):
        """Sinh thêm gà hỗ trợ cho Boss khi Boss chuyển phase."""
        # Xóa các con gà cũ (trừ boss) để tránh lag và rối mắt
        for enemy in self.enemies:
            if enemy.enemy_type != "boss":
                enemy.kill()
                
        # Chọn ngẫu nhiên pattern (Chỉ chọn Wave 1 hoặc Wave 4 vì Wave 2, 3 quá khó cho màn Boss)
        rand_wave = random.choice([1, 3])
        coords = get_wave_pattern(rand_wave)
        
        # Nếu có boss_rect, dịch chuyển tọa độ để gà spawn "dưới chân" boss
        if boss_rect:
            # Tìm Y cao nhất trong pattern để căn chỉnh
            min_y = min(y for _, y in coords) if coords else 0
            # Offset = chân boss - min_y của pattern - một khoảng để sát boss hơn
            y_offset = boss_rect.bottom - min_y - 40
            
            new_coords = []
            for px, py in coords:
                new_coords.append((px, py + y_offset))
            coords = new_coords

        self._spawn_fleet(pattern_coords=coords)

    def update(self):
        """
        Gọi mỗi frame. Điều phối chuyển động toàn đội hình:
        1. Di chuyển tất cả gà sang trái hoặc phải.
        2. Phát hiện khi bất kỳ con gà nào chạm biên màn hình.
        3. Nếu chạm biên: đảo hướng và hạ toàn đội hình xuống.

        Trả về:
            bool: True nếu đội hình đã hạ xuống quá thấp (Player thua).
        """
        # Cờ báo có cần đổi chiều không
        should_reverse = False

        for enemy in self.enemies:
            # Di chuyển ngang theo hướng hiện tại
            enemy.rect.x += self.speed_x * self.direction

            # Kiểm tra chạm biên PHẢI
            if enemy.rect.right > SCREEN_WIDTH:
                should_reverse = True
                break  # Chỉ cần 1 con chạm là đủ để đổi chiều

            # Kiểm tra chạm biên TRÁI
            if enemy.rect.left < 0:
                should_reverse = True
                break

        if should_reverse:
            self._reverse_and_drop()

        # Kiểm tra xem đội hình có hạ xuống quá thấp chưa (gà chạm vùng Player)
        for enemy in self.enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT - 60:
                return True  # Báo hiệu Game Over

        return False  # Đội hình vẫn trong giới hạn an toàn

    def _reverse_and_drop(self):
        """
        (Private) Đảo chiều di chuyển và hạ toàn bộ đội hình xuống một bậc.
        Đồng thời đẩy tất cả gà về phía trong màn hình để tránh bị kẹt ở biên.
        Sau đó, chọn ngẫu nhiên một số gà để thả trứng.
        """
        self.direction *= -1  # Đảo chiều: +1 → -1 hoặc ngược lại

        if self.enemies:
            lowest_y = max(e.target_y for e in self.enemies)
            highest_y = min(e.target_y for e in self.enemies)
            
            # 1/3 cách đáy tương đương với 2/3 màn hình (khoảng 460-500px)
            bounce_threshold = SCREEN_HEIGHT * 0.6 
            # Giới hạn trên: không để con cao nhất bay quá xa màn hình
            top_threshold = 50 
            
            if lowest_y >= bounce_threshold:
                self.v_direction = -1
            elif highest_y <= top_threshold:
                self.v_direction = 1

        for enemy in self.enemies:
            # Chỉ cập nhật target_y để cả đội hình "trượt" xuống từ từ trong Enemy.update
            if hasattr(enemy, "target_y"):
                enemy.target_y += self.v_direction * ENEMY_DROP_Y
            else:
                # Nếu không có target_y (đề phòng), hạ ngay lập tức
                enemy.rect.y += self.v_direction * ENEMY_DROP_Y

            # Đẩy gà vào trong màn hình nếu vẫn đang tràn ra ngoài
            if enemy.rect.right > SCREEN_WIDTH:
                enemy.rect.right = SCREEN_WIDTH
            if enemy.rect.left < 0:
                enemy.rect.left = 0

        # Thả trứng: chỉ thả nếu đạt tỉ lệ EGG_DROP_CHANCE và hết cooldown
        now = pygame.time.get_ticks()
        if now - self.last_egg_drop_time > 1500: # Cooldown 1.5 giây
            if random.random() < EGG_DROP_CHANCE:
                self.last_egg_drop_time = now
                if len(self.enemies) >= EGG_DROP_COUNT:
                    droppers = random.sample(list(self.enemies), EGG_DROP_COUNT)
                else:
                    droppers = list(self.enemies)  # Nếu ít gà hơn, thả tất cả
        
                for enemy in droppers:
                    egg = Egg(enemy.rect.centerx, enemy.rect.bottom)
                    self.all_sprites.add(egg)
                    self.eggs.add(egg)

    def increase_speed(self, increment=SPEED_INCREMENT):
        """
        Tăng tốc độ đội hình — gọi khi bắt đầu wave mới.

        Tham số:
            increment (float): Lượng tăng thêm (mặc định lấy từ settings.py).
        """
        self.speed_x += increment
        self.wave += 1

    def is_empty(self):
        """
        Kiểm tra xem đội hình đã bị tiêu diệt hết chưa.

        Trả về:
            bool: True nếu không còn con gà nào.
        """
        return len(self.enemies) == 0

    def reset(self, new_speed=None):
        """
        Xóa đội hình cũ và tạo lại đội hình mới — dùng khi chuyển wave.

        Tham số:
            new_speed (float | None): Nếu truyền vào, đặt lại tốc độ cụ thể.
        """
        # Xóa toàn bộ gà hiện tại khỏi cả hai group
        self.enemies.empty()

        if new_speed is not None:
            self.speed_x = new_speed

        self.direction = 1  # Reset hướng về phải
        
        # Lấy pattern từ level.py
        coords = get_wave_pattern(self.wave)
        self._spawn_fleet(pattern_coords=coords)


# =============================================================================
# CLASS: Game
# MÔ TẢ: Lớp trung tâm điều phối toàn bộ game.
#         Quản lý: vòng lặp game, sự kiện, va chạm, điểm số, wave, HUD.
# =============================================================================
class Game:

    def __init__(self):
        """
        Khởi tạo toàn bộ hệ thống game:
        - Khởi động Pygame engine.
        - Tạo màn hình và clock.
        - Tạo các Sprite Group.
        - Tạo Player và EnemyFleet.
        - Thiết lập điểm số và trạng thái ban đầu.
        """
        pygame.init()

        # --- Cửa sổ game ---
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)

        # --- Clock để giới hạn FPS ---
        self.clock = pygame.time.Clock()

        # --- Font chữ cho HUD (Heads-Up Display) ---
        self.font_large  = pygame.font.SysFont("consolas", 36, bold=True)
        self.font_medium = pygame.font.SysFont("consolas", 24)
        self.font_small  = pygame.font.SysFont("consolas", 18)

        # --- UI Screens ---
        self.ui_menu        = ui.MainMenuScreen()
        self.ui_leaderboard = ui.LeaderboardScreen()
        self.ui_play_mode   = ui.PlayModeScreen()
        self.ui_settings    = ui.SettingsScreen()
        self.ui_hud         = ui.HUD()

        # --- Sprite Groups ---
        # Group chứa TẤT CẢ sprite — dùng LayeredUpdates để quản lý lớp vẽ (layer)
        self.all_sprites = pygame.sprite.LayeredUpdates()
        # Group riêng cho Enemy — dùng để kiểm tra va chạm đạn-gà
        self.enemies     = pygame.sprite.Group()
        # Group riêng cho Bullet — dùng để kiểm tra va chạm đạn-gà và gà-player
        self.bullets     = pygame.sprite.Group()
        # Group riêng cho Egg — dùng để kiểm tra va chạm trứng-player
        self.eggs        = pygame.sprite.Group()
        # Group riêng cho PowerUp — dùng để kiểm tra va chạm vật phẩm-player
        self.powerups    = pygame.sprite.Group()
        # Group riêng cho Laser của Boss
        self.lasers      = pygame.sprite.Group()


        # --- Trạng thái game ---
        self.state      = STATE_MENU
        self.game_mode  = "story" # "story" hoặc "infinite"
        self.unlocked_infinite = is_story_finished()
        self.score      = 0       # Điểm số hiện tại
        self.lives      = 3       # Số mạng của người chơi
        self.wave       = 1      # Bắt đầu từ wave 1
        self.running    = True    # Game đang chạy?
        self.game_over  = False   # Trạng thái Game Over
        self.victory    = False   # Trạng thái chiến thắng

        # Boss phase tracking
        self.boss_last_phase_hp = ENEMY_HP_BY_TYPE["boss"]
        
        # --- Khởi tạo Âm thanh ---
        self.audio = AudioManager()
        self.audio.load_resources()
        self.audio.play_bgm() 


        # --- UI Buttons for End Screens ---
        self.btn_restart = pygame.Rect(SCREEN_WIDTH // 2 - 210, SCREEN_HEIGHT // 2 + 60, 200, 50)
        self.btn_quit_game = pygame.Rect(SCREEN_WIDTH // 2 + 10, SCREEN_HEIGHT // 2 + 60, 200, 50)

        # --- Khởi tạo Player ---
        self.player = Player()
        self.all_sprites.add(self.player)

        # --- Khởi tạo đội hình gà ---
        self.fleet = EnemyFleet(self.all_sprites, self.enemies, self.eggs, self.wave)

        # --- Load Power-up Icons cho HUD ---
        self.powerup_icons = {}
        icon_map = {
            "pierce":      "pierce.png",
            "triple_shot": "tripple.png",
            "shield":      "shield.png",
            "rapid_fire":  "rapid.png",
            "double_shot": "double.png",
            "cursed":      "curse.png"
        }
        for p_type, filename in icon_map.items():
            path = ASSETS_IMAGES_DIR / filename
            if path.exists():
                img = pygame.image.load(str(path)).convert_alpha()
                self.powerup_icons[p_type] = pygame.transform.scale(img, (30, 30))


    # -------------------------------------------------------------------------
    # VÒNG LẶP CHÍNH
    # -------------------------------------------------------------------------

    def run(self):
        """Vòng lặp chính của game."""
        while self.running:
            self._handle_events()

            if self.state == STATE_PLAYING:
                if not self.game_over and not self.victory:
                    self._update()

            self._draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    # -------------------------------------------------------------------------
    # XỬ LÝ SỰ KIỆN
    # -------------------------------------------------------------------------

    def _handle_events(self):
        """Xử lý sự kiện tùy theo trạng thái game."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_MENU
                    else:
                        self.running = False

                if event.key == pygame.K_r and (self.game_over or self.victory):
                    self._restart()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: # Left click
                    self._handle_click(event.pos)

    def _handle_click(self, pos):
        """Xử lý logic click chuột cho các menu."""
        if self.state == STATE_PLAYING and (self.game_over or self.victory):
            if self.btn_restart.collidepoint(pos):
                self._restart()
            elif self.btn_quit_game.collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_MENU:
            if self.ui_menu.buttons["play"].collidepoint(pos):
                self.state = STATE_PLAY_MODE
            elif self.ui_menu.buttons["leaderboard"].collidepoint(pos):
                self.state = STATE_LEADERBOARD
            elif self.ui_menu.buttons["settings"].collidepoint(pos):
                self.state = STATE_SETTINGS
            elif self.ui_menu.buttons["quit"].collidepoint(pos):
                self.running = False

        elif self.state == STATE_PLAY_MODE:
            if self.ui_play_mode.buttons["story"].collidepoint(pos):
                self.game_mode = "story"
                self._restart()
                self.state = STATE_PLAYING
            elif self.ui_play_mode.buttons["infinite"].collidepoint(pos):
                if self.unlocked_infinite:
                    self.game_mode = "infinite"
                    self._restart()
                    self.state = STATE_PLAYING
            elif self.ui_play_mode.buttons["back"].collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_LEADERBOARD:
            if self.ui_leaderboard.back_button.collidepoint(pos):
                self.state = STATE_MENU

        elif self.state == STATE_SETTINGS:
            if self.ui_settings.back_button.collidepoint(pos):
                self.state = STATE_MENU
            elif self.ui_settings.buttons["sfx"].collidepoint(pos):
                self.audio.toggle_sfx()
            elif self.ui_settings.buttons["music"].collidepoint(pos):
                self.audio.toggle_music()
            elif self.ui_settings.buttons["difficulty"].collidepoint(pos):
                # Placeholder for difficulty toggle
                pass
            elif self.ui_settings.buttons["screen"].collidepoint(pos):
                # Placeholder for screen mode toggle
                pass

    # -------------------------------------------------------------------------
    # CẬP NHẬT LOGIC
    # -------------------------------------------------------------------------

    def _update(self):
        """
        (Private) Cập nhật toàn bộ trạng thái game mỗi frame:
        1. Cập nhật Player (di chuyển + bắn đạn).
        2. Cập nhật tất cả Sprite khác (đạn bay, gà...).
        3. Di chuyển đội hình gà.
        4. Xử lý va chạm.
        5. Kiểm tra điều kiện thắng/thua và chuyển wave.
        """
        # Cập nhật Player: di chuyển
        self.player.update()

        # Xử lý bắn đạn (tách riêng để truyền Group vào)
        self.player.handle_shoot(self.all_sprites, self.bullets, self.audio)


        # Cập nhật tất cả sprite còn lại (đạn bay lên, gà animation...)
        # Dùng vòng lặp riêng để không gọi player.update() 2 lần
        for sprite in self.all_sprites:
            if sprite is not self.player:
                if isinstance(sprite, Enemy):
                    sprite.update(self.all_sprites, self.lasers, self.audio)
                else:
                    sprite.update()



        # Di chuyển đội hình gà và kiểm tra gà chạm đáy
        # Giảm tốc độ hạ xuống (drop) nếu cần, ở đây ENEMY_DROP_Y trong settings
        fleet_reached_bottom = self.fleet.update()
        if fleet_reached_bottom:
            self.game_over = True
            return  # Dừng update ngay lập tức

        # Xử lý Logic Boss Phase (mất 1/5 HP)
        self._update_boss_phase()

        # Xử lý va chạm đạn - gà
        self._handle_bullet_enemy_collision()

        # Xử lý va chạm gà - player
        self._handle_enemy_player_collision()

        # Xử lý va chạm trứng - player
        self._handle_egg_player_collision()

        # Xử lý va chạm vật phẩm - player
        self._handle_powerup_collision()

        # Xử lý va chạm laser - player
        self._handle_laser_player_collision()

        # Kiểm tra điều kiện chuyển wave / chiến thắng

        self._check_wave_progression()

    # -------------------------------------------------------------------------
    # XỬ LÝ VA CHẠM
    # -------------------------------------------------------------------------

    def _handle_bullet_enemy_collision(self):
        """
        (Private) Kiểm tra va chạm giữa đạn và gà.

        Sử dụng groupcollide() của Pygame:
        - Tham số True, True → Tự động xóa cả đạn lẫn gà khi va chạm.
        - Mỗi cặp va chạm tính SCORE_PER_KILL điểm.
        """
        # hits là dict: {bullet: [danh sách enemy va chạm]}
        hits = pygame.sprite.groupcollide(
            self.bullets,  # Group 1: Đạn
            self.enemies,  # Group 2: Gà
            True,          # Xóa đạn sau va chạm
            False          # Không xóa gà ngay, cần trừ máu
        )

        # Trừ máu từng enemy; chỉ cộng điểm khi enemy chết.
        for bullet, hit_enemies in hits.items():
            for enemy in hit_enemies:
                # Tính sát thương dựa trên loại đạn
                damage = BULLET_DAMAGE
                if hasattr(bullet, 'bullet_type') and bullet.bullet_type == "pierce":
                    damage = BULLET_PIERCE_DAMAGE
                    
                if enemy.take_damage(damage):
                    score_multiplier = enemy.max_hp
                    points = SCORE_PER_KILL * score_multiplier
                    
                    # Áp dụng nhân hệ số cho Infinite Mode
                    if self.game_mode == "infinite":
                        points = int(points * (1 + 0.1 * self.wave))
                        
                    self.score += points
                    self.audio.play_chicken_exp()


                    # --- Logic rơi PowerUp ---
                    if random.random() < POWERUP_DROP_RATE:
                        p_type = random.choice(list(POWERUP_TYPES.keys()))
                        p = PowerUp(enemy.rect.centerx, enemy.rect.centery, p_type)
                        self.all_sprites.add(p)
                        self.powerups.add(p)

    def _handle_enemy_player_collision(self):
        """
        (Private) Kiểm tra va chạm giữa đội hình gà và Player.

        Nếu bất kỳ con gà nào chạm vào Player → Game Over ngay lập tức.
        Sử dụng spritecollide() với dokill=False để chỉ phát hiện, không tự xóa.
        """
        collisions = pygame.sprite.spritecollide(
            self.player,   # Sprite cần kiểm tra
            self.enemies,  # Group để kiểm tra chồng lên
            False,         # Không xóa tự động — để hiển thị Game Over trước
            collided=pygame.sprite.collide_mask
        )

        if collisions:
            if self.player.has_shield:
                # Shield bảo vệ được 1 nhát: mất khiên và giết enemy va chạm
                self.player.has_shield = False
                self.player.shield_expire_time = 0
                self.audio.play_explosion()
                for enemy in collisions:
                    enemy.kill()
            else:
                self.audio.play_explosion()
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    # Tạm thời reset vị trí player hoặc cho bất tử ngắn hạn
                    self._respawn_player()



    def _handle_egg_player_collision(self):
        """
        (Private) Kiểm tra va chạm giữa trứng và Player.

        Nếu bất kỳ quả trứng nào chạm vào Player → Game Over ngay lập tức.
        Sử dụng spritecollide() với dokill=False để chỉ phát hiện, không tự xóa.
        """
        collisions = pygame.sprite.spritecollide(
            self.player,  # Sprite cần kiểm tra
            self.eggs,    # Group để kiểm tra chồng lên
            False,        # Không xóa tự động — để hiển thị Game Over trước
            collided=pygame.sprite.collide_mask
        )

        if collisions:
            if self.player.has_shield:
                # Shield bảo vệ được 1 nhát khỏi trứng
                self.player.has_shield = False
                self.player.shield_expire_time = 0
                self.audio.play_explosion()
                for egg in collisions:
                    egg.kill()
            else:
                self.audio.play_explosion()
                self.lives -= 1
                for egg in collisions: egg.kill() # Xóa quả trứng đã va chạm
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self._respawn_player()

    def _respawn_player(self):
        """Reset vị trí player và cho bất tử tạm thời."""
        self.player.rect.centerx = SCREEN_WIDTH // 2
        self.player.rect.bottom = SCREEN_HEIGHT - 70
        # Thêm hiệu ứng bất tử ngắn hạn (dùng shield tạm thời 2 giây)
        self.player.apply_powerup("shield")
        self.player.shield_expire_time = pygame.time.get_ticks() + 2000



    def _handle_powerup_collision(self):
        """
        (Private) Kiểm tra va chạm giữa Player và vật phẩm tăng sức mạnh.
        """
        hits = pygame.sprite.spritecollide(
            self.player,
            self.powerups,
            True  # Xóa vật phẩm sau khi ăn
        )

        for p in hits:
            # Áp dụng buff cho Player
            self.player.apply_powerup(p.type)
            # Có thể cộng thêm một ít điểm khi ăn item
            self.score += 50

    def _handle_laser_player_collision(self):
        """
        (Private) Kiểm tra va chạm giữa tia laze của Boss và Player.
        """
        hits = pygame.sprite.spritecollide(
            self.player,
            self.lasers,
            False,
            collided=pygame.sprite.collide_mask
        )

        if hits:
            # Chỉ xử lý va chạm nếu tia laze đang ở trạng thái gây sát thương (Step 2)
            deadly_hits = [h for h in hits if getattr(h, "is_deadly", True)]
            
            if deadly_hits:
                if self.player.has_shield:
                    self.player.has_shield = False
                    self.player.shield_expire_time = 0
                    self.audio.play_explosion()
                    # Laser không bị mất khi chạm shield, nhưng shield bảo vệ được 1 lần
                else:
                    self.audio.play_explosion()
                    self.game_over = True


    def _update_boss_phase(self):
        """Kiểm tra máu Boss để chuyển phase: bay lên + spawn gà con."""
        boss = self._get_alive_boss()
        if not boss:
            return

        # 1/5 HP của Boss 200 là 40.
        phase_threshold = ENEMY_HP_BY_TYPE["boss"] // 5
        
        if self.boss_last_phase_hp - boss.hp >= phase_threshold:
            # Chuyển phase!
            self.boss_last_phase_hp = boss.hp
            
            # 1. Cho Boss quay về giữa màn hình (vị trí ban đầu)
            # Chỉ cần chỉnh target_y, Enemy.update sẽ lo phần trượt lên/xuống
            boss.target_y = self.fleet.boss_initial_y
            # Đưa boss về giữa ngang nếu đang ở xa
            boss.rect.centerx = SCREEN_WIDTH // 2
            
            # 2. Spawn thêm 1 đội hình gà con hỗ trợ NGAY DƯỚI CHÂN Boss
            self.fleet.spawn_reinforcements(boss_rect=boss.rect)
            
            # 3. Phản hồi âm thanh
            self.audio.play_boss_lazer() # Dùng tạm tiếng laser báo hiệu




    # -------------------------------------------------------------------------
    # QUẢN LÝ WAVE / TIẾN TRÌNH GAME
    # -------------------------------------------------------------------------

    def _check_wave_progression(self):
        """
        (Private) Kiểm tra xem đội hình gà đã bị tiêu diệt hết chưa.
        - Nếu hết gà VÀ chưa đến wave cuối → chuyển sang wave mới.
        - Nếu đã qua wave cuối → chiến thắng.
        """
        if not self.fleet.is_empty():
            return  # Còn gà → chưa cần xét

        if self.wave >= MAX_WAVES and self.game_mode == "story":
            # Đã vượt qua tất cả wave → CHIẾN THẮNG
            self.victory = True
            save_progress(True) # Lưu tiến trình đã hoàn thành story
            self.unlocked_infinite = True # Update cache
        else:
            # Chuyển sang wave tiếp theo
            self._start_next_wave()

    def _start_next_wave(self):
        """(Private) Chuyển sang wave mới."""
        self.wave += 1

        # Xóa các sprite cũ
        self.bullets.empty()
        self.eggs.empty()
        self.powerups.empty()
        self.lasers.empty()

        # Tăng tốc và tạo lại đội hình mới
        self.fleet.increase_speed()
        
        # Logic Infinite Mode: Mỗi 5 wave là Boss, còn lại random
        if self.game_mode == "infinite":
            if self.wave % 5 == 0:
                self.fleet.wave = MAX_WAVES # Giả định MAX_WAVES là wave Boss
            else:
                # Random wave từ 1 đến MAX_WAVES-1
                self.fleet.wave = random.randint(1, MAX_WAVES - 1)
        else:
            self.fleet.wave = self.wave
            
        self.fleet.reset()

    # -------------------------------------------------------------------------
    # KHỞI ĐỘNG LẠI GAME
    # -------------------------------------------------------------------------

    def _restart(self):
        """(Private) Reset toàn bộ trạng thái về ban đầu để chơi lại."""
        # Reset trạng thái
        self.score     = 0
        self.lives     = 3
        self.wave      = 1
        self.game_over = False
        self.victory   = False

        # Xóa sạch tất cả sprite
        self.all_sprites.empty()
        self.enemies.empty()
        self.bullets.empty()
        self.eggs.empty()
        self.powerups.empty()
        self.lasers.empty()


        # Tạo lại Player
        self.player = Player()
        self.all_sprites.add(self.player)

        # Tạo lại đội hình gà với tốc độ mặc định
        self.fleet = EnemyFleet(self.all_sprites, self.enemies, self.eggs, self.wave)
        self.fleet.speed_x = ENEMY_SPEED_X

    # -------------------------------------------------------------------------
    # RENDER / VẼ LÊN MÀN HÌNH
    # -------------------------------------------------------------------------

    def _draw(self):
        """Vẽ toàn bộ frame hiện tại lên màn hình tùy theo state."""
        if self.state == STATE_MENU:
            self.ui_menu.draw(self.screen)
        elif self.state == STATE_PLAY_MODE:
            self.ui_play_mode.draw(self.screen, is_unlocked=self.unlocked_infinite)
        elif self.state == STATE_LEADERBOARD:
            self.ui_leaderboard.draw(self.screen, scores=get_top_scores())
        elif self.state == STATE_SETTINGS:
            self.ui_settings.draw(self.screen, 
                                  sfx_on=self.audio.sfx_enabled, 
                                  music_on=self.audio.music_enabled)
        elif self.state == STATE_PLAYING:
            self._draw_gameplay()

        pygame.display.flip()

    def _draw_gameplay(self):
        """Vẽ màn hình khi đang chơi."""
        self.screen.fill(COLOR_BLACK)
        self._draw_starfield()
        self.all_sprites.draw(self.screen)
        
        # HUD từ ui.py
        self.ui_hud.draw(self.screen, self.score, self.lives, self.wave)
        self._draw_powerup_status()

        # Thanh máu boss: chỉ hiển thị khi boss còn sống trên màn hình.
        boss = self._get_alive_boss()
        if boss is not None:
            self._draw_boss_hp_bar(boss)

        if self.game_over:
            self._draw_game_over_screen()
        elif self.victory:
            self._draw_victory_screen()

    def _draw_starfield(self):
        """
        (Private) Vẽ các chấm trắng nhỏ giả lập nền sao vũ trụ.
        Dùng seed cố định để các ngôi sao không nhảy lung tung mỗi frame.
        """
        rng = random.Random(42)  # Seed cố định → cùng vị trí mỗi frame
        for _ in range(80):
            x = rng.randint(0, SCREEN_WIDTH)
            y = rng.randint(0, SCREEN_HEIGHT)
            brightness = rng.randint(80, 200)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), 1)

    def _draw_hud(self):
        """
        (Private) Vẽ giao diện thông tin (HUD) lên góc màn hình:
        - Góc trên trái: Điểm số.
        - Góc trên phải: Số Wave hiện tại.
        - Cạnh dưới: Đường kẻ phân cách vùng Player.
        """
        # Điểm số (góc trên trái)
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (15, 10))

        # Wave (góc trên phải)
        wave_text = self.font_medium.render(f"WAVE: {self.wave}/{MAX_WAVES}", True, COLOR_ORANGE)
        self.screen.blit(wave_text, (SCREEN_WIDTH - 160, 10))

        # Thanh máu boss: chỉ hiển thị khi boss còn sống trên màn hình.
        boss = self._get_alive_boss()
        if boss is not None:
            self._draw_boss_hp_bar(boss)

        # Đường kẻ ngang ở đáy phân cách vùng an toàn Player
        pygame.draw.line(
            self.screen, (40, 40, 60),
            (0, SCREEN_HEIGHT - 60),
            (SCREEN_WIDTH, SCREEN_HEIGHT - 60),
            1
        )

    def _get_alive_boss(self):
        """
        (Private) Trả về enemy boss còn sống, hoặc None nếu không có.
        """
        for enemy in self.enemies:
            if getattr(enemy, "enemy_type", "") == "boss":
                return enemy
        return None

    def _draw_boss_hp_bar(self, boss):
        """
        (Private) Vẽ thanh máu của boss ở phía trên màn hình.
        """
        bar_width = 320
        bar_height = 16
        x = (SCREEN_WIDTH - bar_width) // 2
        y = 46

        # Viền + nền thanh máu
        pygame.draw.rect(self.screen, COLOR_WHITE, (x - 2, y - 2, bar_width + 4, bar_height + 4), 1)
        pygame.draw.rect(self.screen, (45, 45, 60), (x, y, bar_width, bar_height))

        hp_ratio = max(0.0, min(1.0, boss.hp / max(1, boss.max_hp)))
        fill_width = int(bar_width * hp_ratio)
        fill_color = (220, 60, 60) if hp_ratio < 0.35 else (255, 170, 40)
        pygame.draw.rect(self.screen, fill_color, (x, y, fill_width, bar_height))

        boss_text = self.font_small.render(f"BOSS HP: {boss.hp}/{boss.max_hp}", True, COLOR_WHITE)
        self.screen.blit(boss_text, (x + (bar_width - boss_text.get_width()) // 2, y - 22))

    def _draw_powerup_status(self):
        """
        Vẽ danh sách các power-up đang hoạt động và thời gian còn lại ở góc dưới trái.
        """
        now = pygame.time.get_ticks()
        active_powerups = []
        
        # Kiểm tra các loại buff
        if self.player.pierce_expire_time > now:
            active_powerups.append(("pierce", self.player.pierce_expire_time))
        if self.player.triple_shot_expire_time > now:
            active_powerups.append(("triple_shot", self.player.triple_shot_expire_time))
        if self.player.double_shot_expire_time > now:
            active_powerups.append(("double_shot", self.player.double_shot_expire_time))
        if self.player.rapid_fire_expire_time > now:
            active_powerups.append(("rapid_fire", self.player.rapid_fire_expire_time))
        if self.player.shield_expire_time > now:
            active_powerups.append(("shield", self.player.shield_expire_time))
        if self.player.cursed_expire_time > now:
            active_powerups.append(("cursed", self.player.cursed_expire_time))
            
        if not active_powerups:
            return

        # Vị trí bắt đầu vẽ (góc dưới trái)
        x = 20
        y = SCREEN_HEIGHT - 45
        
        # Mapping tên hiển thị cho người dùng
        powerup_names = {
            "pierce":      "Pierce",
            "triple_shot": "Triple",
            "double_shot": "Double",
            "rapid_fire":  "Rapid",
            "shield":      "Shield",
            "cursed":      "Cursed"
        }
        
        for p_type, expire_time in active_powerups:
            if p_type in self.powerup_icons:
                icon = self.powerup_icons[p_type]
                self.screen.blit(icon, (x, y))
                
                # Hiển thị tên + thời gian
                name = powerup_names.get(p_type, "")
                remaining = (expire_time - now) / 1000
                status_text = f"{name}: {remaining:.1f}s"
                
                text_surf = self.font_small.render(status_text, True, COLOR_WHITE)
                self.screen.blit(text_surf, (x + 35, y + 5))
                
                x += 150  # Tăng khoảng cách vì có thêm tên



    def _draw_game_over_screen(self):
        """
        (Private) Vẽ màn hình Game Over bán trong suốt với điểm số cuối.
        """
        # Lớp phủ bán trong suốt màu đen đỏ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Chữ GAME OVER
        go_text = self.font_large.render("GAME OVER", True, COLOR_RED)
        self.screen.blit(go_text, (
            SCREEN_WIDTH // 2 - go_text.get_width() // 2,
            SCREEN_HEIGHT // 2 - 60
        ))

        # Điểm số cuối
        score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (
            SCREEN_WIDTH // 2 - score_text.get_width() // 2,
            SCREEN_HEIGHT // 2
        ))

        # Nút Chơi lại và Thoát
        ui.draw_button(self.screen, "RESTART [R]", self.btn_restart, COLOR_GREEN, COLOR_BLACK)
        ui.draw_button(self.screen, "QUIT [ESC]", self.btn_quit_game, COLOR_RED, COLOR_WHITE)

    def _draw_victory_screen(self):
        """
        (Private) Vẽ màn hình chiến thắng khi người chơi qua hết tất cả wave.
        """
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        # Chữ CHIẾN THẮNG
        win_text = self.font_large.render("CHIEN THANG!", True, COLOR_GREEN)
        self.screen.blit(win_text, (
            SCREEN_WIDTH // 2 - win_text.get_width() // 2,
            SCREEN_HEIGHT // 2 - 60
        ))

        # Điểm số
        score_text = self.font_medium.render(f"Total Score: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (
            SCREEN_WIDTH // 2 - score_text.get_width() // 2,
            SCREEN_HEIGHT // 2
        ))

        # Nút Chơi lại và Thoát
        ui.draw_button(self.screen, "RESTART [R]", self.btn_restart, COLOR_GREEN, COLOR_BLACK)
        ui.draw_button(self.screen, "QUIT [ESC]", self.btn_quit_game, COLOR_RED, COLOR_WHITE)