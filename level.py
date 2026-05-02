# =============================================================================
# FILE: levels.py
# MÔ TẢ: Dữ liệu và thuật toán sinh tọa độ (x, y) — tâm sprite — cho đàn gà
#         theo từng Wave. Không chứa Pygame hay lệnh vẽ.
#
# Wave 1: zig-zag  |  Wave 2: tam giác  |  Wave 3: hình thoi
# Wave 4: trái tim   |  Wave 5: không gà con (boss — game_logic)
# =============================================================================

from __future__ import annotations

import math

from settings import (
    ENEMY_COLS,
    ENEMY_GRID_TOP,
    ENEMY_HEIGHT,
    ENEMY_H_SPACING,
    ENEMY_ROWS,
    ENEMY_V_SPACING,
    ENEMY_WIDTH,
    MAX_WAVES,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
)


def _margin_x() -> int:
    return max(ENEMY_WIDTH // 2 + 8, 40)


def _formation_bottom_cap() -> int:
    """Cùng công thức với `_play_y_bounds` — clamp không thu nhỏ đội hình tim/thoi."""
    return min(SCREEN_HEIGHT // 2 + 130, SCREEN_HEIGHT - 85)


def _clamp_xy(x: float, y: float) -> tuple[int, int]:
    mx = _margin_x()
    top = ENEMY_GRID_TOP + ENEMY_WIDTH // 4
    bottom_cap = _formation_bottom_cap()
    cx = int(round(max(mx, min(SCREEN_WIDTH - mx, x))))
    cy = int(round(max(top, min(bottom_cap, y))))
    return cx, cy


def _chick_count() -> int:
    return max(1, ENEMY_ROWS * ENEMY_COLS)


def _min_center_distance() -> float:
    """Khoảng cách tối thiểu giữa tâm hai con gà (tránh chồng sprite ~80px)."""
    return max(float(ENEMY_WIDTH), float(ENEMY_H_SPACING)) * 0.98


def _outline_spacing() -> float:
    """Khoảng cách tâm trên viền tim / thoi — cánh sprite rộng hơn rect, chừa lề rõ."""
    base = max(float(ENEMY_WIDTH), float(ENEMY_HEIGHT), float(ENEMY_H_SPACING))
    return base * 1.38


def _play_y_bounds() -> tuple[float, float, float]:
    mx = _margin_x()
    top = float(ENEMY_GRID_TOP + ENEMY_WIDTH // 4)
    bottom_cap = float(_formation_bottom_cap())
    return top, bottom_cap, float(mx)


def _pattern_zigzag(count: int) -> list[tuple[int, int]]:
    """Wave 1 — lưới so le; khoảng cách giãn rõ so với lưới mặc định."""
    cols = max(1, ENEMY_COLS)
    rows = max(1, math.ceil(count / cols))
    h_space = int(round(ENEMY_H_SPACING * 1.24))
    v_space = int(round(ENEMY_V_SPACING * 1.14))
    total_w = (cols - 1) * h_space
    x0 = (SCREEN_WIDTH - total_w) // 2
    y0 = ENEMY_GRID_TOP + 18
    shift = h_space // 2
    out: list[tuple[int, int]] = []
    for r in range(rows):
        row_off = shift if r % 2 else 0
        for c in range(cols):
            if len(out) >= count:
                return out
            x = x0 + c * h_space + row_off
            y = y0 + r * v_space
            out.append(_clamp_xy(x, y))
    return out[:count]


def _pattern_triangle(count: int) -> list[tuple[int, int]]:
    """Wave 2 — tam giác cân; hàng rộng dần, bước hơi giãn để không sát."""
    out: list[tuple[int, int]] = []
    remaining = count
    row = 0
    y0 = ENEMY_GRID_TOP + 28
    h_step = int(round(ENEMY_H_SPACING * 1.16))
    v_step = int(round(ENEMY_V_SPACING * 1.10))

    while remaining > 0:
        n_in_row = row + 1
        if remaining < n_in_row:
            n_in_row = remaining
        y = y0 + row * v_step
        total_w = (n_in_row - 1) * h_step if n_in_row > 1 else 0
        x0 = SCREEN_WIDTH // 2 - total_w // 2
        for c in range(n_in_row):
            x = x0 + c * h_step
            out.append(_clamp_xy(x, y))
        remaining -= n_in_row
        row += 1

    return out[:count]


def _heart_xy(t: float) -> tuple[float, float]:
    """Đường cong trái tim cổ điển (tham số t ∈ [0, 2π]). Trục y toán học hướng lên."""
    st = math.sin(t)
    x = 16.0 * st**3
    y = (
        13.0 * math.cos(t)
        - 5.0 * math.cos(2.0 * t)
        - 2.0 * math.cos(3.0 * t)
        - math.cos(4.0 * t)
    )
    return x, y


def _heart_dense_polyline(
    cx: float, cy: float, scale: float, segments: int = 640
) -> tuple[list[tuple[float, float]], float]:
    """Polyline mịn dọc trái tim; tổng độ dài theo pixel (đã scale)."""
    pts: list[tuple[float, float]] = []
    for i in range(segments + 1):
        t = (2.0 * math.pi * i) / segments
        hx, hy = _heart_xy(t)
        pts.append((cx + scale * hx, cy - scale * hy))
    total = 0.0
    for i in range(1, len(pts)):
        total += math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
    return pts, total


def _sample_polyline_arc_length(
    pts: list[tuple[float, float]], n: int
) -> list[tuple[float, float]]:
    """Lấy n điểm cách đều theo độ dài cung dọc polyline (điểm đầu/cuối trùng → bỏ cạnh đóng)."""
    if n < 1:
        return []
    if len(pts) < 2:
        return [pts[0]] * n

    cum: list[float] = [0.0]
    for i in range(1, len(pts)):
        cum.append(
            cum[-1]
            + math.hypot(pts[i][0] - pts[i - 1][0], pts[i][1] - pts[i - 1][1])
        )
    total = cum[-1]
    if total < 1e-6:
        return [pts[0]] * n

    out: list[tuple[float, float]] = []
    for k in range(n):
        d = (k / n) * total
        lo, hi = 0, len(cum) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if cum[mid] <= d:
                lo = mid
            else:
                hi = mid - 1
        i = lo
        if i >= len(pts) - 1:
            out.append(pts[-1])
            continue
        seg = cum[i + 1] - cum[i]
        t = 0.0 if seg < 1e-9 else (d - cum[i]) / seg
        t = max(0.0, min(1.0, t))
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        out.append((x0 + t * (x1 - x0), y0 + t * (y1 - y0)))
    return out


def _pattern_heart(count: int) -> list[tuple[int, int]]:
    """Wave 3 — 1 Trái tim xếp theo grid (đã ép size)."""
    
    # <-- CHÚ THÍCH: Gọt đỉnh xuống còn 2 '##' và bóp lại form cho cân đối
    heart_map = [
        "  ##   ##  ",
        " #### #### ",
        "###########",
        "###########",
        " ######### ",
        "  #######  ",
        "   #####   ",
        "    ###    ",
        "     #     "
    ]
    
    out: list[tuple[int, int]] = []
    rows = len(heart_map)
    cols = len(heart_map[0])
    
    h_space = int(round(ENEMY_H_SPACING * 1.0)) 
    v_space = int(round(ENEMY_V_SPACING * 1.0))
    
    total_w = (cols - 1) * h_space
    x0 = (SCREEN_WIDTH - total_w) // 2
    
    top, bottom_cap, _ = _play_y_bounds()
    total_h = (rows - 1) * v_space
    y0 = top + (bottom_cap - top - total_h) // 3 
    
    for r, row_str in enumerate(heart_map):
        for c, char in enumerate(row_str):
            if char == '#':
                x = x0 + c * h_space
                y = y0 + r * v_space
                out.append(_clamp_xy(x, y))
                
    return out
    
def _even_on_closed_polygon(
    verts: list[tuple[float, float]], n: int
) -> list[tuple[int, int]]:
    """n điểm cách đều theo chu vi đa giác khép kín (verts theo thứ tự)."""
    m = len(verts)
    if n < 1 or m < 2:
        return []
    lens: list[float] = []
    for i in range(m):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % m]
        lens.append(math.hypot(x1 - x0, y1 - y0))
    total = sum(lens)
    if total < 1e-6:
        return [_clamp_xy(verts[0][0], verts[0][1])] * n

    out: list[tuple[int, int]] = []
    for k in range(n):
        d = (k / n) * total
        acc = 0.0
        for i, L in enumerate(lens):
            if acc + L >= d - 1e-9 or i == len(lens) - 1:
                t = 0.0 if L < 1e-6 else (d - acc) / L
                t = max(0.0, min(1.0, t))
                x0, y0 = verts[i]
                x1, y1 = verts[(i + 1) % m]
                ox = x0 + t * (x1 - x0)
                oy = y0 + t * (y1 - y0)
                out.append(_clamp_xy(ox, oy))
                break
            acc += L
    return out


def _rhombus_fit_to_screen(
    cx: float,
    cy: float,
    edge_len: float,
    aspect: float,
    top: float,
    bottom_cap: float,
    mx: float,
    pad: float,
) -> tuple[float, float]:
    """Trả về (rw, rh) cho thoi cạnh edge_len, thu nhỏ nếu tràn màn."""
    rh = edge_len / math.sqrt(aspect * aspect + 1.0)
    rw = aspect * rh
    max_rw = (SCREEN_WIDTH / 2.0) - mx - pad
    max_rh = min(bottom_cap - cy, cy - top) - pad
    if rw > max_rw or rh > max_rh:
        s = min(max_rw / max(rw, 1e-6), max_rh / max(rh, 1e-6))
        rw *= s
        rh *= s
    return rw, rh


def _pattern_rhombus(count: int) -> list[tuple[int, int]]:
    """Wave 4 — Ba hình thoi: Trái, Phải và một hình nhỏ ở Giữa."""
    if count < 1:
        return []
    
    # Chia gà cho 3 phần: Trái, Phải (~40% mỗi bên), Giữa (~20%)
    c_side = int(count * 0.4)
    c_mid = count - 2 * c_side
    if c_mid < 4: c_mid = 4
    c_side = (count - c_mid) // 2

    top, bottom_cap, mx = _play_y_bounds()
    cy = (top + bottom_cap) / 2.0
    gap = _outline_spacing() * 0.8
    aspect = 1.1
    
    out_pts: list[tuple[int, int]] = []
    
    # --- Hình thoi 1 (bên trái) ---
    cx1 = SCREEN_WIDTH * 0.22
    rw1 = (c_side * gap) / 6.0
    rh1 = rw1 * aspect
    verts1 = [(cx1, cy - rh1), (cx1 + rw1, cy), (cx1, cy + rh1), (cx1 - rw1, cy)]
    out_pts.extend([_clamp_xy(px, py) for px, py in _even_on_closed_polygon(verts1, c_side)])
    
    # --- Hình thoi 2 (bên phải) ---
    cx2 = SCREEN_WIDTH * 0.78
    rw2 = (c_side * gap) / 6.0
    rh2 = rw2 * aspect
    verts2 = [(cx2, cy - rh2), (cx2 + rw2, cy), (cx2, cy + rh2), (cx2 - rw2, cy)]
    out_pts.extend([_clamp_xy(px, py) for px, py in _even_on_closed_polygon(verts2, c_side)])

    # --- Hình thoi 3 (ở giữa - nhỏ hơn) ---
    cxM = SCREEN_WIDTH / 2.0
    rwM = (c_mid * gap) / 6.0
    rhM = rwM * aspect
    vertsM = [(cxM, cy - rhM), (cxM + rwM, cy), (cxM, cy + rhM), (cxM - rwM, cy)]
    out_pts.extend([_clamp_xy(px, py) for px, py in _even_on_closed_polygon(vertsM, c_mid)])
    
    return out_pts


def get_wave_pattern(wave_num: int) -> list[tuple[int, int]]:
    """Trả về list tọa độ (x, y) tâm sprite cho **gà con** trong wave.

    - Wave 1: zig-zag
    - Wave 2: tam giác
    - Wave 3: hình thoi
    - Wave 4: trái tim
    - Wave 5+ (``>= MAX_WAVES``): [] — boss ở ``game_logic``.

    Wave 6+ (nếu mở rộng): lặp lại 1→4.
    """
    if wave_num < 1:
        wave_num = 1

    if wave_num >= MAX_WAVES:
        return []

    n = _chick_count()

    if wave_num == 1:
        return _pattern_zigzag(n)
    if wave_num == 2:
        return _pattern_triangle(n)
    if wave_num == 3:
        return _pattern_rhombus(n)
    if wave_num == 4:
        return _pattern_heart(n)

    m = (wave_num - 1) % 4
    if m == 0:
        return _pattern_zigzag(n)
    if m == 1:
        return _pattern_triangle(n)
    if m == 2:
        return _pattern_rhombus(n)
    return _pattern_heart(n)