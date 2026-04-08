# 🐔 Chicken Invaders — Team Project

## 🚀 Cài đặt & Chạy game

```bash
pip install pygame
python main.py
```

## 🕹️ Điều khiển

| Phím | Hành động |
|------|-----------|
| `← →` | Di chuyển máy bay |
| `SPACE` | Bắn đạn |
| `R` | Chơi lại (sau Game Over / Win) |
| `ESC` | Thoát game |

---

## 📁 Cấu trúc Project (Chuẩn chính thức)

```
chicken_invaders/
├── main.py            ← File chạy game (entry point)
├── game_logic.py      ← Vòng lặp game, va chạm, state machine
├── settings.py        ← Chứa TẤT CẢ thông số: màu sắc, tốc độ, size màn hình...
├── sprites.py         ← Class Player, Enemy, Bullet, Egg, PowerUp...
├── levels.py          ← [TẠO MỚI] Data tọa độ đội hình theo từng Wave
├── ui.py              ← [TẠO MỚI] Class vẽ giao diện (Menu, HUD, Leaderboard)
├── backend.py         ← [TẠO MỚI] Xử lý file điểm số (lưu/đọc)
├── README.md
└── assets/            ← [TẠO MỚI] Thư mục chứa tài nguyên
    ├── images/        ← Ảnh gà, máy bay, background, icon...
    └── audio/         ← Nhạc nền, tiếng súng, tiếng nổ...
```

> ⚠️ **Quy tắc bắt buộc:** Mọi tài nguyên (ảnh, âm thanh) phải đặt đúng trong `assets/images/` hoặc `assets/audio/`. Tuyệt đối không để file rải rác ở thư mục gốc.

---

## 👥 Phân công nhiệm vụ chi tiết

### 👨‍💻 Dev 1 — Animation (Gà & Máy bay)
**File làm việc:** `sprites.py` và `assets/images/`

**Nhiệm vụ:**
- Tìm/cắt sprite sheet cho Player và Enemy
- Load mảng ảnh vào class `Player` và `Enemy`
- Dùng `pygame.time.get_ticks()` để xử lý chuyển frame animation (vỗ cánh, xịt lửa) mà không làm đứng game

> ⚠️ **GIỚI HẠN SCOPE:** Chỉ thay đổi cách hiển thị hình ảnh (`self.image`). **Tuyệt đối không** đụng vào `self.rect` hay logic di chuyển trong `update()`.

---

### 👨‍💻 Dev 2 — Kiến trúc sư Level (Đội hình bay)
**File làm việc:** Tạo mới `levels.py`

**Nhiệm vụ:**
- Thiết kế tọa độ xuất hiện của gà theo từng Wave
- Viết hàm `get_wave_pattern(wave_num)` trả về danh sách tọa độ `(X, Y)` với nhiều hình khối: chữ V, hình tròn, zig-zag...

**Ví dụ interface:**
```python
# levels.py
def get_wave_pattern(wave_num: int) -> list[tuple[int, int]]:
    """Trả về list tọa độ (x, y) của từng con gà trong wave."""
    ...
```

> ⚠️ **GIỚI HẠN SCOPE:** File này thuần chứa **data và thuật toán sinh tọa độ**. Không viết bất kỳ logic Pygame hay lệnh `draw` nào ở đây.

---

### 👨‍💻 Dev 3 — Tính năng Boost / Power-ups
**File làm việc:** `sprites.py` và `assets/images/`

**Nhiệm vụ:**
- Code thêm class `PowerUp` kế thừa `pygame.sprite.Sprite`
- Thiết kế logic để boost thỉnh thoảng rơi từ trên xuống (tương tự class `Egg`)
- Xử lý animation và chuyển động rơi của viên boost

> ⚠️ **GIỚI HẠN SCOPE:** Chỉ code **sự di chuyển** của object PowerUp. Không viết logic va chạm (xử lý khi Player nhặt được boost — phần đó Leader ghép vào `game_logic.py`).

---

### 👨‍💻 Dev 4 — Họa sĩ UI/UX (Giao diện & Màn hình)
**File làm việc:** Tạo mới `ui.py`

**Nhiệm vụ:**
- Thiết kế và code các màn hình: **Menu chính**, **Leaderboard**, **Settings**
- Căn chỉnh font chữ, nút bấm, layout tổng thể
- Dùng **mock data** (dữ liệu giả) để dựng sẵn màn hình Leaderboard — Dev 5 sẽ cắm data thật vào sau

**Ví dụ interface cần expose:**
```python
# ui.py
class MainMenuScreen:
    def draw(self, surface): ...

class LeaderboardScreen:
    def draw(self, surface, scores: list[tuple[str, int]]): ...
    # scores = [("PlayerName", 9999), ...] — Dev 5 sẽ cung cấp list này
```

> ⚠️ **GIỚI HẠN SCOPE:** Mọi mã màu và kích thước font **phải kéo từ `settings.py`**. Không hardcode giá trị cứng (`#FF0000`, `36`...) trực tiếp vào `ui.py`.

---

### 👨‍💻 Dev 5 — Backend & Audio
**File làm việc:** Tạo mới `backend.py` và `assets/audio/`

**Nhiệm vụ:**
- Chuẩn bị và tổ chức file âm thanh (nhạc nền, tiếng súng, tiếng nổ...)
- Viết logic lưu trữ/đọc điểm cao bằng JSON hoặc SQLite

**Bắt buộc phải có 2 hàm public sau** (Dev 4 phụ thuộc vào đây):
```python
# backend.py

def save_score(name: str, score: int) -> None:
    """Lưu điểm của người chơi vào file/database."""
    ...

def get_top_scores(limit: int = 10) -> list[tuple[str, int]]:
    """Trả về danh sách top điểm cao, sắp xếp giảm dần.
    Ví dụ: [("Alice", 9500), ("Bob", 7200), ...]
    """
    ...
```

> ⚠️ **GIỚI HẠN SCOPE:** Chỉ xử lý I/O file và âm thanh. Logic game (tính điểm, khi nào gọi save) do Leader quản lý trong `game_logic.py`.

---

## 🔗 Sơ đồ phụ thuộc giữa các module

```
settings.py  ←── được import bởi TẤT CẢ các file khác
     │
     ├── sprites.py    (Player, Enemy, Bullet, PowerUp)
     │        ↑
     ├── levels.py     (get_wave_pattern)  →  dữ liệu đầu vào cho EnemyFleet
     │
     ├── backend.py    (save_score, get_top_scores)
     │        ↓
     ├── ui.py         (MainMenuScreen, LeaderboardScreen)  ←  nhận data từ backend
     │
     └── game_logic.py  ←── TRUNG TÂM, import và kết nối tất cả
              ↑
          main.py  (chỉ gọi Game().run())
```

---

## 🔧 Snippets hữu ích

### Load ảnh thật thay placeholder
```python
# Trong sprites.py → Player.__init__()
self.image = pygame.image.load("assets/images/player.png").convert_alpha()
self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
```

### Animation vỗ cánh (Dev 1)
```python
# Trong Enemy.__init__()
self.frames = [load frame 1, load frame 2, ...]
self.frame_index = 0
self.last_frame_time = 0

# Trong Enemy.update()
now = pygame.time.get_ticks()
if now - self.last_frame_time > 120:  # đổi frame mỗi 120ms
    self.last_frame_time = now
    self.frame_index = (self.frame_index + 1) % len(self.frames)
    self.image = self.frames[self.frame_index]
```

### Thêm âm thanh (Dev 5)
```python
# Trong backend.py hoặc main.py
pygame.mixer.init()
shoot_sfx = pygame.mixer.Sound("assets/audio/shoot.wav")
shoot_sfx.play()  # Gọi trong Player.handle_shoot()
```

### Thêm Lives (Leader ghép)
```python
# settings.py
PLAYER_LIVES = 3

# game_logic.py → Game.__init__()
self.lives = PLAYER_LIVES
```