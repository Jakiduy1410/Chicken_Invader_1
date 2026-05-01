from collections import deque
from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = Path(
    r"C:\Users\HP\.cursor\projects\c-Users-HP-Downloads-Chicken-Invader-1-main-Chicken-Invader-1-main\assets"
)

# Map: output sheet name -> source image file + crop boxes of 2 poses.
CROP_PLAN = {
    "chick_1_sheet.png": {
        "file": "c__Users_HP_AppData_Roaming_Cursor_User_workspaceStorage_aaf2d6d724e41a022d34f7894805d8d8_images_image-a443d3fb-bcd4-432a-b784-30b80d4dbc92.png",
        "poses": [(120, 15, 300, 176), (305, 15, 530, 176)],
    },
    "chick_2_sheet.png": {
        "file": "c__Users_HP_AppData_Roaming_Cursor_User_workspaceStorage_aaf2d6d724e41a022d34f7894805d8d8_images_image-e1a6c412-a250-431b-935f-54b1ab4ea8bf.png",
        "poses": [(110, 15, 305, 184), (310, 15, 535, 184)],
    },
    "chick_3_sheet.png": {
        "file": "c__Users_HP_AppData_Roaming_Cursor_User_workspaceStorage_aaf2d6d724e41a022d34f7894805d8d8_images_image-0a0c7075-5660-457f-860c-079573a35dec.png",
        "poses": [(55, 35, 250, 202), (260, 35, 480, 202)],
    },
    "chick_4_sheet.png": {
        "file": "c__Users_HP_AppData_Roaming_Cursor_User_workspaceStorage_aaf2d6d724e41a022d34f7894805d8d8_images_image-55fdb6c1-e6b1-4466-91ff-eccb5b12e33f.png",
        "poses": [(40, 15, 215, 176), (225, 15, 460, 176)],
    },
    "boss_sheet.png": {
        "file": "c__Users_HP_AppData_Roaming_Cursor_User_workspaceStorage_aaf2d6d724e41a022d34f7894805d8d8_images_image-7c2b38cd-0020-44a7-8b7d-548cfc7b357a.png",
        "poses": [(65, 20, 305, 210), (315, 20, 545, 210)],
    },
}


def remove_bg_from_corners(img: Image.Image, tolerance=28) -> Image.Image:
    """Flood-fill transparency from 4 corners to remove blue-sky background."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    visited = set()
    queue = deque([(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)])

    def close(c1, c2):
        return all(abs(a - b) <= tolerance for a, b in zip(c1[:3], c2[:3]))

    seeds = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        cur = px[x, y]
        if cur[3] == 0:
            continue
        if not any(close(cur, s) for s in seeds):
            continue
        px[x, y] = (cur[0], cur[1], cur[2], 0)
        if x > 0:
            queue.append((x - 1, y))
        if x < w - 1:
            queue.append((x + 1, y))
        if y > 0:
            queue.append((x, y - 1))
        if y < h - 1:
            queue.append((x, y + 1))
    return img


def trim_to_alpha(img: Image.Image, pad=8) -> Image.Image:
    bbox = img.getbbox()
    if not bbox:
        return img
    x0, y0, x1, y1 = bbox
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(img.size[0], x1 + pad)
    y1 = min(img.size[1], y1 + pad)
    return img.crop((x0, y0, x1, y1))


def crop_pose(src: Image.Image, box, out_size=(40, 40)) -> Image.Image:
    pose = src.crop(box)
    pose = remove_bg_from_corners(pose, tolerance=30)
    pose = trim_to_alpha(pose, pad=6)
    return pose.resize(out_size, Image.Resampling.LANCZOS)


def remove_dark_background(img: Image.Image, threshold=30) -> Image.Image:
    """Convert near-black pixels to transparent for the player source image."""
    img = img.convert("RGBA")
    px = img.load()
    w, h = img.size
    for x in range(w):
        for y in range(h):
            r, g, b, a = px[x, y]
            if a == 0:
                continue
            if r <= threshold and g <= threshold and b <= threshold:
                px[x, y] = (r, g, b, 0)
    return img


def save_sheet(name: str, frames):
    sheet = Image.new("RGBA", (120, 40), (0, 0, 0, 0))
    for i, fr in enumerate(frames[:3]):
        sheet.paste(fr, (i * 40, 0), fr)
    sheet.save(ROOT / name)


def make_player_sheet():
    src_path = SOURCE_DIR / (
        "c__Users_HP_AppData_Roaming_Cursor_User_workspaceStorage_aaf2d6d724e41a022d34f7894805d8d8_images_image-7203f46d-146a-4f39-9a49-48a3bccebca9.png"
    )
    src = Image.open(src_path).convert("RGBA")
    ship = src.crop((66, 52, 122, 182))
    ship = remove_dark_background(ship, threshold=30)
    ship = trim_to_alpha(ship, pad=4).resize((50, 40), Image.Resampling.LANCZOS)

    sheet = Image.new("RGBA", (150, 40), (0, 0, 0, 0))
    for i in range(3):
        sheet.paste(ship, (i * 50, 0), ship)
    sheet.save(ROOT / "player_sheet.png")


def main():
    for out_name, cfg in CROP_PLAN.items():
        src_path = SOURCE_DIR / cfg["file"]
        src = Image.open(src_path).convert("RGBA")
        pose_a = crop_pose(src, cfg["poses"][0])
        pose_b = crop_pose(src, cfg["poses"][1])
        save_sheet(out_name, [pose_a, pose_b, pose_a])

    make_player_sheet()
    print("Done: regenerated 4 chicken sheets, boss sheet, and player sheet.")


if __name__ == "__main__":
    main()
