#!/usr/bin/env python3
"""Generate high-res pixel art scenes for the CLI puzzle game."""

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


def draw_brick_wall(d, x, y, w, h, c1, c2, c3):
    """Draw a brick pattern wall section."""
    rect(d, x, y, w, h, c1)
    brick_h = 4
    brick_w = 8
    for row in range((h // brick_h) + 1):
        by = y + row * brick_h
        offset = (brick_w // 2) if row % 2 else 0
        # Mortar line
        hline(d, x, by, w, c2)
        for col in range(-1, (w // brick_w) + 2):
            bx = x + col * brick_w + offset
            if x <= bx < x + w:
                vline(d, bx, by, brick_h, c2)
            # Brick highlight
            if x <= bx+1 < x+w and by+1 < y+h:
                hline(d, bx+1, by+1, min(brick_w-2, x+w-bx-1), c3)


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


def generate_locked_room():
    """Scene 1: Dark locked room with terminal, lamp, and iron door."""
    img, d = create_image()

    # === Back wall - brick pattern ===
    draw_brick_wall(d, 0, 0, W, 55, C["wall_dark"], C["wall_v_dark"], C["wall"])

    # Ceiling line
    rect(d, 0, 0, W, 3, C["wall"])
    rect(d, 0, 0, W, 1, C["wall_light"])

    # === Floor ===
    rect(d, 0, 70, W, 30, C["floor_dark"])
    # Floor tiles with perspective lines
    for i in range(0, W, 16):
        vline(d, i, 70, 30, C["floor_v_dark"])
    for j in range(70, H, 5):
        hline(d, 0, j, W, C["floor_v_dark"])
    # Floor highlight strip
    rect(d, 0, 70, W, 2, C["floor_light"])

    # === Pipes on ceiling ===
    for py in [4, 7]:
        hline(d, 0, py, W, C["pipe"])
        hline(d, 0, py+1, W, C["pipe_dark"])
        hline(d, 0, py+2, W, C["pipe"])
    # Pipe joints
    for px in [30, 80, 130, 170]:
        rect(d, px, 3, 5, 8, C["pipe_hi"])
        rect(d, px+1, 3, 3, 8, C["pipe"])

    # === Cables hanging on left wall ===
    for cx in [6, 10, 13]:
        for cy in range(12, 60, 2):
            pixel(d, cx + (cy % 3), cy, C["cable"])
            pixel(d, cx + (cy % 3) + 1, cy, C["cable2"])

    # === Lamp (left side) ===
    # Pole
    rect(d, 28, 30, 2, 40, C["metal_dark"])
    rect(d, 29, 30, 1, 40, C["metal"])
    # Base
    rect(d, 22, 68, 16, 3, C["metal_dark"])
    rect(d, 24, 68, 12, 2, C["metal"])
    # Shade
    rect(d, 20, 26, 20, 5, C["amber_v_dim"])
    rect(d, 22, 27, 16, 3, C["amber_dim"])
    rect(d, 24, 28, 12, 1, C["amber"])
    # Bulb
    rect(d, 27, 30, 6, 2, C["amber"])

    # === Terminal (center) ===
    draw_monitor(d, 65, 28, 40, 28, (10, 22, 15))
    # Screen text
    for i, lw in enumerate([18, 12, 22, 8, 16, 14]):
        ty = 36 + i * 3
        hline(d, 72, ty, lw, C["green_dim"])
    # Cursor
    rect(d, 72, 54, 3, 2, C["green_bright"])
    # Keyboard
    rect(d, 68, 61, 34, 5, C["metal_dark"])
    rect(d, 69, 62, 32, 3, C["metal"])
    for kx in range(70, 100, 3):
        rect(d, kx, 62, 2, 1, C["metal_light"])
        rect(d, kx, 64, 2, 1, C["metal_light"])
    # Desk
    rect(d, 58, 58, 54, 3, C["metal"])
    rect(d, 58, 58, 54, 1, C["metal_light"])
    rect(d, 60, 61, 3, 10, C["metal_dark"])
    rect(d, 108, 61, 3, 10, C["metal_dark"])

    # === Paper/note on desk ===
    rect(d, 114, 55, 10, 8, C["white_dim"])
    rect(d, 114, 55, 10, 2, C["white"])
    hline(d, 115, 57, 7, C["metal"])
    hline(d, 115, 59, 5, C["metal"])
    hline(d, 115, 61, 6, C["metal"])

    # === Iron door (right side) ===
    # Door frame
    rect(d, 142, 10, 40, 61, C["metal_dark"])
    rect(d, 143, 10, 38, 1, C["metal_light"])
    vline(d, 142, 10, 61, C["metal_light"])
    vline(d, 181, 10, 61, C["metal"])
    # Door body
    rect(d, 145, 12, 34, 57, C["door_dark"])
    rect(d, 146, 13, 32, 55, C["door"])
    # Door panels (recessed)
    rect(d, 149, 16, 26, 18, C["door_dark"])
    rect(d, 150, 17, 24, 16, C["door_v_dark"])
    rect(d, 149, 40, 26, 18, C["door_dark"])
    rect(d, 150, 41, 24, 16, C["door_v_dark"])
    # Electronic lock
    rect(d, 174, 33, 6, 8, C["metal_light"])
    rect(d, 175, 34, 4, 6, C["metal_dark"])
    rect(d, 176, 36, 2, 2, C["red"])  # Red LED
    # Handle
    rect(d, 173, 44, 2, 5, C["metal_light"])
    rect(d, 173, 44, 2, 1, C["metal_hi"])
    # Rivets
    for ry in [14, 30, 48, 64]:
        for rx in [147, 175]:
            rect(d, rx, ry, 2, 2, C["metal"])

    # === Water stain on wall ===
    random.seed(99)
    for i in range(40):
        wx = 130 + random.randint(-3, 3)
        wy = 20 + i
        pixel(d, wx, wy, C["wall_light"])
        pixel(d, wx+1, wy, C["wall"])

    # === Lighting effects ===
    add_glow(img, 29, 30, 35, (80, 70, 30), 0.3)  # Lamp glow
    add_glow(img, 85, 45, 25, (20, 60, 30), 0.25)  # Monitor glow
    add_glow(img, 177, 37, 10, (80, 15, 15), 0.3)   # Lock LED glow

    add_noise(img, 5)
    img.save(f"{OUTPUT_DIR}/locked_room.png")
    print("  ✓ locked_room.png")


def generate_server_room():
    """Scene 2: Server room with 4 racks, one still running."""
    img, d = create_image()

    # === Background ===
    rect(d, 0, 0, W, H, C["wall_v_dark"])
    # Ceiling
    rect(d, 0, 0, W, 4, C["wall"])
    rect(d, 0, 0, W, 1, C["wall_light"])

    # Floor - reflective industrial tile
    rect(d, 0, 75, W, 25, C["floor_dark"])
    for i in range(0, W, 20):
        rect(d, i, 75, 10, 25, C["floor"])
    for j in range(75, H, 6):
        hline(d, 0, j, W, C["floor_v_dark"])
    rect(d, 0, 75, W, 1, C["floor_hi"])

    # Cable trays on ceiling
    rect(d, 0, 4, W, 3, C["pipe_dark"])
    rect(d, 0, 5, W, 1, C["pipe"])

    # === Four server racks ===
    rack_x = [8, 50, 92, 134]
    rack_w, rack_h = 30, 60

    for i, rx in enumerate(rack_x):
        is_on = (i == 3)

        # Rack frame
        body = C["metal"] if is_on else C["metal_dark"]
        rect(d, rx, 14, rack_w, rack_h, (28, 32, 38))
        rect(d, rx+1, 15, rack_w-2, rack_h-2, body)

        # Front panel sections
        for row in range(6):
            by = 18 + row * 8
            panel_c = C["metal"] if is_on else (48, 52, 56)
            rect(d, rx+3, by, rack_w-6, 6, panel_c)
            rect(d, rx+3, by, rack_w-6, 1, C["metal_light"] if is_on else C["metal_dark"])

            # LEDs
            for led_x in range(rx+5, rx+12, 3):
                if is_on:
                    colors = [C["green_bright"], C["green"], C["blue_led"]]
                    pixel(d, led_x, by+2, colors[(led_x + row) % 3])
                    pixel(d, led_x, by+3, colors[(led_x + row + 1) % 3])
                else:
                    pixel(d, led_x, by+2, (35, 35, 35))
                    pixel(d, led_x, by+3, (35, 35, 35))

            # Drive slots
            for slot_x in range(rx+15, rx+rack_w-4, 4):
                rect(d, slot_x, by+1, 3, 4, C["metal_dark"] if is_on else (38, 40, 44))

        # Ventilation bottom
        for vy in range(66, 72):
            for vx in range(rx+3, rx+rack_w-3, 3):
                pixel(d, vx, vy, C["wall_v_dark"])

        # Rack feet
        rect(d, rx+2, 74, 5, 2, C["metal_dark"])
        rect(d, rx+rack_w-7, 74, 5, 2, C["metal_dark"])

        # Cable from ceiling
        vline(d, rx+rack_w//2, 7, 8, C["cable"])

    # === Glow from active rack ===
    add_glow(img, 149, 45, 40, (20, 80, 40), 0.2)

    # === Monitor on stand (near srv04) ===
    draw_monitor(d, 140, 56, 24, 16, (10, 22, 15))
    # Screen text
    hline(d, 146, 62, 10, C["green_dim"])
    hline(d, 146, 65, 14, C["green_dim"])
    hline(d, 146, 68, 4, C["green"])

    # === Whiteboard (right wall) ===
    rect(d, 174, 14, 22, 30, C["white_dim"])
    rect(d, 174, 14, 22, 2, C["metal"])
    rect(d, 174, 14, 1, 30, C["metal"])
    rect(d, 195, 14, 1, 30, C["metal"])
    # Text on whiteboard
    for wy, wlen in [(19, 12), (22, 10), (25, 14), (28, 12)]:
        hline(d, 177, wy, wlen, C["metal"])
    # Last line in red
    hline(d, 177, 31, 16, C["red"])
    hline(d, 177, 34, 10, C["red_dim"])

    # === Labels under racks ===
    # Floor reflections from active rack LEDs
    for fx in range(135, 165):
        for fy in range(76, 80):
            pixel(d, fx, fy, C["green_v_dim"])

    add_noise(img, 4)
    img.save(f"{OUTPUT_DIR}/server_room.png")
    print("  ✓ server_room.png")


def generate_encrypted_terminal():
    """Scene 3: Dark void with single glowing encrypted terminal."""
    img, d = create_image()

    # Very dark background with subtle texture
    rect(d, 0, 0, W, H, C["black"])
    random.seed(77)
    for _ in range(300):
        x, y = random.randint(0, W-1), random.randint(0, H-1)
        pixel(d, x, y, C["black2"])

    # === Central monitor — the sole light source ===
    mx, my = W//2 - 25, 18
    mw, mh = 50, 40

    # Monitor
    rect(d, mx, my, mw, mh, C["metal_dark"])
    rect(d, mx+1, my+1, mw-2, mh-2, C["metal"])
    rect(d, mx+3, my+3, mw-6, mh-6, C["black"])
    rect(d, mx+4, my+4, mw-8, mh-8, (8, 5, 5))

    # Screen content
    sx, sy = mx+5, my+5
    sw, sh = mw-10, mh-10

    # ENCRYPTED warning bar
    rect(d, sx, sy+2, sw, 5, C["red_dim"])
    rect(d, sx+1, sy+3, sw-2, 3, C["red_v_dim"])
    hline(d, sx+4, sy+4, sw-8, C["red"])

    # File list
    files_y = sy + 12
    for i, fw in enumerate([18, 16, 22]):
        fy = files_y + i * 4
        pixel(d, sx+2, fy, C["amber"])
        pixel(d, sx+3, fy, C["amber"])
        hline(d, sx+5, fy, fw, C["amber_dim"])

    # Cursor
    rect(d, sx+2, files_y + 16, 4, 2, C["amber"])

    # Monitor stand
    rect(d, W//2-4, my+mh, 8, 4, C["metal_dark"])
    rect(d, W//2-8, my+mh+4, 16, 2, C["metal"])

    # Desk surface
    rect(d, mx-20, my+mh+6, mw+40, 3, C["metal_dark"])
    rect(d, mx-20, my+mh+6, mw+40, 1, C["metal"])

    # Keyboard
    rect(d, mx+5, my+mh+7, mw-10, 4, C["metal_dark"])
    for kx in range(mx+7, mx+mw-7, 3):
        pixel(d, kx, my+mh+8, C["metal"])
        pixel(d, kx, my+mh+10, C["metal"])

    # Desk legs
    rect(d, mx-18, my+mh+9, 3, 25, C["metal_dark"])
    rect(d, mx+mw+15, my+mh+9, 3, 25, C["metal_dark"])

    # === Red LED on floor ===
    pixel(d, W//2, 88, C["red"])
    pixel(d, W//2-1, 89, C["red_dim"])
    pixel(d, W//2+1, 89, C["red_dim"])

    # === Glow effects ===
    add_glow(img, W//2, my+mh//2, 55, (50, 20, 15), 0.2)  # Red-ish monitor glow
    add_glow(img, W//2, 88, 12, (80, 15, 15), 0.3)  # LED glow

    add_noise(img, 3)
    img.save(f"{OUTPUT_DIR}/encrypted_terminal.png")
    print("  ✓ encrypted_terminal.png")


def generate_final_message():
    """Scene 4: Glitched screen, red warning, everything dying."""
    img, d = create_image()

    # Total darkness
    rect(d, 0, 0, W, H, C["black"])

    # === Glitching monitor filling most of view ===
    mx, my = 20, 5
    mw, mh = W-40, H-10

    # Monitor frame (distorted)
    rect(d, mx, my, mw, mh, (40, 20, 20))
    rect(d, mx+2, my+2, mw-4, mh-4, C["black"])

    # Screen - dark red tint
    rect(d, mx+3, my+3, mw-6, mh-6, (12, 4, 4))

    # Scan lines
    for y in range(my+3, my+mh-3, 2):
        hline(d, mx+3, y, mw-6, (18, 6, 6))

    # CONNECTION TERMINATED
    bar_y = my + 20
    rect(d, mx+20, bar_y, mw-40, 7, C["red_dim"])
    hline(d, mx+25, bar_y+3, mw-50, C["red"])

    # "你不该打开这个"
    msg_y = my + 38
    rect(d, mx+20, msg_y, mw-40, 7, (35, 12, 12))
    hline(d, mx+30, msg_y+3, mw-60, C["red"])

    # Source IP
    hline(d, mx+30, msg_y+14, 25, C["red_dim"])

    # SIGNAL LOST
    hline(d, mx+30, msg_y+20, 20, (65, 22, 22))

    # === Glitch artifacts ===
    random.seed(42)
    # Horizontal glitch bands
    for _ in range(8):
        gy = random.randint(my+5, my+mh-8)
        gx = random.randint(mx+3, mx+mw//2)
        gw = random.randint(20, 80)
        rect(d, gx, gy, gw, 2, (random.randint(30, 60), random.randint(5, 15), random.randint(5, 15)))

    # Static noise
    for _ in range(500):
        x = random.randint(mx+3, mx+mw-4)
        y = random.randint(my+3, my+mh-4)
        v = random.randint(15, 55)
        pixel(d, x, y, (v, v//4, v//4))

    # Pixel corruption blocks
    for _ in range(15):
        bx = random.randint(mx+10, mx+mw-20)
        by = random.randint(my+10, my+mh-15)
        bw = random.randint(3, 12)
        bh = random.randint(2, 5)
        rect(d, bx, by, bw, bh, (random.randint(40, 80), 0, 0))

    # === Glow ===
    add_glow(img, W//2, H//2, 60, (60, 10, 10), 0.25)

    add_noise(img, 6)
    img.save(f"{OUTPUT_DIR}/final_message.png")
    print("  ✓ final_message.png")


def generate_title():
    """Title screen with game logo."""
    img, d = create_image()

    # Dark gradient background
    for y in range(H):
        v = max(0, 18 - y // 5)
        hline(d, 0, y, W, (v, v + 6, v + 14))

    # === Decorative top line ===
    hline(d, 30, 10, W-60, C["cyan_dim"])
    pixel(d, 30, 10, C["cyan"])
    pixel(d, W-31, 10, C["cyan"])

    # === "OFFLINE" in large pixel blocks ===
    block = 5
    letters_y = 20
    # O
    ox = 20
    rect(d, ox, letters_y, block*4, block, C["cyan"])
    rect(d, ox, letters_y+block*4, block*4, block, C["cyan"])
    rect(d, ox, letters_y, block, block*5, C["cyan"])
    rect(d, ox+block*3, letters_y, block, block*5, C["cyan"])
    # F
    fx = 44
    rect(d, fx, letters_y, block*4, block, C["cyan"])
    rect(d, fx, letters_y, block, block*5, C["cyan"])
    rect(d, fx, letters_y+block*2, block*3, block, C["cyan"])
    # F
    f2x = 68
    rect(d, f2x, letters_y, block*4, block, C["cyan"])
    rect(d, f2x, letters_y, block, block*5, C["cyan"])
    rect(d, f2x, letters_y+block*2, block*3, block, C["cyan"])
    # L
    lx = 92
    rect(d, lx, letters_y, block, block*5, C["cyan"])
    rect(d, lx, letters_y+block*4, block*4, block, C["cyan"])
    # I
    ix = 116
    rect(d, ix, letters_y, block*4, block, C["cyan"])
    rect(d, ix+block*1.5, letters_y, block, block*5, C["cyan"])
    rect(d, ix, letters_y+block*4, block*4, block, C["cyan"])
    # N
    nx = 140
    rect(d, nx, letters_y, block, block*5, C["cyan"])
    rect(d, nx+block*3, letters_y, block, block*5, C["cyan"])
    for i in range(4):
        rect(d, int(nx+block+i*block*0.7), letters_y+block+i*block, block, block, C["cyan"])
    # E
    ex = 164
    rect(d, ex, letters_y, block*4, block, C["cyan"])
    rect(d, ex, letters_y, block, block*5, C["cyan"])
    rect(d, ex, letters_y+block*2, block*3, block, C["cyan"])
    rect(d, ex, letters_y+block*4, block*4, block, C["cyan"])

    # === "SIGNAL" in green ===
    sig_y = 52
    block2 = 4
    # S
    sx = 40
    rect(d, sx, sig_y, block2*4, block2, C["green"])
    rect(d, sx, sig_y+block2, block2, block2, C["green"])
    rect(d, sx, sig_y+block2*2, block2*4, block2, C["green"])
    rect(d, sx+block2*3, sig_y+block2*3, block2, block2, C["green"])
    rect(d, sx, sig_y+block2*4, block2*4, block2, C["green"])
    # I
    si = 60
    rect(d, si+block2, sig_y, block2, block2*5, C["green"])
    rect(d, si, sig_y, block2*3, block2, C["green"])
    rect(d, si, sig_y+block2*4, block2*3, block2, C["green"])
    # G
    gx = 76
    rect(d, gx, sig_y, block2*4, block2, C["green"])
    rect(d, gx, sig_y, block2, block2*5, C["green"])
    rect(d, gx, sig_y+block2*4, block2*4, block2, C["green"])
    rect(d, gx+block2*3, sig_y+block2*2, block2, block2*3, C["green"])
    rect(d, gx+block2*2, sig_y+block2*2, block2, block2, C["green"])
    # N
    gnx = 96
    rect(d, gnx, sig_y, block2, block2*5, C["green"])
    rect(d, gnx+block2*3, sig_y, block2, block2*5, C["green"])
    for i in range(3):
        rect(d, gnx+block2+i*block2, sig_y+block2+i*block2, block2, block2, C["green"])
    # A
    ax = 116
    rect(d, ax, sig_y, block2*4, block2, C["green"])
    rect(d, ax, sig_y, block2, block2*5, C["green"])
    rect(d, ax+block2*3, sig_y, block2, block2*5, C["green"])
    rect(d, ax, sig_y+block2*2, block2*4, block2, C["green"])
    # L
    glx = 136
    rect(d, glx, sig_y, block2, block2*5, C["green"])
    rect(d, glx, sig_y+block2*4, block2*4, block2, C["green"])

    # === Subtitle line ===
    hline(d, 50, 76, W-100, C["wall"])
    # Decorative dots
    for dx in [60, W//2, W-61]:
        rect(d, dx, 75, 2, 3, C["green_dim"])

    # === "第一章：离线信号" would be text overlay in app ===

    # === Bottom decoration ===
    hline(d, 30, 85, W-60, C["cyan_dim"])

    # Glows
    add_glow(img, W//2, 35, 50, (30, 80, 90), 0.15)
    add_glow(img, W//2, 62, 40, (20, 60, 30), 0.15)

    add_noise(img, 4)
    img.save(f"{OUTPUT_DIR}/title.png")
    print("  ✓ title.png")


if __name__ == "__main__":
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Generating high-res scene images (200x100)...")
    generate_locked_room()
    generate_server_room()
    generate_encrypted_terminal()
    generate_final_message()
    generate_title()
    print("\nDone! Images saved to", OUTPUT_DIR)
