# 🚀 Chicken Invaders - Python Team Project

Chào mừng bạn đến với dự án **Chicken Invaders** được xây dựng bằng ngôn ngữ Python và thư viện Pygame. Đây là một bản clone hiện đại với đầy đủ tính năng từ Menu, Bảng xếp hạng đến các chế độ chơi thử thách.

---

## 🎮 Tính năng chính

- **Chế độ Story (Cốt truyện)**: Trải nghiệm 5 màn chơi (Waves) với độ khó tăng dần, kết thúc bằng một trận đấu trùm (Boss) cực kỳ kịch tính.
- **Chế độ Infinite (Vô tận)**: Mở khóa sau khi phá đảo Story Mode. Thử thách bản thân với các đợt tấn công ngẫu nhiên và hệ số điểm tăng dần theo thời gian.
- **Hệ thống Power-ups**:
    - 🛡️ **Shield**: Bảo vệ máy bay khỏi va chạm.
    - 🚀 **Double/Triple Shot**: Tăng số lượng đạn bắn ra.
    - ⚡ **Rapid Fire**: Tăng tốc độ bắn đạn.
    - 💎 **Pierce**: Đạn xuyên thấu, tiêu diệt nhiều kẻ địch cùng lúc.
- **Giao diện hiện đại (UI)**:
    - Menu chính sống động với hiệu ứng Starfield.
    - Bảng xếp hạng (Leaderboard) ghi lại những huyền thoại.
    - Menu cài đặt (Settings) cho phép tùy chỉnh âm thanh và nhạc nền.
- **Âm thanh & Hiệu ứng**: Hệ thống SFX sống động và nhạc nền cực cuốn.

---

## 🛠️ Yêu cầu hệ thống

- **Python**: Phiên bản 3.8 trở lên.
- **Thư viện**: `pygame`.

---

## 📥 Cách cài đặt

1. **Clone project** hoặc tải mã nguồn về máy.
2. **Cài đặt thư viện Pygame**:
   ```powershell
   pip install pygame
   ```
3. **Kiểm tra Assets**: Đảm bảo thư mục `assets/` chứa đầy đủ hình ảnh và âm thanh cần thiết.

---

## 🚀 Cách chơi

1. **Khởi động game**:
   ```powershell
   python main.py
   ```
2. **Điều khiển**:
    - ⌨️ **Mũi tên (Left/Right/Up/Down)**: Di chuyển máy bay.
    - ⌨️ **Dấu cách (SPACE)**: Bắn đạn.
    - ⌨️ **R**: Chơi lại nhanh (khi Game Over/Victory).
    - ⌨️ **ESC**: Quay lại Menu hoặc Thoát game.

---

## 📂 Cấu trúc thư mục

```text
Chicken_Invader/
├── assets/                 # Tài nguyên game (audio, image)
├── data/                   # Dữ liệu người chơi (JSON)
│   ├── high_scores.json    # Bảng xếp hạng
│   └── progress.json       # Tiến trình chơi
├── backend.py              # Xử lý dữ liệu & Âm thanh
├── game_logic.py           # Logic cốt lõi & State Machine
├── level.py                # Định nghĩa các Wave mẫu
├── main.py                 # File thực thi chính
├── settings.py             # Cấu hình hằng số (Speed, Color, HP)
├── sprites.py              # Các lớp đối tượng (Player, Enemy, v.v.)
├── ui.py                   # Thành phần giao diện & Vẽ màn hình
└── README.md               # Hướng dẫn dự án
```

---

## 🏆 Leaderboard Legends

Bảng xếp hạng hiện tại đang được thống trị bởi các huyền thoại:
1. **Bombombuzin** - Điểm số: **∞**
2. **Viet Gay** - Điểm số: **100kg**
3. **Phat Ha Tinh** - Điểm số: **3838**
... và nhiều người chơi khác. Hãy cố gắng ghi tên mình vào bảng vàng!

---

*Chúc bạn chơi game vui vẻ!* 🐔🚀