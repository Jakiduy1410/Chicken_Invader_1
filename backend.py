import json
import os
import pygame

# --- CẤU HÌNH ---
SCORE_FILE = "high_scores.json"
AUDIO_FOLDER = "assets/audio"

# Tự động tạo thư mục nếu chưa có
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

# --- LOGIC LƯU TRỮ ĐIỂM ---
def save_score(name: str, score: int) -> None:
    """Lưu điểm vào file JSON."""
    scores = _load_raw_data()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x['score'], reverse=True)
    with open(SCORE_FILE, "w", encoding="utf-8") as f:
        json.dump(scores, f, ensure_ascii=False, indent=4)
    print(f"✅ Đã lưu điểm cho {name}")

def get_top_scores(limit: int = 10) -> list[tuple[str, int]]:
    """Trả về top điểm cao cho Dev 4."""
    scores = _load_raw_data()
    return [(item['name'], item['score']) for item in scores[:limit]]

def _load_raw_data():
    if not os.path.exists(SCORE_FILE): return []
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except: return []

# --- QUẢN LÝ ÂM THANH ---
class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.sfx = {}

    def load_resources(self):
        """Tải các tệp âm thanh. Mỗi tệp được tải riêng để tránh lỗi nếu thiếu 1 file."""
        sounds_to_load = {
            "shoot": "shoot.mp3",
            "explosion": "explosion.mp3",
            "chicken_exp": "chicken_exp.mp3",
            "boss_lazer": "boss_lazer.mp3"
        }
        
        for key, filename in sounds_to_load.items():
            path = os.path.join(AUDIO_FOLDER, filename)
            if os.path.exists(path):
                try:
                    self.sfx[key] = pygame.mixer.Sound(path)
                    # print(f"✅ Đã tải: {filename}")
                except Exception as e:
                    print(f"❌ Lỗi khi tải {filename}: {e}")
            else:
                # print(f"⚠️ Không tìm thấy: {filename}")
                pass
        
        # Load nhạc nền (Music)
        bgm_path = os.path.join(AUDIO_FOLDER, "background.mp3")
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
            except:
                pass


    def play_bgm(self):
        """Phát nhạc nền lặp lại vô tận với âm lượng nhỏ hơn."""
        # Giá trị từ 0.0 (tắt tiếng) đến 1.0 (âm lượng tối đa)
        # 0.2 nghĩa là chỉ bằng 20% âm lượng gốc
        pygame.mixer.music.set_volume(0.2) 
        pygame.mixer.music.play(-1)
        
    def play_shoot(self):
        """Phát tiếng súng bắn."""
        if "shoot" in self.sfx:
            self.sfx["shoot"].play()

    def play_explosion(self):
        """Phát tiếng nổ."""
        if "explosion" in self.sfx:
            self.sfx["explosion"].play()
    
    def play_chicken_exp(self): 
        """Phát tiếng gà bị bắn nổ."""
        if "chicken_exp" in self.sfx:
            self.sfx["chicken_exp"].play()
    
    def play_boss_lazer(self): 
        """Phát tiếng gà bị bắn nổ."""
        if "boss_lazer" in self.sfx:
            self.sfx["boss_lazer"].play()
            
        
if __name__ == "__main__":
    # Khởi tạo pygame để test âm thanh
    pygame.init() 
    
    audio = AudioManager()
    audio.load_resources()
    
    print("Đang test nhạc nổ...")
    audio.play_boss_lazer()
    
    # Giữ chương trình chạy trong 5 giây để nghe nhạc
    pygame.time.delay(5000)