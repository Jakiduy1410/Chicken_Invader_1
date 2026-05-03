import json
import os
import pygame

# --- CẤU HÌNH ---
DATA_FOLDER = "data"
SCORE_FILE = os.path.join(DATA_FOLDER, "high_scores.json")
PROGRESS_FILE = os.path.join(DATA_FOLDER, "progress.json")
AUDIO_FOLDER = "assets/audio"

# Tự động tạo thư mục nếu chưa có
for folder in [DATA_FOLDER, AUDIO_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- LOGIC LƯU TRỮ ĐIỂM ---
def save_score(name: str, score: int) -> None:
    """Lưu điểm vào file JSON."""
    scores = _load_raw_data()
    scores.append({"name": name, "score": score})
    
    def get_sort_value(x):
        val = x.get('score', 0)
        if isinstance(val, int):
            return val
        # Nếu là string như "100kg", thử lấy số ra
        import re
        nums = re.findall(r'\d+', str(val))
        if nums:
            return int(nums[0])
        return 0

    scores.sort(key=get_sort_value, reverse=True)
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

# --- LOGIC TIẾN TRÌNH ---
def save_progress(story_finished: bool = True) -> None:
    """Lưu trạng thái hoàn thành Story Mode."""
    data = {"story_finished": story_finished}
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def is_story_finished() -> bool:
    """Kiểm tra xem Story Mode đã hoàn thành chưa."""
    if not os.path.exists(PROGRESS_FILE):
        return False
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("story_finished", False)
    except:
        return False

# --- QUẢN LÝ ÂM THANH ---
class AudioManager:
    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        self.sfx = {}
        self.sfx_enabled = True
        self.music_enabled = True

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
        if not self.music_enabled:
            return
        pygame.mixer.music.set_volume(0.2) 
        pygame.mixer.music.play(-1)
        
    def stop_bgm(self):
        """Dừng nhạc nền."""
        pygame.mixer.music.stop()

    def play_shoot(self):
        """Phát tiếng súng bắn."""
        if self.sfx_enabled and "shoot" in self.sfx:
            self.sfx["shoot"].play()

    def play_explosion(self):
        """Phát tiếng nổ."""
        if self.sfx_enabled and "explosion" in self.sfx:
            self.sfx["explosion"].play()
    
    def play_chicken_exp(self): 
        """Phát tiếng gà bị bắn nổ."""
        if self.sfx_enabled and "chicken_exp" in self.sfx:
            self.sfx["chicken_exp"].play()
    
    def play_boss_lazer(self): 
        """Phát tiếng boss lazer."""
        if self.sfx_enabled and "boss_lazer" in self.sfx:
            self.sfx["boss_lazer"].play()

    def toggle_sfx(self):
        self.sfx_enabled = not self.sfx_enabled
        return self.sfx_enabled

    def toggle_music(self):
        self.music_enabled = not self.music_enabled
        if self.music_enabled:
            self.play_bgm()
        else:
            self.stop_bgm()
        return self.music_enabled
            
        
if __name__ == "__main__":
    # Khởi tạo pygame để test âm thanh
    pygame.init() 
    
    audio = AudioManager()
    audio.load_resources()
    
    print("Đang test nhạc nổ...")
    audio.play_boss_lazer()
    
    # Giữ chương trình chạy trong 5 giây để nghe nhạc
    pygame.time.delay(5000)