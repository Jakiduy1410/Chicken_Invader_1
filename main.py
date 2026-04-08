# =============================================================================
# FILE: main.py
# MÔ TẢ: Entry point — file duy nhất cần chạy để khởi động game.
#         Đây là file "cổng vào" đơn giản nhất có thể.
#         Toàn bộ logic đã được đóng gói trong game_logic.py.
#
# CÁCH CHẠY:
#     Cài đặt Pygame: pip install pygame
#     Chạy game:     python main.py
#
# ĐIỀU KHIỂN:
#     ← → (Mũi tên trái/phải) : Di chuyển máy bay
#     SPACE                    : Bắn đạn
#     R                        : Chơi lại (sau Game Over / Win)
#     ESC                      : Thoát game
# =============================================================================

from game_logic import Game


def main():
    """
    Hàm main: Tạo đối tượng Game và bắt đầu vòng lặp.
    Toàn bộ logic (khởi tạo Pygame, xử lý sự kiện, render...)
    đều nằm bên trong class Game — main.py chỉ là điểm kích hoạt.
    """
    game = Game()
    game.run()


# Chỉ chạy main() khi file này được gọi trực tiếp
# (Không chạy nếu file này được import bởi module khác)
if __name__ == "__main__":
    main()
