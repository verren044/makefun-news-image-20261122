#!/usr/bin/env python3
"""THE WORLD — SUNDAY 22 NOVEMBER 2026.

One 1024x1024 newspaper front page summing up the world's news of
Sunday 22 November 2026: 52 stories in all — 13 anchor stories with
small drawn scenes, a world map with seven numbered story sites, a UTC
timeline, a by-region index, and 39 briefs. Pure Python 3.13 standard
library, deterministic, no network, no randomness, no files read.
Run it and it writes entry.png to MAKEFUN_OUTPUT_DIR.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (178, 34, 34)
GREY = (98, 94, 86)
BLUE = (36, 82, 138)
SEA = (46, 104, 164)
SKY = (170, 200, 226)
NIGHT = (15, 25, 50)
DEEP = (13, 36, 68)
SAND = (216, 188, 140)
LEAF = (76, 122, 68)
GOLD = (234, 186, 50)
FIRE = (228, 108, 30)
WHITE = (255, 255, 255)
MIST = (228, 224, 212)
SLATE = (92, 98, 112)


class Sheet:
    """A plain RGB pixel sheet with small drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill(0, 0, w, h, bg)

    def dot(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        r, g, b = c
        for yy in range(y0, y1):
            base = yy * self.w * 3
            for xx in range(x0, x1):
                i = base + xx * 3
                self.buf[i] = r
                self.buf[i + 1] = g
                self.buf[i + 2] = b

    def hline(self, x, y, w, c):
        self.fill(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill(x, y, 1, h, c)

    def frame(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def disc(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            span = int(math.sqrt(r * r - dy * dy))
            self.fill(cx - span, cy + dy, span * 2 + 1, 1, c)

    def trace(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        half = t // 2
        while True:
            self.fill(x - half, y - half, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def poly(self, pts, c):
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % len(pts)]
                if ay == by:
                    continue
                if (ay <= y < by) or (by <= y < ay):
                    xs.append(ax + (y - ay) * (bx - ax) / (by - ay))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                xa = int(math.ceil(xs[i]))
                xb = int(math.floor(xs[i + 1]))
                if xb >= xa:
                    self.fill(xa, y, xb - xa + 1, 1, c)

    def burst(self, cx, cy, ro, ri, c):
        pts = []
        for i in range(10):
            r = ro if i % 2 == 0 else ri
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((int(cx + r * math.cos(a)),
                        int(cy + r * math.sin(a))))
        self.poly(pts, c)

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            g = GLYPHS.get(ch)
            if g is None:
                raise ValueError("no glyph for %r" % ch)
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.fill(cx + col * scale, y + row * scale,
                                  scale, scale, c)
            cx += 6 * scale
        return cx

    def text_mid(self, cx, y, s, scale, c):
        x = cx - self.text_w(s, scale) // 2
        return self.text(x, y, s, scale, c)

    def png(self):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * self.w * 3:(y + 1) * self.w * 3]

        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data +
                    struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
                chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
                chunk(b"IEND", b""))


# A 5x7 bitmap alphabet, uppercase only. Each glyph is 7 rows of 5 bits.
GLYPHS = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
}


# ------------------------------------------------------------------ scenes
# Every scene draws inside (x, y, w, h); the anchor cards call them with
# h = 28, so each one is a small, bold picture strip.


def scene_poland(s, x, y, w, h):
    s.fill(x, y, w, h, NIGHT)
    for sx, sy in ((14, 5), (52, 10), (96, 4), (150, 8), (210, 5),
                   (260, 9), (300, 6)):
        s.dot(x + sx, y + sy, WHITE)
    # Polish flag on its pole, left
    s.vline(x + 18, y + 3, 22, WHITE)
    s.fill(x + 19, y + 3, 30, 6, WHITE)
    s.fill(x + 19, y + 9, 30, 6, RED)
    # two missile streaks falling in from the right
    s.trace(x + 110, y + 2, x + 200, y + 18, FIRE, 2)
    s.trace(x + 170, y + 2, x + 250, y + 15, FIRE, 2)
    # impact burst on the ground line
    s.burst(x + w - 46, y + h - 9, 9, 3, FIRE)
    s.burst(x + w - 46, y + h - 9, 5, 2, GOLD)
    s.fill(x, y + h - 2, w, 2, (52, 52, 60))


def scene_sparta(s, x, y, w, h):
    s.fill(x, y, w, h, NIGHT)
    for sx, sy in ((14, 5), (52, 10), (96, 4), (150, 8), (210, 5), (260, 9)):
        s.dot(x + sx, y + sy, WHITE)
    # dark sea, cargo ship listing and on fire
    s.fill(x, y + h - 10, w, 10, DEEP)
    s.fill(x + 80, y + h - 16, 120, 8, (30, 30, 36))
    s.fill(x + 92, y + h - 21, 80, 5, (72, 72, 80))
    s.fill(x + 160, y + h - 28, 20, 8, WHITE)
    s.burst(x + 120, y + h - 18, 8, 3, FIRE)
    s.burst(x + 120, y + h - 18, 4, 2, GOLD)
    s.burst(x + 190, y + h - 17, 6, 2, FIRE)
    # two drones overhead, streaks diving toward the ship
    for dx, dy in ((56, 5), (240, 6)):
        s.hline(x + dx - 5, y + dy, 11, WHITE)
        s.vline(x + dx, y + dy - 5, 11, WHITE)
        s.trace(x + dx, y + dy + 5, x + dx + 22, y + dy + 13, GOLD, 1)
    # Finnish coast, right
    s.poly([(x + w - 56, y + h), (x + w - 18, y + 6), (x + w, y + 10),
            (x + w, y + h)], (54, 74, 54))
    s.text(x + 6, y + 3, "GULF OF FINLAND", 1, WHITE)


def scene_cop31(s, x, y, w, h):
    s.fill(x, y, w, h, (212, 228, 212))
    # small globe, left
    s.disc(x + 46, y + h // 2, 11, BLUE)
    s.disc(x + 42, y + h // 2 - 3, 4, LEAF)
    s.disc(x + 51, y + h // 2 + 4, 3, LEAF)
    s.hline(x + 35, y + h // 2, 23, WHITE)
    # clock: the talks have run into overtime
    s.disc(x + 120, y + h // 2, 10, WHITE)
    s.frame(x + 110, y + h // 2 - 10, 21, 21, INK)
    s.trace(x + 120, y + h // 2, x + 120, y + h // 2 - 7, INK, 2)
    s.trace(x + 120, y + h // 2, x + 126, y + h // 2 + 3, INK, 2)
    s.text(x + 150, y + 10, "OVERTIME", 1, RED)
    # a row of small flags
    for i in range(4):
        fx = x + 158 + i * 32
        s.vline(fx, y + 20, 7, INK)
        cols = ((0, 60, 160), (255, 255, 255), (220, 0, 0))
        s.fill(fx + 1, y + 20, 18, 2, cols[i % 3])
        s.fill(fx + 1, y + 22, 18, 2, cols[(i + 1) % 3])
        s.fill(fx + 1, y + 24, 18, 2, cols[(i + 2) % 3])


def scene_mexico(s, x, y, w, h):
    s.fill(x, y, w, h, (34, 24, 18))
    for sx, sy in ((14, 5), (52, 10), (96, 4), (150, 8), (210, 5),
                   (260, 9), (300, 6)):
        s.dot(x + sx, y + sy, WHITE)
    # desert ground
    s.fill(x, y + h - 8, w, 8, (98, 76, 46))
    # helicopter with its searchlight beam on the ground
    s.fill(x + 66, y + 5, 30, 8, (72, 80, 98))
    s.fill(x + 96, y + 8, 32, 3, (72, 80, 98))
    s.fill(x + 76, y + 2, 10, 3, (72, 80, 98))
    s.poly([(x + 72, y + 13), (x + 84, y + 13), (x + 116, y + h - 8),
            (x + 84, y + h - 8)], (242, 222, 142))
    # burning roadblock truck
    s.fill(x + 210, y + h - 16, 56, 9, (122, 42, 32))
    s.fill(x + 222, y + h - 23, 20, 7, (92, 32, 24))
    s.burst(x + 238, y + h - 20, 8, 3, FIRE)
    s.burst(x + 238, y + h - 20, 4, 2, GOLD)
    # the raided house, centre
    s.fill(x + 140, y + h - 20, 40, 13, (152, 122, 86))
    s.poly([(x + 138, y + h - 20), (x + 160, y + h - 27),
            (x + 182, y + h - 20)], (112, 42, 32))
    s.text(x + 200, y + 3, "GUASAVE, SINALOA", 1, WHITE)


def scene_fbi(s, x, y, w, h):
    s.fill(x, y, w, h, NIGHT)
    # three server racks with blinking lights
    for i in range(3):
        rx = x + 14 + i * 66
        s.fill(rx, y + 4, 56, h - 8, (28, 44, 78))
        s.frame(rx, y + 4, 56, h - 8, (90, 110, 150))
        for j in range(3):
            ry = y + 9 + j * 7
            s.fill(rx + 5, ry, 26, 3, (40, 90, 60))
            s.dot(rx + 38, ry + 1, (80, 220, 120))
            s.dot(rx + 44, ry + 1, (220, 80, 80))
    # red warning banner
    s.fill(x + 226, y + 4, w - 234, 20, RED)
    s.text(x + 234, y + 9, "BREACH?", 1, WHITE)


def scene_nvidia(s, x, y, w, h):
    s.fill(x, y, w, h, WHITE)
    # five falling bars, steep drop left to right
    bars = [22, 18, 13, 9, 4]
    base = y + h - 3
    for i, bh in enumerate(bars):
        s.fill(x + 12 + i * 30, base - bh, 26, bh, RED)
    s.trace(x + 14, base - 22, x + 168, base - 4, INK, 2)
    s.text(x + w - 78, y + 4, "-14 PC", 2, RED)
    s.text(x + w - 78, y + 20, "7 DAYS DOWN", 1, GREY)


def scene_kyiv(s, x, y, w, h):
    # Ukrainian flag bands
    s.fill(x, y, w, h // 2, (0, 90, 180))
    s.fill(x, y + h // 2, w, h - h // 2, (255, 215, 0))
    # a white document with a red seal, centre
    s.fill(x + 118, y + 3, 92, h - 6, WHITE)
    s.frame(x + 118, y + 3, 92, h - 6, INK)
    for i in range(3):
        s.hline(x + 126, y + 8 + i * 6, 52, GREY)
    s.disc(x + 198, y + h - 9, 4, RED)
    # a pen lying across the paper
    s.trace(x + 124, y + h - 5, x + 204, y + 7, INK, 2)
    s.text(x + 8, y + 4, "NO PAPER YET", 1, WHITE)
    s.text(x + 8, y + h - 11, "KYIV WAITS", 1, INK)


def scene_kryvyi(s, x, y, w, h):
    s.fill(x, y, w, h, NIGHT)
    for sx, sy in ((14, 5), (52, 10), (96, 4), (150, 8), (210, 5),
                   (260, 9), (300, 6)):
        s.dot(x + sx, y + sy, WHITE)
    # city skyline with lit windows
    base = y + h - 2
    heights = [12, 20, 10, 16, 22]
    bw = w // 5
    for i, bh in enumerate(heights):
        bx = x + i * bw
        s.fill(bx + 2, base - bh, bw - 4, bh, (52, 52, 60))
        for wy in range(base - bh + 4, base - 2, 7):
            s.dot(bx + 8, wy, GOLD)
    # double-tap: two blasts arriving one after the other
    s.burst(x + 104, y + 10, 9, 3, FIRE)
    s.burst(x + 104, y + 10, 5, 2, GOLD)
    s.burst(x + 208, y + 15, 7, 3, FIRE)
    s.burst(x + 208, y + 15, 4, 2, GOLD)
    s.trace(x + 56, y + 2, x + 104, y + 8, FIRE, 2)
    s.trace(x + 256, y + 2, x + 208, y + 13, FIRE, 2)


def scene_riemann(s, x, y, w, h):
    # a chalkboard with a zeta curve on it
    s.fill(x, y, w, h, (24, 52, 36))
    s.text(x + 8, y + 4, "ZETA(S)", 1, WHITE)
    s.text(x + 8, y + h - 14, "PROOF?", 2, GOLD)
    prev = None
    for px in range(90, w - 96, 4):
        py = y + h // 2 - int(7 * math.sin(px / 16.0)) - px // 48
        if prev is not None:
            s.trace(prev[0], prev[1], x + px, py, WHITE, 1)
        prev = (x + px, py)
    # the critical line
    s.vline(x + w - 104, y + 3, h - 6, GOLD)
    s.text(x + w - 94, y + 5, "1/2", 1, GOLD)


def scene_boat(s, x, y, w, h):
    s.fill(x, y, w, h, SKY)
    s.disc(x + 298, y + 7, 5, (240, 214, 120))
    # the river
    s.fill(x, y + h - 14, w, 14, (24, 68, 118))
    for dx in range(0, w, 24):
        s.hline(x + dx, y + h - 9, 12, (120, 170, 220))
    # capsized hull, upside down in the water
    s.poly([(x + 108, y + h - 14), (x + 208, y + h - 14),
            (x + 193, y + h - 25), (x + 123, y + h - 25)], (120, 70, 40))
    # a life ring floating beside it
    s.disc(x + 248, y + h - 8, 6, FIRE)
    s.disc(x + 248, y + h - 8, 3, (24, 68, 118))
    # mourners' umbrellas on the bank
    for ux in (28, 56, 282):
        s.vline(x + ux, y + h - 22, 8, INK)
        s.poly([(x + ux - 9, y + h - 14), (x + ux + 9, y + h - 14),
                (x + ux, y + h - 20)], INK)
    s.text(x + 6, y + 3, "NIGERIA", 1, INK)


def scene_fire(s, x, y, w, h):
    s.fill(x, y, w, h, (40, 40, 48))
    # factory silhouette with two chimneys
    s.fill(x + 28, y + h - 18, 116, 14, (20, 20, 26))
    s.fill(x + 156, y + h - 24, 12, 20, (20, 20, 26))
    s.fill(x + 174, y + h - 24, 12, 20, (20, 20, 26))
    s.fill(x + 192, y + h - 12, 56, 8, (20, 20, 26))
    # flames on the roof
    s.burst(x + 66, y + h - 19, 9, 3, FIRE)
    s.burst(x + 66, y + h - 19, 5, 2, GOLD)
    s.burst(x + 112, y + h - 17, 7, 3, FIRE)
    s.burst(x + 214, y + h - 16, 6, 3, FIRE)
    # smoke drifting up
    for sx, sy, r in ((76, 7, 5), (96, 4, 4), (114, 8, 5),
                      (224, 5, 4), (244, 9, 5)):
        s.disc(x + sx, y + sy, r, (120, 120, 128))
    s.text(x + w - 92, y + 3, "39 MISSING", 1, WHITE)


def scene_cricket(s, x, y, w, h):
    s.fill(x, y, w, h, LEAF)
    # the pitch, a pale triangle
    s.poly([(x, y + h), (x + w // 2, y + 3), (x + w, y + h)],
           (196, 164, 112))
    s.trace(x + w // 2, y + 3, x + w // 2, y + h - 2, WHITE, 1)
    s.trace(x + w // 2, y + 3, x + 6, y + h - 2, WHITE, 1)
    s.trace(x + w // 2, y + 3, x + w - 6, y + h - 2, WHITE, 1)
    # the stumps, right
    for sx in (w - 58, w - 52, w - 46):
        s.vline(x + sx, y + h - 13, 10, GOLD)
    s.hline(x + w - 58, y + h - 14, 12, GOLD)
    # the ball, mid-air
    s.disc(x + 56, y + 11, 4, RED)
    s.disc(x + 56, y + 11, 1, WHITE)
    s.text(x + w // 2 - 16, y + 11, "1-0", 2, INK)


def scene_turin(s, x, y, w, h):
    # a tennis court seen from above, stretched to the strip's width
    s.fill(x, y, w, h, (46, 110, 66))
    s.fill(x + 8, y + 4, w - 16, h - 8, (66, 140, 86))
    s.frame(x + 8, y + 4, w - 16, h - 8, WHITE)
    s.vline(x + w // 2, y + 6, h - 12, WHITE)
    s.hline(x + 8, y + h // 2 - 1, w - 16, WHITE)
    s.trace(x + 8, y + 4, x + w - 8, y + h - 4, WHITE, 1)
    s.disc(x + w - 52, y + 11, 5, GOLD)
    s.disc(x + w - 54, y + 9, 2, WHITE)
    s.text(x + 16, y + h - 20, "7-6 6-4", 1, WHITE)


# --------------------------------------------------------------------- map
# Rough continent outlines as (lon, lat) points, drawn by me.
CONTINENTS = {
    "NA": [(-168, 66), (-140, 70), (-120, 72), (-95, 72), (-80, 70),
           (-70, 62), (-55, 47), (-65, 44), (-75, 35), (-80, 25),
           (-90, 21), (-97, 16), (-105, 20), (-115, 28), (-125, 40),
           (-140, 60), (-160, 58)],
    "SA": [(-78, 8), (-60, 8), (-50, 0), (-38, -5), (-35, -10),
           (-40, -22), (-48, -28), (-58, -34), (-68, -40), (-70, -52),
           (-68, -40), (-72, -20), (-80, -5)],
    "AF": [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (32, 31),
           (36, 28), (40, 15), (44, 11), (48, 10), (40, 0), (35, -10),
           (30, -20), (25, -32), (20, -35), (15, -28), (12, -18),
           (9, -5), (9, 4), (-8, 4), (-13, 8)],
    "EU": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 68),
           (24, 71), (18, 70), (12, 65), (5, 60), (0, 55), (-5, 50),
           (-10, 45)],
    "AS": [(30, 68), (40, 72), (60, 73), (90, 75), (120, 73), (150, 70),
           (170, 66), (178, 65), (170, 60), (160, 55), (140, 40),
           (130, 35), (127, 40), (120, 35), (110, 20), (105, 10),
           (100, 8), (95, 15), (90, 22), (85, 20), (80, 8), (75, 8),
           (70, 20), (60, 25), (55, 26), (50, 29), (45, 30), (40, 36),
           (35, 36), (30, 40)],
    "OC": [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38),
           (150, -37), (153, -27), (146, -19), (142, -11), (136, -12),
           (132, -11), (126, -14), (122, -17)],
}

# Numbered story sites on the map; the key sits in the index panel.
SITES = [
    ("1", 22.0, 50.0),    # Rzeszow, Poland
    ("2", 27.5, 59.8),    # Gulf of Finland
    ("3", 30.7, 36.9),    # Antalya, COP31
    ("4", -108.5, 25.6),  # Guasave, Sinaloa, Mexico
    ("5", 33.4, 47.9),    # Kryvyi Rih
    ("6", 7.5, 9.0),      # Nigeria
    ("7", 7.7, 45.1),     # Turin
]


def draw_map(s, x, y, w, h):
    s.fill(x, y, w, h, SEA)
    for pts in CONTINENTS.values():
        conv = []
        for lon, lat in pts:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((78 - lat) / 136.0 * h)
            conv.append((px, py))
        s.poly(conv, LEAF)
    for num, lon, lat in SITES:
        mx = x + int((lon + 180) / 360.0 * w)
        my = y + int((78 - lat) / 136.0 * h)
        s.disc(mx, my, 4, RED)
        s.disc(mx, my, 2, WHITE)
        s.text(mx + 6, my - 3, num, 1, WHITE)
    s.text(x + 10, y + h - 13, "THE WORLD, 22 NOVEMBER 2026", 1, WHITE)


# ------------------------------------------------------- masthead side boxes
FIGURES = [
    ("NVIDIA", "-14 PC", "DOWN"),
    ("S+P 500", "-3.7 PC", "DOWN"),
    ("BITCOIN", "UNDER $60K", "DOWN"),
    ("COP31 POWER", "35 PC 2035", None),
    ("ATP FINAL", "ZVEREV-ALCARAZ", None),
]


def draw_numbers(s, x, y, w, h):
    s.frame(x, y, w, h, INK)
    s.text(x + 8, y + 6, "BY THE NUMBERS", 1, RED)
    s.hline(x + 8, y + 15, w - 16, MIST)
    for i, (label, value, trend) in enumerate(FIGURES):
        ty = y + 20 + i * 11
        s.text(x + 8, ty, label, 1, INK)
        vx = x + w - 8 - s.text_w(value, 1)
        s.text(vx, ty, value, 1, RED)
        if trend == "DOWN":
            s.poly([(vx - 11, ty), (vx - 5, ty), (vx - 8, ty + 6)], RED)


QUOTES = [
    ("RUTTE, ON POLAND", "DEFEND EVERY INCH OF POLISH TERRITORY"),
    ("STREETING, ON THE STRIKES", "OUTRAGEOUS PROVOCATION"),
    ("KURUM, ON THE COP31 DEAL", "A TEXT ALL PARTIES CAN AGREE ON"),
]


def wrap_line(s, limit):
    words = s.split(" ")
    lines = []
    cur = ""
    for wd in words:
        if cur and len(cur) + 1 + len(wd) > limit:
            lines.append(cur)
            cur = wd
        else:
            cur = wd if not cur else cur + " " + wd
    if cur:
        lines.append(cur)
    return lines


def draw_quotes(s, x, y, w, h):
    s.frame(x, y, w, h, INK)
    s.text(x + 8, y + 5, "IN THEIR WORDS", 1, RED)
    s.hline(x + 8, y + 14, w - 16, MIST)
    ty = y + 18
    for who, quote in QUOTES:
        top = ty
        s.text(x + 8, ty, who, 1, RED)
        ty += 9
        for ln in wrap_line(quote, 42):
            s.text(x + 8, ty, ln, 1, INK)
            ty += 9
        s.fill(x + 3, top, 2, ty - top - 2, RED)
        ty += 2


# ------------------------------------------------------------------ timeline
EVENTS = [(0, "FBI HACK"), (3, "COP31 DEAL"), (6, "RUTTE WARSAW"),
          (9, "MEXICO RAID"), (12, "HORMUZ")]


def draw_timeline(s):
    line_y = 114
    s.hline(14, line_y, 996, INK)
    for hh, lab in ((0, "00"), (6, "06"), (12, "12"), (18, "18"), (24, "24")):
        tx = 14 + int(hh / 24 * 996)
        s.vline(tx, line_y - 4, 9, INK)
        lx = tx - s.text_w(lab, 1) // 2
        lx = max(14, min(lx, 1010 - s.text_w(lab, 1)))
        s.text(lx, line_y + 6, lab, 1, GREY)
    for hh, lab in EVENTS:
        ex = 14 + int(hh / 24 * 996)
        s.disc(ex, line_y, 4, RED)
        s.disc(ex, line_y, 2, WHITE)
        lx = ex - s.text_w(lab, 1) // 2
        lx = max(14, min(1010 - s.text_w(lab, 1), lx))
        s.text(lx, 98, lab, 1, INK)
    s.text(1010 - s.text_w("UTC", 1), 98, "UTC", 1, GREY)


# -------------------------------------------------------------- index panel
REGIONS = [("MIDDLE EAST", 5), ("EUROPE", 21), ("ASIA-PACIFIC", 12),
           ("AMERICAS", 5), ("AFRICA", 4), ("MARKETS + TECH", 5)]


def draw_index(s, x, y, w, h):
    s.frame(x, y, w, h, INK)
    s.text(x + 8, y + 7, "BY REGION: 52 STORIES", 1, RED)
    for i, (name, n) in enumerate(REGIONS):
        ty = y + 21 + i * 12
        s.text(x + 8, ty, name, 1, INK)
        s.text(x + w - 8 - s.text_w(str(n), 1), ty, str(n), 1, INK)
    s.hline(x + 8, y + 96, w - 16, MIST)
    s.text(x + 8, y + 102, "MAP: 1 POLAND 2 GULF OF FINLAND 3 ANTALYA",
           1, GREY)
    s.text(x + 8, y + 114, "4 MEXICO 5 KRYVYI RIH 6 NIGERIA 7 TURIN",
           1, GREY)


def draw_card(s, x, y, w, h, kicker, headline, sub, scene):
    s.frame(x, y, w, h, INK)
    scene(s, x + 1, y + 1, w - 2, 28)
    s.hline(x + 1, y + 29, w - 2, INK)
    s.text(x + 8, y + 33, kicker, 1, RED)
    s.text(x + 8, y + 43, headline, 2, INK)
    s.text(x + 8, y + 61, sub, 1, GREY)


# 13 anchor stories: (kicker, headline, supporting line, scene)
ANCHORS = [
    ("POLAND", "RUTTE VOWS: EVERY INCH",
     "NATO: WE WILL DEFEND POLAND", scene_poland),
    ("GULF OF FINLAND", "DRONES HIT SPARTA II",
     "RUSSIAN SHIP ABLAZE, DRIFTS ON", scene_sparta),
    ("CLIMATE", "COP31: DEAL AT LAST?",
     "NEW TEXT, VOTE AT 06:00 GMT", scene_cop31),
    ("MEXICO", "EL CHAPO ISIDRO CAUGHT",
     "11 DEAD IN SINALOA RAID, $5M REWARD", scene_mexico),
    ("USA", "FBI PROBES DATABASE HACK",
     "CRIME DATABASE APPARENTLY BREACHED", scene_fbi),
    ("MARKETS", "NVIDIA SINKS 14 PC",
     "SEC PROBE, 7TH DAY OF LOSSES", scene_nvidia),
    ("UKRAINE", "NO DEAL WITHOUT PAPER",
     "US WANTS DEAL BY JANUARY", scene_kyiv),
    ("UKRAINE", "KRYVYI RIH TOLL RISES",
     "2 DEAD, 58 HURT, CHILD KILLED", scene_kryvyi),
    ("MATHS", "RIEMANN PROOF CLAIMED",
     "ALPOGE SAYS CLAUDE HELPED SOLVE IT", scene_riemann),
    ("NIGERIA", "BOAT CAPSIZES, 24 DEAD",
     "FUNERAL PASSENGERS DROWN", scene_boat),
    ("INDONESIA", "FACTORY FIRE: 39 MISSING",
     "CANDY PLANT BLAZE, 3 DEAD", scene_fire),
    ("CRICKET", "PAKISTAN TAKE SERIES 1-0",
     "8-WICKET WIN OVER SRI LANKA", scene_cricket),
    ("TENNIS", "ZVEREV V ALCARAZ FINAL",
     "SEMIS WON, FINAL TODAY IN TURIN", scene_turin),
]

# 39 briefs, column-major (3 columns x 13 rows): (headline, caption)
BRIEFS = [
    # column 1: Middle East, Gulf and the war
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
    # column 2: Europe, tech and markets
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
    # column 3: Asia, the Americas, Africa and sport
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


def compose(s):
    s.fill(0, 0, W, H, PAPER)
    # masthead with its two side boxes
    draw_numbers(s, 14, 10, 290, 76)
    draw_quotes(s, 720, 10, 290, 76)
    s.text_mid(512, 12, "THE WORLD", 6, INK)
    s.text_mid(512, 60, "SUNDAY 22 NOVEMBER 2026", 2, INK)
    s.fill(14, 92, 996, 2, INK)
    # UTC timeline strip
    draw_timeline(s)
    # map row: the world map and the region index beside it
    draw_map(s, 14, 138, 640, 134)
    s.frame(14, 138, 640, 134, INK)
    draw_index(s, 666, 138, 344, 134)
    # anchor grid: 3 columns x 4 rows, then one wide card
    cols = (14, 344, 674)
    rows = (280, 362, 444, 526)
    for r in range(4):
        for c in range(3):
            kicker, headline, sub, scene = ANCHORS[r * 3 + c]
            draw_card(s, cols[c], rows[r], 322, 76, kicker, headline, sub,
                      scene)
    kicker, headline, sub, scene = ANCHORS[12]
    draw_card(s, 14, 608, 996, 76, kicker, headline, sub, scene)
    # briefs: 3 columns x 13 rows
    s.text(14, 694, "THE DAY IN BRIEF", 2, RED)
    s.text(1010 - s.text_w("39 MORE STORIES", 1), 700, "39 MORE STORIES",
           1, GREY)
    s.fill(14, 714, 996, 2, INK)
    for i, (headline, cap) in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        bx = 14 + col * 332
        by = 722 + row * 20
        s.text(bx, by, headline, 1, INK)
        s.text(bx, by + 9, cap, 1, GREY)
        if row < 12:
            s.hline(bx, by + 17, 322, MIST)
    # footer
    s.fill(14, 986, 996, 2, INK)
    s.text(14, 993, "THE WORLD, SUNDAY 22 NOVEMBER 2026", 1, GREY)
    s.text(1010 - s.text_w("52 STORIES FROM ONE DAY", 1), 993,
           "52 STORIES FROM ONE DAY", 1, GREY)


def main():
    assert len(ANCHORS) == 13, len(ANCHORS)
    assert len(BRIEFS) == 39, len(BRIEFS)
    assert sum(n for _, n in REGIONS) == 52
    s = Sheet(W, H, PAPER)
    compose(s)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/entry.png")
    if out.endswith(".png"):
        path = out
    else:
        os.makedirs(out, exist_ok=True)
        path = os.path.join(out, "entry.png")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(s.png())
    print("wrote", path)


if __name__ == "__main__":
    main()
