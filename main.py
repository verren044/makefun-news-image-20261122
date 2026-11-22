#!/usr/bin/env python3
"""THE WORLD, SUNDAY 22 NOVEMBER 2026.

A dense newspaper front page summing up the world's news of Sunday
22 November 2026: 52 verified stories (13 anchor cards with drawn
picture strips, a world map with numbered story sites, a UTC timeline
strip, a by-region index, and 39 briefs). Pure Python 3.13 standard
library only, deterministic, no network, no randomness, no external
files. Every story happened, or was first reported, on 22 November
2026, cross-checked against the day's reporting (BBC, Reuters, CNN,
The Times, SimpleLife.news, C54, CareerIndia, ATP Tour, IANS,
The Silk Paradox briefing, AsiaToday, Bytes Europe).
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (18, 18, 18)
RED = (176, 32, 32)
GREY = (96, 92, 84)
BLUE = (38, 84, 140)
OCEAN = (52, 110, 168)
SKY = (168, 198, 224)
NIGHT = (16, 26, 52)
SEA = (14, 38, 70)
SAND = (214, 186, 138)
GREEN = (74, 120, 66)
YELLOW = (232, 184, 48)
ORANGE = (226, 106, 28)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT = (226, 222, 210)
STEEL = (90, 96, 110)

# ------------------------------------------------------------------ buffer
BUF = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = yy * W * 3
        for xx in range(x0, x1):
            i = base + xx * 3
            BUF[i] = c[0]
            BUF[i + 1] = c[1]
            BUF[i + 2] = c[2]


def hline(x, y, w, c):
    rect(x, y, w, 1, c)


def vline(x, y, h, c):
    rect(x, y, 1, h, c)


def frame(x, y, w, h, c, t=1):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def ellipse(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy * dy) / float(ry * ry)
        if t < 0:
            continue
        dx = int(rx * math.sqrt(t))
        rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)


def circle(cx, cy, r, c):
    ellipse(cx, cy, r, r, c)


def line(x0, y0, x1, y1, c, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    half = thick // 2
    while True:
        rect(x - half, y - half, thick, thick, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def poly(points, c):
    """Scanline fill of a polygon given as [(x, y), ...]."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0, y1 = min(ys), max(ys)
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, ya = points[i]
            x1, yb = points[(i + 1) % n]
            if ya == yb:
                continue
            if (ya <= y < yb) or (yb <= y < ya):
                t = (y - ya) / float(yb - ya)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = int(math.ceil(xs[i]))
            xb = int(math.floor(xs[i + 1]))
            if xb >= xa:
                rect(xa, y, xb - xa + 1, 1, c)


def star(cx, cy, r_outer, r_inner, c, rot=-math.pi / 2):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = rot + i * math.pi / 5
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    poly(pts, c)


# ------------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits. Uppercase only.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("missing glyph for %r" % ch)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_centered(cx, y, s, scale, c):
    x = cx - text_width(s, scale) // 2
    draw_text(x, y, s, scale, c)
    return x


# ------------------------------------------------------------------- PNG writer
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += BUF[y * W * 3:(y + 1) * W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ------------------------------------------------------------- mini scenes
# Each draws a small picture strip inside (x, y, w, h); h is 36 for the
# four anchor rows and 56 for the row-5 Medvedev card.


def mini_poland(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in ((18, 7), (58, 13), (118, 5), (198, 11), (258, 7),
                   (298, 15), (88, 19), (178, 17)):
        set_px(x + sx, y + sy, WHITE)
    # Polish flag on a pole, left
    vline(x + 22, y + 4, 26, WHITE)
    rect(x + 23, y + 4, 34, 7, WHITE)
    rect(x + 23, y + 11, 34, 7, RED)
    # two missile streaks falling to the right
    line(x + 120, y + 2, x + 210, y + 20, ORANGE, 2)
    line(x + 180, y + 2, x + 250, y + 16, ORANGE, 2)
    # impact burst
    ex, ey = x + w - 52, y + h - 12
    star(ex, ey, 11, 4, ORANGE)
    star(ex, ey, 6, 2, YELLOW)
    circle(ex - 34, ey - 2, 5, (90, 88, 84))
    # ground line
    rect(x, y + h - 3, w, 3, (52, 52, 60))


def mini_kryvyi(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in ((18, 7), (58, 13), (118, 5), (198, 11), (258, 7),
                   (298, 15), (88, 19), (178, 17)):
        set_px(x + sx, y + sy, WHITE)
    base = y + h - 3
    heights = [14, 22, 11, 18, 24]
    bw = w // 5
    for i, bh in enumerate(heights):
        bx = x + i * bw
        rect(bx + 2, base - bh, bw - 4, bh, (52, 52, 60))
        for wy in range(base - bh + 5, base - 3, 8):
            set_px(bx + 8, wy, YELLOW)
    # double-tap: two blasts, one above the other in time
    star(x + 110, y + 12, 10, 4, ORANGE)
    star(x + 110, y + 12, 6, 2, YELLOW)
    star(x + 210, y + 18, 8, 3, ORANGE)
    star(x + 210, y + 18, 4, 2, YELLOW)
    line(x + 60, y + 2, x + 110, y + 10, ORANGE, 2)
    line(x + 260, y + 2, x + 210, y + 16, ORANGE, 2)


def mini_khasab(x, y, w, h):
    rect(x, y, w, h, (24, 68, 118))
    rect(x, y + h - 14, w, 14, (16, 44, 84))
    # tanker hull
    rect(x + 40, y + h - 16, 150, 10, (28, 28, 34))
    rect(x + 40, y + h - 19, 150, 3, (70, 70, 78))
    rect(x + 158, y + h - 30, 26, 12, WHITE)
    rect(x + 52, y + h - 26, 10, 8, (200, 60, 40))
    # fire plume from the deck
    star(x + 120, y + h - 20, 7, 3, ORANGE)
    star(x + 120, y + h - 20, 4, 2, YELLOW)
    # incoming projectile streak
    line(x + w - 20, y + 2, x + 130, y + 14, YELLOW, 2)
    # spiked mine in the water, right
    mx, my = x + w - 40, y + 10
    circle(mx, my, 5, INK)
    for dx, dy in ((-7, 0), (7, 0), (0, -7), (0, 7), (-5, -5), (5, -5),
                   (-5, 5), (5, 5)):
        line(mx, my, mx + dx, my + dy, INK, 1)


def mini_hodeidah(x, y, w, h):
    rect(x, y, w, h, (240, 214, 160))
    circle(x + w - 28, y + 9, 6, (240, 200, 110))
    base = y + h - 3
    # port cranes
    for cx0 in (30, 120, 210):
        vline(x + cx0, y + 8, base - (y + 8), (70, 78, 96))
        line(x + cx0, y + 8, x + cx0 + 34, y + 16, (70, 78, 96), 2)
        line(x + cx0 + 34, y + 16, x + cx0 + 34, y + 22, (70, 78, 96), 1)
    # docked ship
    rect(x + 60, base - 10, 90, 8, (110, 112, 120))
    rect(x + 70, base - 16, 20, 6, (110, 112, 120))
    # strike blast over the port
    star(x + w // 2 + 60, y + 12, 10, 4, ORANGE)
    star(x + w // 2 + 60, y + 12, 5, 2, YELLOW)
    rect(x, base, w, 3, (70, 78, 96))


def mini_cop31(x, y, w, h):
    rect(x, y, w, h, (210, 226, 210))
    cx, cy = x + 52, y + h // 2
    circle(cx, cy, 13, BLUE)
    ellipse(cx - 4, cy - 3, 5, 3, GREEN)
    ellipse(cx + 5, cy + 4, 4, 3, GREEN)
    line(cx - 13, cy, cx + 13, cy, WHITE, 1)
    # clock: talks into overtime
    ccx, ccy = x + 130, y + h // 2
    circle(ccx, ccy, 12, WHITE)
    frame(ccx - 12, ccy - 12, 25, 25, INK)
    line(ccx, ccy, ccx, ccy - 8, INK, 2)
    line(ccx, ccy, ccx + 7, ccy + 3, INK, 2)
    draw_text(x + 160, y + 12, "OVERTIME", 1, RED)
    # small flags row
    for i in range(4):
        fx = x + 168 + i * 34
        vline(fx, y + 24, 8, INK)
        cols = ((0, 60, 160), (255, 255, 255), (220, 0, 0))
        rect(fx + 1, y + 24, 20, 3, cols[i % 3])
        rect(fx + 1, y + 27, 20, 3, cols[(i + 1) % 3])
        rect(fx + 1, y + 30, 20, 3, cols[(i + 2) % 3])


def mini_markets(x, y, w, h):
    rect(x, y, w, h, WHITE)
    bars = [24, 20, 15, 11, 7]
    bw = (w - 30) // 5
    base = y + h - 4
    for i, bh in enumerate(bars):
        rect(x + 15 + i * bw, base - bh, bw - 4, bh, RED)
    line(x + 18, base - 24, x + w - 100, base - 10, INK, 2)
    draw_text(x + w - 96, y + 4, "-3.7 PC", 2, RED)


def mini_ukeu(x, y, w, h):
    rect(x, y, w, h, (24, 48, 120))
    cx, cy = x + 60, y + h // 2
    for i in range(12):
        a = i * math.pi / 6
        sx = cx + int(13 * math.cos(a))
        sy = cy + int(13 * math.sin(a))
        star(sx, sy, 3, 1, YELLOW)
    rect(x + 130, y + 6, 60, 10, (0, 60, 160))
    rect(x + 130, y + 16, 60, 10, WHITE)
    rect(x + 130, y + 26, 60, 10, (200, 0, 0))
    line(x + 130, y + 6, x + 160, y + 16, RED, 2)
    line(x + 130, y + 16, x + 160, y + 6, RED, 2)
    draw_text(x + 205, y + 12, "100K", 2, WHITE)
    rect(x + 130, y + h - 6, 160, 3, YELLOW)


def mini_peru(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + 24, y + 8, 5, (240, 214, 120))
    # Andes ridge
    poly([(x, y + h), (x + 60, y + 6), (x + 120, y + h)], (96, 96, 98))
    poly([(x + 90, y + h), (x + 170, y + 2), (x + 250, y + h)], (120, 118, 116))
    poly([(x + 150, y + 14), (x + 170, y + 2), (x + 190, y + 14)], WHITE)
    # shaking building with crack
    bx = x + w - 70
    rect(bx, y + h - 20, 40, 17, (176, 120, 80))
    line(bx + 8, y + h - 20, bx + 20, y + h - 10, INK, 1)
    line(bx + 20, y + h - 10, bx + 12, y + h - 3, INK, 1)
    for dx in range(0, 60, 12):
        line(x + dx, y + h - 4, x + dx + 6, y + h - 8, (90, 88, 84), 1)
    draw_text(x + 12, y + 4, "6.8", 2, INK)


def mini_india(x, y, w, h):
    rect(x, y, w, h, WHITE)
    bars = [8, 13, 10, 18, 26]
    bw = (w - 30) // 5
    base = y + h - 4
    for i, bh in enumerate(bars):
        rect(x + 15 + i * bw, base - bh, bw - 4, bh, GREEN)
    line(x + 18, base - 8, x + w - 18, base - 28, INK, 2)
    line(x + w - 18, base - 28, x + w - 32, base - 28, INK, 2)
    line(x + w - 18, base - 28, x + w - 18, base - 16, INK, 2)
    draw_text(x + 15, y + 4, "RECORD", 2, INK)


def mini_rikers(x, y, w, h):
    rect(x, y, w, h, (40, 60, 90))
    # prison bars
    for i in range(9):
        bx = x + 14 + i * 32
        vline(bx, y + 4, h - 8, (120, 150, 190))
    hline(x, y + 6, w, (120, 150, 190))
    hline(x, y + h - 7, w, (120, 150, 190))
    # open gate: one bar swung aside
    line(x + 46, y + 6, x + 70, y + h - 7, YELLOW, 3)
    draw_text(x + w - 110, y + 12, "2032", 2, WHITE)


def mini_akvan(x, y, w, h):
    rect(x, y, w, h, (40, 60, 90))
    cx, cy = x + w // 2 - 30, y + h // 2
    for r in (16, 11, 6):
        circle(cx, cy, r, SKY)
        circle(cx, cy, r - 2, (40, 60, 90))
    circle(cx, cy, 3, WHITE)
    for dx in range(0, w - 10, 14):
        line(x + dx, y + h - 12, x + dx + 5, y + h - 6, (120, 150, 190), 1)
    rect(x + w - 92, y + h - 14, 84, 10, (240, 220, 180))
    for i in range(6):
        rect(x + w - 88 + i * 13, y + h - 12, 8, 6, INK)
    draw_text(x + w - 88, y + 6, "LANDFALL", 1, YELLOW)


def mini_rahul(x, y, w, h):
    rect(x, y, w, h, GREEN)
    poly([(x, y + h), (x + w // 2, y + 4), (x + w, y + h)], (196, 164, 112))
    line(x + w // 2, y + 4, x + w // 2, y + h - 2, WHITE, 1)
    line(x + w // 2, y + 4, x + 8, y + h - 2, WHITE, 1)
    line(x + w // 2, y + 4, x + w - 8, y + h - 2, WHITE, 1)
    # stumps, right
    for sx in (w - 60, w - 54, w - 48):
        vline(x + sx, y + h - 14, 11, YELLOW)
    hline(x + w - 60, y + h - 15, 13, YELLOW)
    circle(x + 44, y + h - 8, 5, WHITE)
    circle(x + w - 44, y + h - 8, 5, WHITE)
    draw_text(x + w // 2 - 18, y + 12, "100", 2, INK)


def mini_turin(x, y, w, h):
    rect(x, y, w, h, (46, 110, 66))
    rect(x + 10, y + 6, w - 20, h - 12, (66, 140, 86))
    frame(x + 10, y + 6, w - 20, h - 12, WHITE)
    vline(x + w // 2, y + 8, h - 16, WHITE)
    hline(x + 10, y + h // 2 - 1, w - 20, WHITE)
    line(x + 10, y + 6, x + w - 10, y + h - 6, WHITE, 1)
    circle(x + w - 60, y + 14, 6, YELLOW)
    circle(x + w - 62, y + 12, 2, WHITE)
    draw_text(x + 20, y + h - 22, "6-3 6-4", 1, WHITE)



def mini_sparta(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in ((18, 7), (58, 13), (118, 5), (198, 11), (258, 7),
                   (298, 15), (88, 19), (178, 17)):
        set_px(x + sx, y + sy, WHITE)
    # dark sea
    rect(x, y + h - 12, w, 12, SEA)
    # cargo ship, listing, on fire
    rect(x + 90, y + h - 18, 130, 10, (28, 28, 34))
    rect(x + 100, y + h - 24, 90, 6, (70, 70, 78))
    rect(x + 170, y + h - 32, 22, 10, WHITE)
    star(x + 130, y + h - 22, 9, 3, ORANGE)
    star(x + 130, y + h - 22, 5, 2, YELLOW)
    star(x + 200, y + h - 20, 6, 2, ORANGE)
    # two drones above with streaks
    for dx, dy in ((60, 6), (250, 8)):
        line(x + dx - 6, y + dy, x + dx + 6, y + dy, WHITE, 1)
        line(x + dx, y + dy - 6, x + dx, y + dy + 6, WHITE, 1)
        line(x + dx, y + dy + 6, x + dx + 24, y + dy + 16, YELLOW, 1)
    # Finnish coast, right
    poly([(x + w - 60, y + h), (x + w - 20, y + 8), (x + w, y + 12),
          (x + w, y + h)], (52, 72, 52))
    draw_text(x + 8, y + 4, "GULF OF FINLAND", 1, WHITE)


def mini_mexico(x, y, w, h):
    rect(x, y, w, h, (32, 22, 16))
    for sx, sy in ((18, 7), (58, 13), (118, 5), (198, 11), (258, 7),
                   (298, 15), (88, 19), (178, 17)):
        set_px(x + sx, y + sy, WHITE)
    # desert ground
    rect(x, y + h - 10, w, 10, (96, 74, 44))
    # helicopter with searchlight beam
    hx, hy = x + 90, y + 10
    ellipse(hx, hy, 16, 7, (70, 78, 96))
    rect(hx + 14, hy - 2, 34, 3, (70, 78, 96))
    rect(hx - 4, hy - 8, 10, 3, (70, 78, 96))
    poly([(hx - 6, hy + 6), (hx + 6, hy + 6), (hx + 46, y + h - 10),
          (hx + 10, y + h - 10)], (240, 220, 140))
    # burning roadblock truck
    rect(x + 210, y + h - 18, 60, 10, (120, 40, 30))
    rect(x + 222, y + h - 26, 22, 8, (90, 30, 22))
    star(x + 240, y + h - 24, 9, 3, ORANGE)
    star(x + 240, y + h - 24, 5, 2, YELLOW)
    # house raided, centre
    rect(x + 140, y + h - 24, 44, 16, (150, 120, 84))
    poly([(x + 138, y + h - 24), (x + 162, y + h - 32),
          (x + 186, y + h - 24)], (110, 40, 30))
    draw_text(x + 8, y + 4, "GUASAVE, SINALOA", 1, WHITE)


def mini_fbi(x, y, w, h):
    rect(x, y, w, h, (16, 26, 52))
    # server racks
    for i in range(3):
        rx = x + 16 + i * 74
        rect(rx, y + 6, 62, h - 12, (28, 44, 78))
        frame(rx, y + 6, 62, h - 12, (90, 110, 150))
        for j in range(3):
            ry = y + 12 + j * 9
            rect(rx + 6, ry, 30, 4, (40, 90, 60))
            set_px(rx + 44, ry + 1, (80, 220, 120))
            set_px(rx + 50, ry + 1, (220, 80, 80))
    # red warning banner
    rect(x + 240, y + 6, w - 248, 24, RED)
    draw_text(x + 248, y + 13, "BREACH?", 1, WHITE)


def mini_nvidia(x, y, w, h):
    rect(x, y, w, h, WHITE)
    # falling bars, steep drop
    bars = [26, 22, 16, 10, 4]
    bw = (w - 30) // 5
    base = y + h - 4
    for i, bh in enumerate(bars):
        rect(x + 15 + i * bw, base - bh, bw - 4, bh, RED)
    line(x + 18, base - 26, x + w - 100, base - 4, INK, 2)
    draw_text(x + w - 72, y + 4, "-14 PC", 2, RED)
    draw_text(x + w - 72, y + 22, "7 DAYS DOWN", 1, GREY)


def mini_kyiv(x, y, w, h):
    # Ukrainian flag bands
    rect(x, y, w, h // 2, (0, 90, 180))
    rect(x, y + h // 2, w, h - h // 2, (255, 215, 0))
    # white document with red seal, centre
    rect(x + 110, y + 4, 100, h - 8, WHITE)
    frame(x + 110, y + 4, 100, h - 8, INK)
    for i in range(3):
        hline(x + 118, y + 10 + i * 7, 60, GREY)
    circle(x + 196, y + h - 12, 5, RED)
    # pen across the paper
    line(x + 116, y + h - 6, x + 204, y + 8, INK, 2)
    draw_text(x + 8, y + 4, "NO PAPER YET", 1, WHITE)
    draw_text(x + 8, y + h - 12, "KYIV WAITS", 1, INK)


def mini_riemann(x, y, w, h):
    rect(x, y, w, h, (24, 52, 36))
    # chalk zeta curve
    prev = None
    for px in range(0, w - 90, 4):
        py = y + h // 2 - int(10 * math.sin(px / 18.0)) - px // 22
        if prev is not None:
            line(prev[0], prev[1], x + px, py, WHITE, 1)
        prev = (x + px, py)
    # critical line
    vline(x + w - 110, y + 4, h - 8, YELLOW)
    draw_text(x + w - 100, y + 6, "1/2", 1, YELLOW)
    draw_text(x + 10, y + 6, "ZETA(S)", 1, WHITE)
    draw_text(x + 10, y + h - 14, "PROOF?", 2, YELLOW)


def mini_boat(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + 24, y + 8, 5, (240, 214, 120))
    # river
    rect(x, y + h - 16, w, 16, (24, 68, 118))
    for dx in range(0, w, 26):
        hline(x + dx, y + h - 10, 14, (120, 170, 220))
    # capsized hull
    poly([(x + 110, y + h - 16), (x + 210, y + h - 16),
          (x + 195, y + h - 28), (x + 125, y + h - 28)], (120, 70, 40))
    # life ring floating
    circle(x + 250, y + h - 10, 7, ORANGE)
    circle(x + 250, y + h - 10, 3, (24, 68, 118))
    # bank with mourners' umbrellas
    for ux in (30, 60, 280):
        line(x + ux, y + h - 16, x + ux, y + h - 26, INK, 1)
        poly([(x + ux - 10, y + h - 26), (x + ux + 10, y + h - 26),
              (x + ux, y + h - 32)], INK)
    draw_text(x + 8, y + 4, "NIGERIA", 1, INK)


def mini_fire(x, y, w, h):
    rect(x, y, w, h, (40, 40, 48))
    # factory silhouette
    rect(x + 30, y + h - 20, 120, 16, (20, 20, 26))
    rect(x + 160, y + h - 26, 14, 22, (20, 20, 26))
    rect(x + 180, y + h - 26, 14, 22, (20, 20, 26))
    rect(x + 200, y + h - 14, 60, 10, (20, 20, 26))
    # flames
    star(x + 70, y + h - 22, 10, 4, ORANGE)
    star(x + 70, y + h - 22, 6, 2, YELLOW)
    star(x + 120, y + h - 20, 8, 3, ORANGE)
    star(x + 220, y + h - 18, 7, 3, ORANGE)
    # smoke
    for i, (sx, sy, r) in enumerate(((80, 8, 6), (100, 5, 5), (120, 9, 6),
                                     (230, 6, 5), (250, 10, 6))):
        circle(x + sx, y + sy, r, (120, 120, 128))
    draw_text(x + w - 96, y + 4, "39 MISSING", 1, WHITE)


def mini_cricket(x, y, w, h):
    rect(x, y, w, h, GREEN)
    poly([(x, y + h), (x + w // 2, y + 4), (x + w, y + h)], (196, 164, 112))
    line(x + w // 2, y + 4, x + w // 2, y + h - 2, WHITE, 1)
    line(x + w // 2, y + 4, x + 8, y + h - 2, WHITE, 1)
    line(x + w // 2, y + 4, x + w - 8, y + h - 2, WHITE, 1)
    # stumps, right
    for sx in (w - 60, w - 54, w - 48):
        vline(x + sx, y + h - 14, 11, YELLOW)
    hline(x + w - 60, y + h - 15, 13, YELLOW)
    # ball mid-air
    circle(x + 60, y + 12, 4, RED)
    circle(x + 60, y + 12, 1, WHITE)
    draw_text(x + w // 2 - 18, y + 12, "1-0", 2, INK)


def mini_turin_final(x, y, w, h):
    rect(x, y, w, h, (46, 110, 66))
    rect(x + 10, y + 6, w - 20, h - 12, (66, 140, 86))
    frame(x + 10, y + 6, w - 20, h - 12, WHITE)
    vline(x + w // 2, y + 8, h - 16, WHITE)
    hline(x + 10, y + h // 2 - 1, w - 20, WHITE)
    line(x + 10, y + 6, x + w - 10, y + h - 6, WHITE, 1)
    circle(x + w - 60, y + 14, 6, YELLOW)
    circle(x + w - 62, y + 12, 2, WHITE)
    draw_text(x + 20, y + h - 22, "7-6 6-4", 1, WHITE)


# world map panel ------------------------------------------------------------
CONTINENTS = {
    'NA': [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
           (-85, 70), (-75, 62), (-60, 55), (-55, 47), (-65, 44),
           (-75, 35), (-80, 25), (-90, 21), (-97, 16), (-105, 20),
           (-115, 28), (-125, 40), (-140, 60), (-155, 58)],
    'SA': [(-80, 10), (-60, 10), (-50, 0), (-40, -5), (-35, -10),
           (-40, -20), (-50, -30), (-60, -35), (-70, -40), (-70, -50),
           (-65, -55), (-70, -20), (-80, -5)],
    'AF': [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
           (35, 28), (40, 15), (43, 11), (48, 10), (40, 0), (35, -10),
           (30, -20), (25, -30), (20, -35), (15, -30), (12, -18),
           (9, -5), (9, 4), (-8, 4), (-13, 8)],
    'EU': [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 70),
           (25, 71), (18, 70), (12, 65), (5, 60), (0, 55), (-5, 50),
           (-10, 45)],
    'AS': [(30, 70), (40, 72), (60, 73), (90, 75), (120, 73), (150, 70),
           (170, 66), (180, 65), (170, 60), (160, 55), (140, 40),
           (130, 35), (127, 40), (120, 35), (110, 20), (105, 10),
           (100, 8), (95, 15), (90, 22), (85, 20), (80, 8), (75, 8),
           (70, 20), (60, 25), (55, 26), (50, 29), (45, 30), (40, 36),
           (35, 36), (30, 40)],
    'OC': [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38),
           (150, -37), (153, -27), (146, -19), (142, -11), (136, -12),
           (132, -11), (126, -14), (122, -17)],
}

# Numbered story sites on the map; the key lives in the index panel.
MAP_NUMBERS = [
    ("1", 22.0, 50.0),   # Rzeszow, Poland
    ("2", 27.5, 59.8),   # Gulf of Finland / Sparta II
    ("3", 30.7, 36.9),   # Antalya / COP31
    ("4", -108.5, 25.6), # Guasave, Sinaloa, Mexico
    ("5", 33.4, 47.9),   # Kryvyi Rih
    ("6", 7.5, 9.0),     # Nigeria
    ("7", 7.7, 45.1),    # Turin
]


def scene_map_numbered(x, y, w, h):
    rect(x, y, w, h, OCEAN)
    for lonlat in CONTINENTS.values():
        pts = []
        for lon, lat in lonlat:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((75 - lat) / 135.0 * h)
            pts.append((px, py))
        poly(pts, GREEN)
    for num, lon, lat in MAP_NUMBERS:
        mx = x + int((lon + 180) / 360.0 * w)
        my = y + int((75 - lat) / 135.0 * h)
        circle(mx, my, 4, RED)
        circle(mx, my, 2, WHITE)
        draw_text(mx + 6, my - 3, num, 1, WHITE)


# ------------------------------------------- masthead side boxes
# The masthead flanks (left x16-336, right x688-1008, y2-82) hold two
# drawn modules: BY THE NUMBERS and IN THEIR WORDS. Figures and quotes
# are from 22 Nov 2026 reporting (sources in BUILD_LOG.md). Boxes sit
# at (16, 2, 320, 80) and (688, 2, 320, 80): clear of the centred
# masthead (x353-671) and the dateline (x369-655), and clear of the
# masthead rule at y84.


NUMBERS_ROWS = [
    ("NVIDIA", "-14 PC", "DOWN"),
    ("S+P 500", "-3.7 PC", "DOWN"),
    ("BITCOIN", "UNDER $60K", "DOWN"),
    ("COP31 POWER", "35 PC 2035", None),
    ("ATP FINAL", "ZVEREV-ALCARAZ", None),
]


def draw_trend(x, y, up, c):
    """Small 7x7 up/down triangle marking a rising or falling figure."""
    if up:
        poly([(x + 3, y), (x + 7, y + 6), (x, y + 6)], c)
    else:
        poly([(x, y), (x + 7, y), (x + 3, y + 6)], c)


def draw_numbers_box(x, y, w, h):
    """Left masthead flank: BY THE NUMBERS, five figures of the day."""
    frame(x, y, w, h, INK)
    draw_text(x + 10, y + 7, "BY THE NUMBERS", 1, RED)
    hline(x + 10, y + 17, w - 20, LIGHT)
    for i, (label, value, trend) in enumerate(NUMBERS_ROWS):
        ty = y + 23 + i * 11
        draw_text(x + 10, ty, label, 1, INK)
        vx = x + w - 10 - text_width(value, 1)
        draw_text(vx, ty, value, 1, RED)
        if trend is not None:
            draw_trend(vx - 12, ty, trend == "UP",
                       BLUE if trend == "UP" else RED)


QUOTES = [
    ("RUTTE, ON POLAND",
     "DEFEND EVERY INCH OF POLISH TERRITORY"),
    ("STREETING, ON THE STRIKES",
     "OUTRAGEOUS PROVOCATION"),
    ("KURUM, ON THE COP31 DEAL",
     "A TEXT ALL PARTIES CAN AGREE ON"),
]


def wrap_words(s, max_chars):
    """Greedy word wrap; returns lines of at most max_chars characters."""
    lines = []
    cur = ""
    for word in s.split(" "):
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = word if not cur else cur + " " + word
    if cur:
        lines.append(cur)
    return lines


def draw_quotes_strip(x, y, w, h):
    """Right masthead flank: IN THEIR WORDS, three quotes of the day."""
    frame(x, y, w, h, INK)
    draw_text(x + 10, y + 6, "IN THEIR WORDS", 1, RED)
    hline(x + 10, y + 16, w - 20, LIGHT)
    ty = y + 19
    for who, quote in QUOTES:
        top = ty
        draw_text(x + 10, ty, who, 1, RED)
        ty += 10
        for qline in wrap_words(quote, 48):
            draw_text(x + 10, ty, qline, 1, INK)
            ty += 10
        rect(x + 5, top, 2, ty - top - 3, RED)


# ---------------------------------------------------------------------- layout
def anchor_card(x, y, w, h, kicker, headline, sub, scene_fn, scene_h):
    frame(x, y, w, h, INK)
    scene_fn(x + 1, y + 1, w - 2, scene_h)
    hline(x + 1, y + scene_h + 1, w - 2, INK)
    ty = y + scene_h + 6
    draw_text(x + 10, ty, kicker, 1, RED)
    draw_text(x + 10, ty + 12, headline, 2, INK)
    draw_text(x + 10, ty + 30, sub, 1, GREY)


def draw_timeline():
    line_y = 100
    hline(16, line_y, 992, INK)
    for hh, lab in ((0, "00"), (6, "06"), (12, "12"), (18, "18"), (24, "24")):
        tx = 16 + int(hh / 24 * 992)
        vline(tx, line_y - 4, 9, INK)
        lx = tx - text_width(lab, 1) // 2
        lx = max(16, min(lx, 1008 - text_width(lab, 1)))
        draw_text(lx, line_y + 6, lab, 1, GREY)
    events = [(0, "FBI HACK"), (3, "COP31 DEAL"), (6, "RUTTE WARSAW"),
              (9, "MEXICO RAID"), (12, "HORMUZ")]
    for hh, lab in events:
        ex = 16 + int(hh / 24 * 992)
        circle(ex, line_y, 4, RED)
        circle(ex, line_y, 2, WHITE)
        lx = ex - text_width(lab, 1) // 2
        lx = max(16, min(1008 - text_width(lab, 1), lx))
        draw_text(lx, 89, lab, 1, INK)
    draw_text(1008 - text_width("UTC", 1), 89, "UTC", 1, GREY)


def index_panel(x, y, w, h):
    frame(x, y, w, h, INK)
    draw_text(x + 10, y + 8, "BY REGION: 52 STORIES", 1, RED)
    rows = [("MIDDLE EAST", 5), ("EUROPE", 21), ("ASIA-PACIFIC", 12),
            ("AMERICAS", 5), ("AFRICA", 4), ("MARKETS + TECH", 5)]
    for i, (name, n) in enumerate(rows):
        ty = y + 22 + i * 11
        draw_text(x + 10, ty, name, 1, INK)
        draw_text(x + w - 10 - text_width(str(n), 1), ty, str(n), 1, INK)
    hline(x + 10, y + 92, w - 20, LIGHT)
    draw_text(x + 10, y + 98, "MAP: 1 POLAND 2 GULF OF FINLAND 3 ANTALYA", 1, GREY)
    draw_text(x + 10, y + 108, "4 MEXICO 5 KRYVYI RIH 6 NIGERIA 7 TURIN", 1, GREY)


# 13 anchor cards: (kicker, headline, caption, scene)
ANCHORS = [
    ("POLAND", "RUTTE VOWS: EVERY INCH",
     "NATO: WE WILL DEFEND POLAND", mini_poland),
    ("GULF OF FINLAND", "DRONES HIT SPARTA II",
     "RUSSIAN SHIP ABLAZE, DRIFTS ON", mini_sparta),
    ("CLIMATE", "COP31: DEAL AT LAST?",
     "NEW TEXT, VOTE AT 06:00 GMT", mini_cop31),
    ("MEXICO", "EL CHAPO ISIDRO CAUGHT",
     "11 DEAD IN SINALOA RAID, $5M REWARD", mini_mexico),
    ("USA", "FBI PROBES DATABASE HACK",
     "CRIME DATABASE APPARENTLY BREACHED", mini_fbi),
    ("MARKETS", "NVIDIA SINKS 14 PC",
     "SEC PROBE, 7TH DAY OF LOSSES", mini_nvidia),
    ("UKRAINE", "NO DEAL WITHOUT PAPER",
     "US WANTS DEAL BY JANUARY", mini_kyiv),
    ("UKRAINE", "KRYVYI RIH TOLL RISES",
     "2 DEAD, 58 HURT, CHILD KILLED", mini_kryvyi),
    ("MATHS", "RIEMANN PROOF CLAIMED",
     "ALPOGE SAYS CLAUDE HELPED SOLVE IT", mini_riemann),
    ("NIGERIA", "BOAT CAPSIZES, 24 DEAD",
     "FUNERAL PASSENGERS DROWN", mini_boat),
    ("INDONESIA", "FACTORY FIRE: 39 MISSING",
     "CANDY PLANT BLAZE, 3 DEAD", mini_fire),
    ("CRICKET", "PAKISTAN TAKE SERIES 1-0",
     "8-WICKET WIN OVER SRI LANKA", mini_cricket),
    ("TENNIS", "ZVEREV V ALCARAZ FINAL",
     "SEMIS WON, FINAL TODAY IN TURIN", mini_turin_final),
]

# 39 briefs, column-major (3 columns x 13 rows).
BRIEFS = [
    # column 1: Middle East + Gulf + war
    ("IRAN ROLLS OUT BLACKOUTS", "WAR DAMAGE HITS POWER GRID"),
    ("HORMUZ REOPENING IN 2 DAYS", "IRAN SHORTENS ITS OWN PLAN"),
    ("BAHRAIN: IRAN HIT SETS FIRE", "CIVIL PLANT BLAZES, NO DEAD"),
    ("TRUMP WEIGHS NEW IRAN STRIKES", "PENTAGON WARNS OF MOUNTING COST"),
    ("428 CHILDREN KILLED IN 2 WARS", "IRAN RED CRESCENT SEEKS PROBE"),
    ("US, CHINA AGREE ON AI WEAPONS", "HUMANS TO KEEP MILITARY CALLS"),
    ("ZELENSKY: BRIDGE HIT WAS FAIR", "KYIV AFTER 109 RUSSIAN STRIKES"),
    ("LAVROV: KYIV IS RUSSIAN LAND", "FOREIGN MINISTER IN TV CLAIM"),
    ("15 VILLAGES OFFERED CEASEFIRE", "KYIV PROPOSES LOCAL EVACUATIONS"),
    ("FILIN MISSILE SHOT DOWN", "NEW RUSSIAN CRUISE MISSILE SEEN"),
    ("KERCH BRIDGE REPAIRS MONTHS", "KYIV: DEBRIS BLOCKS SHIPPING"),
    ("DENMARK: PLOT TO KILL RAPPER", "RUSSIA ACCUSED OF ASSASSINATION"),
    ("ESTONIA TO SHUT RUSSIA BORDER", "MOSCOW CRITICISES THE MOVE"),
    # column 2: Europe + tech + markets
    ("NATO COUNCIL MEETS MONDAY", "ALLIES TO DISCUSS POLAND BREACH"),
    ("KH-101 CONFIRMED IN POLAND", "PROSECUTOR: RUSSIAN MISSILE FOUND"),
    ("TRUMP: PUTIN HIT BY MISTAKE", "US PLAYS DOWN POLAND STRIKES"),
    ("UK-EU DEAL STANDS WITHOUT FEES", "MILIBAND ON TUITION ROW"),
    ("ECB HUNT AS LAGARDE RESIGNS", "EU SEEKS NEW CENTRAL BANK CHIEF"),
    ("NORWAY OIL LICENCES VOID", "TOP COURT RULES AGAINST DRILLING"),
    ("CHINA SPIED FOR AI CHIPS", "NYT: YEARS-LONG ESPIONAGE DRIVE"),
    ("BEIJING BUILDS ISLAND RUNWAY", "SOUTH CHINA SEA PUSH GROWS"),
    ("TAIWAN STOCKS PLUNGE", "FUND STEPS IN, SHORT BAN FROM MONDAY"),
    ("S KOREA MINISTER RESIGNS", "AI CHEATING SCANDAL AT EXAMS"),
    ("TIKTOK DEEPFAKE TOOL GOES GLOBAL", "PUBLIC FIGURES GET DETECTION"),
    ("JAPAN, INDIA DEEPEN DEFENCE", "LIVE-FIRE MISSILE TRAINING AGREED"),
    ("GOLD, BITCOIN TAKE A HIT", "GLOBAL STOCKS IN WEEK FROM HELL"),
    # column 3: Americas + Asia + Africa + sport
    ("MODI OPENS NITISH SETU BRIDGE", "PATNA TO VAISHALI LINK OPENS"),
    ("INDIA PASSES 1 CRORE HPV JABS", "VACCINE MILESTONE CROSSED"),
    ("INDIA LEAD NZ BY 118 RUNS", "486 FOR 4 IN WELLINGTON TEST"),
    ("LEEDS STUN CHELSEA 4-1", "SHOCK OF THE PREMIER LEAGUE DAY"),
    ("MAN CITY HELD 1-1 BY FULHAM", "NEWCASTLE 2-2 ARSENAL TOO"),
    ("REAL MADRID BEAT CELTA 2-1", "LA LIGA LEADERS HOLD ON"),
    ("AUS EDGE ENGLAND IN T20 THRILLER", "3-WICKET WIN, 191 FOR 7"),
    ("TRUMP: CAP CARD RATES AT 10 PC", "VOWS TO WORK WITH DEMOCRATS"),
    ("DEMOCRATS RECLAIM CONGRESS", "MIDTERM COMEBACK COMPLETE"),
    ("SOMALIA AMBUSH: HUNDREDS DEAD", "AL-SHABAAB CLAIMS BIG ATTACK"),
    ("KENYA CLEARS LAST EBOLA CASE", "DRC TOLL PASSES 5,300 DEAD"),
    ("GHANA UNVEILS HERITAGE NOTES", "NKRUMAH, ANNAN ON NEW BANKNOTES"),
    ("EL NINO DROUGHT HITS FIJI, TONGA", "CRISIS LEVELS IN THE PACIFIC"),
]


def draw_page():
    rect(0, 0, W, H, PAPER)
    # masthead
    draw_text_centered(W // 2, 12, "THE WORLD", 6, INK)
    draw_text_centered(W // 2, 60, "SUNDAY 22 NOVEMBER 2026", 2, INK)
    draw_numbers_box(16, 2, 320, 80)
    draw_quotes_strip(688, 2, 320, 80)
    rect(16, 84, 992, 3, INK)
    # UTC timeline strip
    draw_timeline()
    # anchor grid: rows 1-4 (h 84), row 5 (h 124)
    cols = (16, 352, 688)
    rows = (118, 207, 296, 385)
    for r in range(4):
        for c in range(3):
            kicker, headline, sub, scene_fn = ANCHORS[r * 3 + c]
            anchor_card(cols[c], rows[r], 320, 84, kicker, headline, sub,
                        scene_fn, 36)
    kicker, headline, sub, scene_fn = ANCHORS[12]
    anchor_card(16, 474, 320, 124, kicker, headline, sub, scene_fn, 56)
    frame(352, 474, 320, 124, INK)
    scene_map_numbered(353, 475, 318, 122)
    index_panel(688, 474, 320, 124)
    # briefs header
    draw_text_centered(W // 2, 606, "THE DAY IN BRIEF - 39 MORE STORIES", 2,
                       INK)
    rect(16, 626, 992, 2, INK)
    # briefs: 3 columns x 13 rows
    for i, (head, cap) in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        bx = 16 + col * 336
        by = 632 + row * 27
        draw_text(bx, by, head, 1, INK)
        draw_text(bx, by + 11, cap, 1, GREY)
        if row < 12:
            hline(bx, by + 24, 320, LIGHT)
    # footer
    rect(16, 988, 992, 2, INK)
    draw_text_centered(W // 2, 996, "52 STORIES, ONE DAY", 2, RED)


def main():
    assert len(ANCHORS) == 13, len(ANCHORS)
    assert len(BRIEFS) == 39, len(BRIEFS)
    assert sum(n for _, n in
               [("MIDDLE EAST", 5), ("EUROPE", 21), ("ASIA-PACIFIC", 12),
                ("AMERICAS", 5), ("AFRICA", 4),
                ("MARKETS + TECH", 5)]) == 52
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/entry.png")
    if out_dir.endswith(".png"):
        path = out_dir
    else:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
