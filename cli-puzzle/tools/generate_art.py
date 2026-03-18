#!/usr/bin/env python3
"""Generate high-res pixel art scenes for the CLI puzzle game.

New storyline: A programmer gets paged at 3AM and gradually discovers
a supply chain terror attack — and that they themselves are the attacker.

ART_TO_IMAGE mapping:
  title.png          — Title screen: "OFFLINE SIGNAL"
  bedroom.png        — Scene 1: Dark bedroom at 3AM, laptop glow, PagerDuty alert
  prod_server.png    — Scene 2: Production server dashboard, logs, error spikes
  code_review.png    — Scene 3: Git diff view, PR with hidden messages
  supply_chain.png   — Scene 4: Forensics terminal, git log, countdown to 8AM
  the_mirror.png     — Scene 5: The reveal — git blame, glitch, "你终于想起来了吗？"
"""

import random
from PIL import Image, ImageDraw, ImageFilter

OUTPUT_DIR = "../content/scene_images"

# Width/height for all scenes — renders ~200 cols in terminal
W, H = 200, 100

# Color palette - dark cyberpunk/hacker theme
C = {
    "black":        (8, 12, 20),
    "black2":       (12, 16, 26),
    "wall_v_dark":  (14, 22, 34),
    "wall_dark":    (22, 32, 48),
    "wall":         (35, 50, 70),
    "wall_light":   (55, 75, 100),
    "wall_hi":      (70, 90, 115),
    "floor_v_dark": (18, 25, 32),
    "floor_dark":   (28, 38, 48),
    "floor":        (42, 52, 62),
    "floor_light":  (58, 68, 78),
    "floor_hi":     (70, 80, 90),
    "metal_dark":   (55, 60, 68),
    "metal":        (80, 88, 98),
    "metal_light":  (110, 118, 128),
    "metal_hi":     (140, 148, 155),
    "green_v_dim":  (15, 45, 22),
    "green_dim":    (30, 80, 40),
    "green":        (55, 185, 85),
    "green_bright": (110, 255, 140),
    "cyan":         (80, 200, 220),
    "cyan_dim":     (35, 90, 100),
    "red":          (210, 55, 55),
    "red_dim":      (130, 35, 35),
    "red_v_dim":    (70, 20, 20),
    "amber":        (210, 165, 55),
    "amber_dim":    (130, 95, 35),
    "amber_v_dim":  (70, 55, 20),
    "blue_led":     (45, 110, 255),
    "white":        (210, 210, 210),
    "white_dim":    (150, 150, 150),
    "door_v_dark":  (40, 32, 24),
    "door_dark":    (62, 52, 40),
    "door":         (88, 74, 55),
    "door_light":   (112, 96, 72),
    "rust":         (125, 65, 32),
    "rust_dim":     (80, 42, 22),
    "pipe":         (65, 72, 78),
    "pipe_dark":    (45, 50, 55),
    "pipe_hi":      (85, 92, 98),
    "cable":        (42, 48, 38),
    "cable2":       (55, 62, 50),
    "purple":       (105, 45, 145),
    "purple_dim":   (60, 25, 85),
    # Extended palette for new scenes
    "blue_dim":     (20, 40, 80),
    "blue_screen":  (35, 65, 120),
    "blue_bright":  (70, 140, 255),
    "diff_green":   (40, 120, 50),
    "diff_green_bg":(18, 40, 22),
    "diff_red":     (160, 50, 50),
    "diff_red_bg":  (45, 16, 16),
    "phone_screen": (60, 140, 200),
    "orange_alert": (220, 120, 30),
    "orange_dim":   (140, 70, 20),
    "city_light":   (180, 165, 120),
    "city_dim":     (60, 55, 42),
    "pillow":       (50, 48, 58),
    "blanket":      (38, 42, 55),
    "blanket_dark": (25, 28, 40),
    "wood_dark":    (35, 28, 22),
    "wood":         (52, 42, 34),
    "wood_light":   (68, 56, 44),
    "grey_dark":    (30, 32, 36),
    "grey":         (50, 54, 58),
    "grey_light":   (75, 80, 85),
    "blood_red":    (160, 15, 15),
    "blood_dim":    (90, 8, 8),
    "glitch_cyan":  (0, 220, 200),
    "glitch_magenta":(200, 30, 180),
}


def create_image():
    img = Image.new("RGB", (W, H), C["black"])
    draw = ImageDraw.Draw(img)
    return img, draw

def rect(d, x, y, w, h, color):
    d.rectangle([x, y, x+w-1, y+h-1], fill=color)

def pixel(d, x, y, color):
    if 0 <= x < W and 0 <= y < H:
        d.point((x, y), fill=color)

def hline(d, x, y, length, color):
    d.line([(x, y), (x+length-1, y)], fill=color)

def vline(d, x, y, length, color):
    d.line([(x, y), (x, y+length-1)], fill=color)

def add_noise(img, intensity=8):
    """Add subtle noise for texture."""
    random.seed(42)
    pixels = img.load()
    for y in range(H):
        for x in range(W):
            r, g, b = pixels[x, y]
            n = random.randint(-intensity, intensity)
            pixels[x, y] = (max(0, min(255, r+n)), max(0, min(255, g+n)), max(0, min(255, b+n)))

def add_glow(img, cx, cy, radius, color, intensity=0.5):
    """Add a radial glow effect."""
    pixels = img.load()
    cr, cg, cb = color
    for y in range(max(0, cy-radius), min(H, cy+radius)):
        for x in range(max(0, cx-radius), min(W, cx+radius)):
            dist = ((x-cx)**2 + (y-cy)**2) ** 0.5
            if dist < radius:
                factor = (1 - dist/radius) * intensity
                r, g, b = pixels[x, y]
                pixels[x, y] = (
                    min(255, int(r + cr * factor)),
                    min(255, int(g + cg * factor)),
                    min(255, int(b + cb * factor)),
                )


def draw_monitor(d, x, y, w, h, screen_color, text_lines=None):
    """Draw a monitor/screen."""
    # Bezel
    rect(d, x, y, w, h, C["metal_dark"])
    rect(d, x+1, y+1, w-2, h-2, C["metal"])
    # Screen
    sw, sh = w-6, h-6
    rect(d, x+3, y+3, sw, sh, C["black"])
    rect(d, x+4, y+4, sw-2, sh-2, screen_color)
    # Stand
    rect(d, x+w//2-3, y+h, 6, 3, C["metal_dark"])
    rect(d, x+w//2-5, y+h+3, 10, 2, C["metal"])
    # Screen reflection
    hline(d, x+5, y+5, sw//3, tuple(min(255, c+20) for c in screen_color))


# ============================================================
# Scene 1: bedroom.png
# ============================================================

def generate_bedroom():
    """Scene 1: Dark bedroom at 3AM. Laptop glow, phone buzzing, city lights."""
    img, d = create_image()

    # === Dark walls ===
    rect(d, 0, 0, W, H, C["black"])
    # Subtle wall texture - very dark blue-grey
    for y in range(0, 70):
        v = 10 + y // 8
        hline(d, 0, y, W, (v, v+2, v+6))

    # === Floor ===
    rect(d, 0, 75, W, 25, C["floor_v_dark"])
    for i in range(0, W, 12):
        vline(d, i, 75, 25, (14, 18, 24))
    rect(d, 0, 75, W, 1, C["floor_dark"])

    # === Window (right side) — city skyline at night ===
    wx, wy, ww, wh = 140, 8, 50, 42
    # Window frame
    rect(d, wx-1, wy-1, ww+2, wh+2, C["grey_dark"])
    # Night sky
    rect(d, wx, wy, ww, wh, (6, 8, 18))
    # Stars
    random.seed(33)
    for _ in range(15):
        sx = random.randint(wx+2, wx+ww-3)
        sy = random.randint(wy+2, wy+14)
        pixel(d, sx, sy, (120, 120, 140))
    # City skyline - distant buildings
    buildings = [(0, 22), (6, 18), (11, 24), (16, 16), (20, 26), (25, 20),
                 (29, 14), (33, 22), (37, 18), (42, 24), (46, 20)]
    for bx_off, bh in buildings:
        b_top = wy + wh - bh
        bw = random.randint(3, 5)
        rect(d, wx+bx_off, b_top, bw, bh, C["city_dim"])
        # Lit windows in buildings
        for _ in range(random.randint(1, 3)):
            lx = wx + bx_off + random.randint(0, max(0, bw-2))
            ly = b_top + random.randint(1, max(1, bh-3))
            pixel(d, lx, ly, C["city_light"])
    # Window cross-frame
    vline(d, wx+ww//2, wy, wh, C["grey_dark"])
    hline(d, wx, wy+wh//2, ww, C["grey_dark"])
    # Curtain edges (dark fabric)
    rect(d, wx-4, wy-1, 3, wh+2, C["blanket_dark"])
    rect(d, wx+ww+1, wy-1, 3, wh+2, C["blanket_dark"])

    # === Bed (left side) — messy sheets ===
    bx, by = 4, 48
    # Bed frame
    rect(d, bx, by+18, 55, 5, C["wood_dark"])
    rect(d, bx, by+23, 55, 2, C["wood"])
    # Mattress
    rect(d, bx+2, by+8, 51, 12, C["blanket_dark"])
    # Rumpled blanket
    rect(d, bx+4, by+4, 46, 15, C["blanket"])
    # Blanket folds/wrinkles
    for i in range(5):
        fx = bx + 8 + i * 9
        hline(d, fx, by + 6 + (i % 3), 6, C["blanket_dark"])
        hline(d, fx+1, by + 10 + (i % 2), 4, (45, 50, 65))
    # Pillow
    rect(d, bx+5, by, 16, 7, C["pillow"])
    rect(d, bx+6, by+1, 14, 5, (58, 55, 65))
    # Pillow dent
    hline(d, bx+9, by+3, 8, C["pillow"])

    # === Desk (center-right) ===
    dx, dy = 68, 48
    dw, dh = 62, 3
    rect(d, dx, dy, dw, dh, C["wood"])
    rect(d, dx, dy, dw, 1, C["wood_light"])
    # Desk legs
    rect(d, dx+2, dy+dh, 2, 24, C["wood_dark"])
    rect(d, dx+dw-4, dy+dh, 2, 24, C["wood_dark"])

    # === Laptop on desk (main light source) ===
    lx, ly = 78, 28
    lw, lh = 34, 20
    # Laptop screen (angled slightly)
    rect(d, lx, ly, lw, lh, C["grey_dark"])
    rect(d, lx+1, ly+1, lw-2, lh-2, C["grey"])
    # Screen content — terminal with error text
    rect(d, lx+2, ly+2, lw-4, lh-4, (8, 14, 22))
    # Terminal lines
    for i, length in enumerate([16, 22, 12, 18, 8, 14, 24, 10]):
        ty = ly + 4 + i * 2
        if ty < ly + lh - 3:
            color = C["red"] if i == 2 else C["green_dim"]
            hline(d, lx+4, ty, min(length, lw-8), color)
    # Blinking cursor
    rect(d, lx+4, ly+lh-5, 2, 1, C["green_bright"])
    # Laptop base on desk
    rect(d, lx-2, dy-2, lw+4, 3, C["grey"])
    rect(d, lx, dy-1, lw, 1, C["grey_light"])
    # Trackpad
    rect(d, lx+12, dy-1, 10, 2, C["metal_dark"])

    # === Phone buzzing on desk (PagerDuty alert) ===
    px, py = 120, dy-6
    pw, ph = 8, 5
    # Phone body
    rect(d, px, py, pw, ph, (20, 20, 28))
    # Phone screen — lit up with alert
    rect(d, px+1, py+1, pw-2, ph-2, C["orange_alert"])
    # Alert icon — small exclamation
    pixel(d, px+3, py+1, C["white"])
    pixel(d, px+4, py+1, C["white"])
    pixel(d, px+3, py+3, C["white"])
    # Buzz lines (vibration effect)
    pixel(d, px-1, py+1, C["orange_dim"])
    pixel(d, px+pw, py+2, C["orange_dim"])
    pixel(d, px-1, py+3, C["orange_dim"])

    # === Coffee mug on desk ===
    rect(d, dx+4, dy-4, 5, 4, C["grey_dark"])
    rect(d, dx+9, dy-3, 2, 2, C["grey_dark"])  # handle

    # === Clock on wall showing 3:00 ===
    cx, cy = 66, 14
    rect(d, cx, cy, 12, 6, C["grey_dark"])
    rect(d, cx+1, cy+1, 10, 4, (5, 8, 14))
    # "3:00" in red LED
    hline(d, cx+2, cy+2, 2, C["red"])
    pixel(d, cx+5, cy+2, C["red"])
    pixel(d, cx+5, cy+3, C["red"])
    hline(d, cx+7, cy+2, 2, C["red"])
    hline(d, cx+7, cy+3, 2, C["red"])

    # === Lighting effects ===
    # Laptop screen glow — dominant light source
    add_glow(img, lx+lw//2, ly+lh//2, 45, (25, 50, 70), 0.25)
    # Phone alert glow — orange pulse
    add_glow(img, px+pw//2, py+ph//2, 15, (80, 50, 10), 0.35)
    # City window light — very faint
    add_glow(img, wx+ww//2, wy+wh//2, 30, (15, 15, 10), 0.08)

    add_noise(img, 5)
    img.save(f"{OUTPUT_DIR}/bedroom.png")
    print("  ✓ bedroom.png")


# ============================================================
# Scene 2: prod_server.png
# ============================================================

def generate_prod_server():
    """Scene 2: Production server dashboard. Logs scrolling, graphs spiking, errors."""
    img, d = create_image()

    # Full-screen terminal background
    rect(d, 0, 0, W, H, (6, 10, 16))

    # === Top status bar ===
    rect(d, 0, 0, W, 5, (18, 22, 32))
    hline(d, 0, 4, W, (25, 30, 40))
    # hostname and time in status bar
    hline(d, 3, 2, 28, C["green_dim"])          # prod-web-01
    hline(d, 80, 2, 14, C["amber_dim"])          # 03:14 UTC
    hline(d, 160, 2, 18, C["red_dim"])           # CRITICAL
    # Red dot indicator
    rect(d, 155, 1, 3, 3, C["red"])

    # === Left panel: scrolling logs (60% width) ===
    lp_x, lp_y, lp_w, lp_h = 1, 7, 118, 58
    rect(d, lp_x, lp_y, lp_w, lp_h, (10, 14, 22))
    # Panel border
    vline(d, lp_x+lp_w, lp_y, lp_h, (25, 30, 40))
    # Panel title
    hline(d, lp_x+2, lp_y+1, 20, C["cyan_dim"])   # "Access Logs"

    # Log lines — mostly green/dim, some red errors
    random.seed(314)
    log_colors = [C["green_dim"]] * 6 + [C["white_dim"]] * 2 + [C["red"]] * 2
    for i in range(22):
        ly = lp_y + 4 + i * 2 + (i // 8)
        if ly >= lp_y + lp_h - 2:
            break
        # Timestamp
        hline(d, lp_x+2, ly, 10, C["grey_dark"])
        # Log level indicator
        is_error = (i in [5, 8, 12, 15, 18, 19, 20, 21])
        level_color = C["red"] if is_error else C["green_dim"]
        hline(d, lp_x+14, ly, 4, level_color)
        # Message
        msg_len = random.randint(20, 70)
        msg_color = C["red_dim"] if is_error else random.choice(log_colors)
        hline(d, lp_x+20, ly, min(msg_len, lp_w-24), msg_color)

    # Errors become more frequent at bottom (things getting worse)
    for i in range(3):
        ey = lp_y + lp_h - 6 + i * 2
        rect(d, lp_x+2, ey, lp_w-4, 1, C["red_v_dim"])
        hline(d, lp_x+2, ey, 10, C["red_dim"])
        hline(d, lp_x+20, ey, random.randint(30, 60), C["red"])

    # === Right panel top: CPU/Memory graph ===
    gp_x, gp_y, gp_w, gp_h = 122, 7, 76, 26
    rect(d, gp_x, gp_y, gp_w, gp_h, (10, 14, 22))
    # Graph title
    hline(d, gp_x+2, gp_y+1, 12, C["amber_dim"])  # "CPU / MEM"
    # Graph axes
    vline(d, gp_x+8, gp_y+4, gp_h-6, C["grey_dark"])
    hline(d, gp_x+8, gp_y+gp_h-3, gp_w-12, C["grey_dark"])
    # Y-axis labels
    for i in range(4):
        ly = gp_y + 5 + i * 5
        hline(d, gp_x+2, ly, 5, (30, 34, 40))
    # CPU line — spikes dramatically at the right
    cpu_vals = [16, 14, 15, 13, 14, 12, 14, 18, 22, 30, 40, 55, 70, 82, 88, 92, 95]
    for i, val in enumerate(cpu_vals):
        gx = gp_x + 10 + i * 4
        gy = gp_y + gp_h - 4 - (val * (gp_h - 8)) // 100
        if i > 0:
            prev_gy = gp_y + gp_h - 4 - (cpu_vals[i-1] * (gp_h - 8)) // 100
            # Draw line segment
            for step in range(4):
                sy = prev_gy + (gy - prev_gy) * step // 4
                color = C["red"] if val > 70 else C["amber"] if val > 40 else C["green"]
                pixel(d, gx-4+step, sy, color)
        color = C["red"] if val > 70 else C["amber"] if val > 40 else C["green"]
        pixel(d, gx, gy, color)
        pixel(d, gx, gy+1, color)

    # === Right panel bottom: error rate / request graph ===
    ep_x, ep_y, ep_w, ep_h = 122, 35, 76, 30
    rect(d, ep_x, ep_y, ep_w, ep_h, (10, 14, 22))
    hline(d, ep_x+2, ep_y+1, 14, C["red_dim"])    # "Error Rate"
    vline(d, ep_x+8, ep_y+4, ep_h-6, C["grey_dark"])
    hline(d, ep_x+8, ep_y+ep_h-3, ep_w-12, C["grey_dark"])
    # Error rate bars — escalating
    err_vals = [2, 1, 3, 2, 1, 4, 3, 8, 15, 25, 40, 60, 75, 88, 95]
    for i, val in enumerate(err_vals):
        bx = ep_x + 10 + i * 4
        bar_h = max(1, (val * (ep_h - 10)) // 100)
        by = ep_y + ep_h - 4 - bar_h
        bar_color = C["red"] if val > 50 else C["amber"] if val > 20 else C["green_dim"]
        rect(d, bx, by, 3, bar_h, bar_color)

    # === Bottom panel: active alerts ===
    ap_y = 67
    rect(d, 1, ap_y, W-2, H-ap_y-1, (14, 10, 10))
    hline(d, 1, ap_y, W-2, (40, 15, 15))
    # "ACTIVE ALERTS (23)"
    hline(d, 4, ap_y+2, 22, C["red"])
    hline(d, 30, ap_y+2, 4, C["amber"])

    # Alert lines
    alert_msgs = [
        (C["red"],     45), (C["red"],     52), (C["red"],     38),
        (C["amber"],   48), (C["red"],     55), (C["red"],     60),
        (C["red"],     42), (C["amber"],   35), (C["red"],     50),
    ]
    for i, (ac, aw) in enumerate(alert_msgs):
        ay = ap_y + 5 + i * 3
        if ay >= H - 3:
            break
        # Severity dot
        pixel(d, 4, ay, ac)
        pixel(d, 5, ay, ac)
        # Timestamp
        hline(d, 8, ay, 12, C["grey_dark"])
        # Service name
        hline(d, 22, ay, 16, C["amber_dim"])
        # Message
        hline(d, 40, ay, aw, ac if ac == C["red"] else C["amber_dim"])

    # === Pulsing red border effect (things are bad) ===
    for edge_y in [0, H-1]:
        hline(d, 0, edge_y, W, C["red_v_dim"])
    for edge_x in [0, W-1]:
        vline(d, edge_x, 0, H, C["red_v_dim"])

    # === Glow effects ===
    add_glow(img, gp_x+gp_w-8, gp_y+8, 20, (80, 15, 15), 0.2)  # Spike glow
    add_glow(img, ep_x+ep_w-8, ep_y+10, 18, (80, 15, 15), 0.2)  # Error spike glow
    add_glow(img, 155, 1, 8, (80, 15, 15), 0.4)                  # CRITICAL indicator

    add_noise(img, 4)
    img.save(f"{OUTPUT_DIR}/prod_server.png")
    print("  ✓ prod_server.png")


# ============================================================
# Scene 3: code_review.png
# ============================================================

def generate_code_review():
    """Scene 3: Git diff view. A PR with hidden messages in the code."""
    img, d = create_image()

    # Full-screen terminal
    rect(d, 0, 0, W, H, (6, 10, 16))

    # === Top bar: diff header ===
    rect(d, 0, 0, W, 5, (18, 22, 32))
    hline(d, 0, 4, W, (25, 30, 40))
    # "diff --git a/lib/auth.py b/lib/auth.py"
    hline(d, 3, 2, 50, C["white_dim"])

    # === File header ===
    rect(d, 0, 6, W, 4, (20, 28, 40))
    hline(d, 3, 7, 30, C["cyan"])        # "--- a/lib/auth.py"
    hline(d, 3, 9, 30, C["cyan"])        # "+++ b/lib/auth.py"

    # === Hunk header ===
    rect(d, 0, 11, W, 3, (22, 22, 40))
    hline(d, 3, 12, 40, C["purple"])      # "@@ -142,8 +142,24 @@"

    # === Diff lines ===
    random.seed(71)
    # Line number gutter
    gutter_w = 12

    # Define diff content: (type, length) where type is 'ctx', 'add', 'del', 'add_sus'
    diff_lines = [
        ('ctx', 38), ('ctx', 30), ('ctx', 45),
        ('del', 28), ('del', 35),
        ('add', 42), ('add', 50), ('add', 30), ('add', 22),
        ('ctx', 40), ('ctx', 18),
        ('del', 32),
        ('add', 48), ('add_sus', 55), ('add', 38),
        ('ctx', 26), ('ctx', 44),
        ('del', 30), ('del', 40), ('del', 25),
        ('add', 52), ('add_sus', 60), ('add', 34), ('add', 28), ('add_sus', 45),
        ('ctx', 36), ('ctx', 30),
    ]

    for i, (line_type, length) in enumerate(diff_lines):
        ly = 15 + i * 3
        if ly >= H - 5:
            break

        # Line number gutter
        hline(d, 1, ly, 5, (35, 38, 45))
        hline(d, 7, ly, 5, (35, 38, 45))
        vline(d, gutter_w, ly, 3, (20, 24, 32))

        clamp_len = min(length, W - gutter_w - 6)

        if line_type == 'ctx':
            # Context line — dim white
            hline(d, gutter_w+2, ly, clamp_len, (55, 58, 62))
            hline(d, gutter_w+2, ly+1, max(0, clamp_len-10), (40, 43, 48))
        elif line_type == 'del':
            # Deleted line — red background, red text
            rect(d, gutter_w+1, ly, W-gutter_w-2, 2, C["diff_red_bg"])
            pixel(d, gutter_w+2, ly, C["diff_red"])   # '-' marker
            hline(d, gutter_w+4, ly, clamp_len, C["diff_red"])
            hline(d, gutter_w+4, ly+1, max(0, clamp_len-8), (100, 35, 35))
        elif line_type == 'add':
            # Added line — green background, green text
            rect(d, gutter_w+1, ly, W-gutter_w-2, 2, C["diff_green_bg"])
            pixel(d, gutter_w+2, ly, C["diff_green"])  # '+' marker
            hline(d, gutter_w+4, ly, clamp_len, C["diff_green"])
            hline(d, gutter_w+4, ly+1, max(0, clamp_len-8), (30, 80, 35))
        elif line_type == 'add_sus':
            # Suspicious added line — green bg but with amber/highlighted section
            rect(d, gutter_w+1, ly, W-gutter_w-2, 2, C["diff_green_bg"])
            pixel(d, gutter_w+2, ly, C["diff_green"])
            # Normal part
            norm_len = clamp_len // 3
            hline(d, gutter_w+4, ly, norm_len, C["diff_green"])
            # Suspicious highlighted section — the "hidden message"
            sus_start = gutter_w + 4 + norm_len + 2
            sus_len = clamp_len - norm_len - 4
            rect(d, sus_start-1, ly, sus_len+2, 2, (30, 45, 20))
            hline(d, sus_start, ly, sus_len, C["amber"])
            hline(d, sus_start, ly+1, sus_len, C["amber_dim"])

    # === Bottom: command prompt ===
    rect(d, 0, H-5, W, 5, (12, 16, 24))
    hline(d, 3, H-3, 16, C["green_dim"])    # prompt
    rect(d, 20, H-3, 2, 1, C["green_bright"])  # cursor

    # === Subtle glow on suspicious lines ===
    add_glow(img, W//2+20, 56, 30, (40, 40, 10), 0.1)
    add_glow(img, W//2+20, 80, 30, (40, 40, 10), 0.1)

    add_noise(img, 3)
    img.save(f"{OUTPUT_DIR}/code_review.png")
    print("  ✓ code_review.png")


# ============================================================
# Scene 4: supply_chain.png
# ============================================================

def generate_supply_chain():
    """Scene 4: Forensics terminal. Git log, countdown to 8AM, encrypted files."""
    img, d = create_image()

    # Very dark background — deeper in the rabbit hole
    rect(d, 0, 0, W, H, (4, 6, 12))

    # Subtle hex/data watermark in background
    random.seed(99)
    for _ in range(200):
        hx = random.randint(0, W-1)
        hy = random.randint(0, H-1)
        pixel(d, hx, hy, (8, 12, 20))

    # === Left panel: git log output ===
    gl_x, gl_y, gl_w, gl_h = 2, 3, 100, 65
    rect(d, gl_x, gl_y, gl_w, gl_h, (8, 10, 18))
    # Title
    hline(d, gl_x+2, gl_y+1, 16, C["amber"])   # "$ git log --all"

    # Git log entries
    commits = [
        # (hash_color, message_len, time_len, author_suspicious)
        (C["amber"],     30, 14, False),
        (C["amber"],     26, 14, False),
        (C["amber"],     38, 14, False),
        (C["red"],       34, 14, True),      # suspicious
        (C["amber"],     28, 14, False),
        (C["red"],       42, 14, True),      # suspicious
        (C["amber"],     22, 14, False),
        (C["red"],       48, 14, True),      # suspicious
    ]
    for i, (hc, ml, tl, sus) in enumerate(commits):
        cy = gl_y + 5 + i * 7
        if cy + 5 >= gl_y + gl_h:
            break
        # Commit hash
        hline(d, gl_x+2, cy, 8, hc)
        # Author
        author_color = C["red_dim"] if sus else C["cyan_dim"]
        hline(d, gl_x+12, cy, 14, author_color)
        # Date
        hline(d, gl_x+28, cy, tl, C["grey_dark"])
        # Commit message
        msg_color = C["red"] if sus else C["green_dim"]
        hline(d, gl_x+6, cy+2, min(ml, gl_w-10), msg_color)
        # Diff stats on suspicious commits
        if sus:
            hline(d, gl_x+6, cy+4, 8, C["green"])
            hline(d, gl_x+16, cy+4, 6, C["red"])
            # Files changed indicator
            hline(d, gl_x+24, cy+4, 18, C["amber_dim"])

    # === Right panel: encrypted files / forensic analysis ===
    fp_x, fp_y, fp_w, fp_h = 106, 3, 92, 40
    rect(d, fp_x, fp_y, fp_w, fp_h, (8, 10, 18))
    hline(d, fp_x+2, fp_y+1, 22, C["cyan_dim"])   # "Dependency Analysis"

    # File tree with threat indicators
    files_data = [
        (4,  'dir',  20, False),
        (8,  'file', 28, False),
        (8,  'file', 32, True),     # compromised
        (8,  'file', 24, False),
        (4,  'dir',  18, False),
        (8,  'file', 30, True),     # compromised
        (8,  'file', 26, True),     # compromised
        (4,  'dir',  22, False),
        (8,  'file', 34, False),
        (8,  'file', 20, True),     # compromised
    ]
    for i, (indent, ftype, flen, compromised) in enumerate(files_data):
        fy = fp_y + 4 + i * 3
        if fy >= fp_y + fp_h - 2:
            break
        # Tree connector
        if indent > 4:
            vline(d, fp_x+indent-2, fy-1, 3, C["grey_dark"])
            hline(d, fp_x+indent-2, fy, 2, C["grey_dark"])
        # Icon
        icon_c = C["amber"] if ftype == 'dir' else (C["red"] if compromised else C["cyan_dim"])
        pixel(d, fp_x+indent+2, fy, icon_c)
        pixel(d, fp_x+indent+3, fy, icon_c)
        # Filename
        fc = C["red"] if compromised else C["white_dim"]
        hline(d, fp_x+indent+5, fy, min(flen, fp_w-indent-8), fc)
        # Threat tag
        if compromised:
            tag_x = fp_x + indent + 5 + flen + 2
            if tag_x + 8 < fp_x + fp_w:
                hline(d, tag_x, fy, 8, C["red"])

    # === Countdown timer (bottom right) — time until 8:00 AM trigger ===
    ct_x, ct_y, ct_w, ct_h = 130, 48, 60, 18
    rect(d, ct_x, ct_y, ct_w, ct_h, (20, 8, 8))
    rect(d, ct_x+1, ct_y+1, ct_w-2, ct_h-2, (14, 5, 5))
    # "TRIGGER IN:" label
    hline(d, ct_x+4, ct_y+3, 16, C["red_dim"])
    # Large countdown digits "04:46:12"
    digit_y = ct_y + 7
    # Hours
    rect(d, ct_x+8, digit_y, 3, 5, C["red"])
    rect(d, ct_x+12, digit_y, 3, 5, C["red"])
    # Colon
    pixel(d, ct_x+16, digit_y+1, C["red"])
    pixel(d, ct_x+16, digit_y+3, C["red"])
    # Minutes
    rect(d, ct_x+18, digit_y, 3, 5, C["red"])
    rect(d, ct_x+22, digit_y, 3, 5, C["red"])
    # Colon
    pixel(d, ct_x+26, digit_y+1, C["red_dim"])
    pixel(d, ct_x+26, digit_y+3, C["red_dim"])
    # Seconds
    rect(d, ct_x+28, digit_y, 3, 5, C["red_dim"])
    rect(d, ct_x+32, digit_y, 3, 5, C["red_dim"])
    # "08:00 UTC" target label
    hline(d, ct_x+8, ct_y+14, 18, C["red_v_dim"])

    # === Bottom: hash comparison / checksums ===
    hash_y = 72
    rect(d, 2, hash_y, W-4, 26, (6, 8, 14))
    hline(d, 4, hash_y+1, 24, C["amber_dim"])   # "Checksum Verification"

    # Hash rows — expected vs actual, some mismatched
    for i in range(7):
        hy = hash_y + 4 + i * 3
        if hy >= H - 3:
            break
        # Package name
        hline(d, 4, hy, 20, C["white_dim"])
        # Expected hash
        hline(d, 26, hy, 32, C["green_dim"])
        # Actual hash — red if mismatch
        mismatch = i in [1, 3, 4, 6]
        actual_c = C["red"] if mismatch else C["green_dim"]
        hline(d, 62, hy, 32, actual_c)
        # Status
        status_c = C["red"] if mismatch else C["green"]
        pixel(d, 96, hy, status_c)
        pixel(d, 97, hy, status_c)

    # === Glows ===
    add_glow(img, ct_x+ct_w//2, ct_y+ct_h//2, 25, (80, 15, 15), 0.25)  # Countdown glow
    # Suspicious commit glow
    add_glow(img, gl_x+gl_w//2, gl_y+gl_h//2, 30, (40, 10, 10), 0.1)

    add_noise(img, 4)
    img.save(f"{OUTPUT_DIR}/supply_chain.png")
    print("  ✓ supply_chain.png")


# ============================================================
# Scene 5: the_mirror.png
# ============================================================

def generate_the_mirror():
    """Scene 5: The reveal. git blame, glitch effects, the screen looks back at you."""
    img, d = create_image()

    # Total darkness
    rect(d, 0, 0, W, H, C["black"])

    # === Screen fills the entire view — it IS the scene ===
    # Very dark red-tinted base
    rect(d, 0, 0, W, H, (8, 2, 2))

    # === Scan lines across entire image ===
    for y in range(0, H, 2):
        hline(d, 0, y, W, (12, 4, 4))

    # === git blame output — top half ===
    random.seed(66)
    blame_y_start = 4
    for i in range(16):
        ly = blame_y_start + i * 3
        if ly >= 52:
            break

        # Commit hash
        hline(d, 3, ly, 7, C["amber_dim"])
        # Author — ALL lines show YOUR name (same author color)
        hline(d, 12, ly, 10, C["red"])
        # Timestamp
        hline(d, 24, ly, 12, C["red_v_dim"])
        # Line number
        hline(d, 38, ly, 3, (40, 15, 15))
        # Code content — gets more disturbing
        code_len = random.randint(20, 65)
        code_color = C["red_dim"] if i < 10 else C["red"]
        hline(d, 44, ly, min(code_len, W-48), code_color)

        # Every author field is YOUR name — emphasized
        if i % 4 == 0:
            rect(d, 11, ly-1, 12, 3, (30, 5, 5))
            hline(d, 12, ly, 10, C["red"])

    # === Central revelation message area ===
    msg_y = 52
    # Dark box
    rect(d, 20, msg_y, W-40, 14, (18, 4, 4))
    rect(d, 21, msg_y+1, W-42, 12, (12, 2, 2))
    # "你终于想起来了吗？" — represented as the key line
    # Two rows of characters: top is the question
    msg_w = W - 80
    hline(d, 40, msg_y+4, msg_w, C["red"])
    hline(d, 42, msg_y+5, msg_w-4, C["blood_red"])
    # Second line — emphasis
    hline(d, 50, msg_y+8, msg_w-20, C["red_dim"])
    hline(d, 52, msg_y+9, msg_w-24, (100, 12, 12))

    # === "It was you all along" — git blame proof ===
    proof_y = 70
    hline(d, 10, proof_y, 30, C["amber"])       # "All 847 lines authored by:"
    hline(d, 10, proof_y+3, 24, C["red"])        # Your username
    hline(d, 10, proof_y+6, 36, C["red_dim"])    # Your email
    hline(d, 10, proof_y+9, 28, C["amber_dim"])  # "First commit: 6 months ago"

    # === Glitch artifacts — heavy ===
    random.seed(42)
    # Horizontal displacement bands
    for _ in range(12):
        gy = random.randint(2, H-4)
        gx_offset = random.randint(-15, 15)
        gw = random.randint(30, 120)
        gx = max(0, min(W-gw, 20 + gx_offset))
        gh = random.randint(1, 3)
        # Chromatic aberration — cyan/magenta split
        if random.random() > 0.5:
            rect(d, gx, gy, gw, gh, C["glitch_cyan"])
        else:
            rect(d, gx, gy, gw, gh, C["glitch_magenta"])

    # Heavy static noise blocks
    for _ in range(25):
        bx = random.randint(0, W-15)
        by = random.randint(0, H-8)
        bw = random.randint(4, 18)
        bh = random.randint(2, 6)
        v = random.randint(20, 80)
        rect(d, bx, by, bw, bh, (v, v//6, v//6))

    # Scattered pixel noise — dense
    for _ in range(800):
        nx = random.randint(0, W-1)
        ny = random.randint(0, H-1)
        v = random.randint(10, 60)
        pixel(d, nx, ny, (v, v//5, v//5))

    # === Digital "eye" effect — the screen looks back ===
    # Subtle concentric rings in the lower-center suggesting an eye/lens
    eye_cx, eye_cy = W//2, 84
    for r in [12, 8, 5, 3]:
        eye_color = (50 + (12-r)*8, 5, 5)
        for angle_step in range(60):
            import math
            a = angle_step * math.pi * 2 / 60
            ex = int(eye_cx + r * math.cos(a))
            ey = int(eye_cy + r * 0.6 * math.sin(a))  # Elliptical
            pixel(d, ex, ey, eye_color)
    # Eye center — bright red dot
    rect(d, eye_cx-1, eye_cy-1, 3, 2, C["blood_red"])
    pixel(d, eye_cx, eye_cy, C["red"])

    # === Vertical line distortion at edges ===
    for vx in [0, 1, W-2, W-1]:
        for vy in range(H):
            if random.random() > 0.6:
                pixel(d, vx, vy, C["red_v_dim"])

    # === Glow effects ===
    add_glow(img, W//2, msg_y+7, 50, (80, 8, 8), 0.3)    # Message glow
    add_glow(img, eye_cx, eye_cy, 20, (100, 10, 10), 0.4)  # Eye glow
    # Overall red wash
    add_glow(img, W//2, H//2, 80, (30, 3, 3), 0.15)

    add_noise(img, 6)
    img.save(f"{OUTPUT_DIR}/the_mirror.png")
    print("  ✓ the_mirror.png")


# ============================================================
# Title screen
# ============================================================

def generate_title():
    """Title screen with game logo — moody, ominous."""
    img, d = create_image()

    # Dark gradient background — deeper, more ominous than before
    for y in range(H):
        r = max(0, 12 - y // 8)
        g = max(0, 10 - y // 10)
        b = max(0, 20 - y // 5)
        hline(d, 0, y, W, (r, g, b))

    # Subtle static texture in background
    random.seed(55)
    for _ in range(150):
        sx = random.randint(0, W-1)
        sy = random.randint(0, H-1)
        pixel(d, sx, sy, (14, 16, 24))

    # === Decorative top line ===
    hline(d, 30, 10, W-60, C["red_v_dim"])
    pixel(d, 30, 10, C["red_dim"])
    pixel(d, W-31, 10, C["red_dim"])

    # === "OFFLINE" in large pixel blocks ===
    block = 5
    letters_y = 20
    # Use cyan but slightly desaturated/darker for more ominous feel
    letter_c = (60, 160, 180)
    # O
    ox = 20
    rect(d, ox, letters_y, block*4, block, letter_c)
    rect(d, ox, letters_y+block*4, block*4, block, letter_c)
    rect(d, ox, letters_y, block, block*5, letter_c)
    rect(d, ox+block*3, letters_y, block, block*5, letter_c)
    # F
    fx = 44
    rect(d, fx, letters_y, block*4, block, letter_c)
    rect(d, fx, letters_y, block, block*5, letter_c)
    rect(d, fx, letters_y+block*2, block*3, block, letter_c)
    # F
    f2x = 68
    rect(d, f2x, letters_y, block*4, block, letter_c)
    rect(d, f2x, letters_y, block, block*5, letter_c)
    rect(d, f2x, letters_y+block*2, block*3, block, letter_c)
    # L
    lx = 92
    rect(d, lx, letters_y, block, block*5, letter_c)
    rect(d, lx, letters_y+block*4, block*4, block, letter_c)
    # I
    ix = 116
    rect(d, ix, letters_y, block*4, block, letter_c)
    rect(d, ix+block*1.5, letters_y, block, block*5, letter_c)
    rect(d, ix, letters_y+block*4, block*4, block, letter_c)
    # N
    nx = 140
    rect(d, nx, letters_y, block, block*5, letter_c)
    rect(d, nx+block*3, letters_y, block, block*5, letter_c)
    for i in range(4):
        rect(d, int(nx+block+i*block*0.7), letters_y+block+i*block, block, block, letter_c)
    # E
    ex = 164
    rect(d, ex, letters_y, block*4, block, letter_c)
    rect(d, ex, letters_y, block, block*5, letter_c)
    rect(d, ex, letters_y+block*2, block*3, block, letter_c)
    rect(d, ex, letters_y+block*4, block*4, block, letter_c)

    # === "SIGNAL" in red-tinted green (more ominous) ===
    sig_y = 52
    block2 = 4
    sig_c = (45, 140, 60)  # Slightly muted green
    # S
    sx = 40
    rect(d, sx, sig_y, block2*4, block2, sig_c)
    rect(d, sx, sig_y+block2, block2, block2, sig_c)
    rect(d, sx, sig_y+block2*2, block2*4, block2, sig_c)
    rect(d, sx+block2*3, sig_y+block2*3, block2, block2, sig_c)
    rect(d, sx, sig_y+block2*4, block2*4, block2, sig_c)
    # I
    si = 60
    rect(d, si+block2, sig_y, block2, block2*5, sig_c)
    rect(d, si, sig_y, block2*3, block2, sig_c)
    rect(d, si, sig_y+block2*4, block2*3, block2, sig_c)
    # G
    gx = 76
    rect(d, gx, sig_y, block2*4, block2, sig_c)
    rect(d, gx, sig_y, block2, block2*5, sig_c)
    rect(d, gx, sig_y+block2*4, block2*4, block2, sig_c)
    rect(d, gx+block2*3, sig_y+block2*2, block2, block2*3, sig_c)
    rect(d, gx+block2*2, sig_y+block2*2, block2, block2, sig_c)
    # N
    gnx = 96
    rect(d, gnx, sig_y, block2, block2*5, sig_c)
    rect(d, gnx+block2*3, sig_y, block2, block2*5, sig_c)
    for i in range(3):
        rect(d, gnx+block2+i*block2, sig_y+block2+i*block2, block2, block2, sig_c)
    # A
    ax = 116
    rect(d, ax, sig_y, block2*4, block2, sig_c)
    rect(d, ax, sig_y, block2, block2*5, sig_c)
    rect(d, ax+block2*3, sig_y, block2, block2*5, sig_c)
    rect(d, ax, sig_y+block2*2, block2*4, block2, sig_c)
    # L
    glx = 136
    rect(d, glx, sig_y, block2, block2*5, sig_c)
    rect(d, glx, sig_y+block2*4, block2*4, block2, sig_c)

    # === Subtitle line ===
    hline(d, 50, 76, W-100, C["wall_dark"])
    # Decorative dots — red accents instead of green
    for dx in [60, W//2, W-61]:
        rect(d, dx, 75, 2, 3, C["red_v_dim"])

    # === Bottom decoration with subtle warning ===
    hline(d, 30, 85, W-60, C["red_v_dim"])
    # Small red pulse dots along bottom line
    for pulse_x in [50, 80, 110, 140]:
        pixel(d, pulse_x, 85, C["red_dim"])

    # === Bottom corner: faint "3:00 AM" ===
    hline(d, W-24, H-6, 10, C["red_v_dim"])

    # Glows — shifted mood: cooler cyan up top, ominous red undertone
    add_glow(img, W//2, 35, 50, (20, 60, 70), 0.12)
    add_glow(img, W//2, 62, 40, (15, 45, 22), 0.12)
    # Subtle red underglow
    add_glow(img, W//2, H, 60, (30, 5, 5), 0.1)

    add_noise(img, 4)
    img.save(f"{OUTPUT_DIR}/title.png")
    print("  ✓ title.png")


if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating high-res scene images (200x100)...")
    generate_bedroom()
    generate_prod_server()
    generate_code_review()
    generate_supply_chain()
    generate_the_mirror()
    generate_title()
    print("\nDone! Images saved to", OUTPUT_DIR)
