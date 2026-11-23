#!/usr/bin/env python3
"""Draw the 22 November 2026 front-page image (entry.png), stdlib only.

A newspaper front page: masthead with the date, one lead story and five
more panels, each with a drawn illustration, a headline and one short
factual line. Everything is drawn by code: a 5x7 bitmap font, flat vector
shapes, panels. No external assets, no network, no third-party packages.
Deterministic: the same bytes every run.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# Palette
PAPER = (246, 241, 227)
INK = (17, 17, 17)
RED = (176, 32, 32)
BLUE = (31, 78, 121)
TEAL = (14, 110, 110)
GREEN = (34, 110, 54)
ORANGE = (214, 110, 20)
GOLD = (196, 148, 32)
GREY = (120, 120, 116)
LIGHT = (232, 226, 208)
WHITE = (255, 255, 255)
SKY = (196, 222, 235)
SAND = (224, 205, 160)
DARK = (28, 32, 40)
SMOKE = (168, 164, 154)

buf = bytearray(W * H * 3)
for i in range(W * H):
    buf[i * 3:i * 3 + 3] = bytes(PAPER)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        buf[i:i + 3] = bytes(c)


def rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        buf[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)


def hline(x0, x1, y, c):
    for x in range(min(x0, x1), max(x0, x1) + 1):
        px(x, y, c)


def vline(x, y0, y1, c):
    for y in range(min(y0, y1), max(y0, y1) + 1):
        px(x, y, c)


def line(x0, y0, x1, y1, c, thick=1):
    dx, dy = abs(x1 - x0), abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    while True:
        for t in range(thick):
            px(x0 + t, y0, c)
            px(x0, y0 + t, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=True):
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d = (x - cx) ** 2 + (y - cy) ** 2
            if fill:
                if d <= r * r:
                    px(x, y, c)
            else:
                if r * r - 2 * r <= d <= r * r:
                    px(x, y, c)


def ellipse(cx, cy, rx, ry, c):
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1.0:
                px(x, y, c)


def triangle(p1, p2, p3, c):
    xs = [p1[0], p2[0], p3[0]]
    ys = [p1[1], p2[1], p3[1]]
    x0, x1 = min(xs), max(xs)
    y0, y1 = min(ys), max(ys)
    d = (p2[1] - p3[1]) * (p1[0] - p3[0]) + (p3[0] - p2[0]) * (p1[1] - p3[1])
    if d == 0:
        return
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            a = ((p2[1] - p3[1]) * (x - p3[0]) + (p3[0] - p2[0]) * (y - p3[1])) / d
            b = ((p3[1] - p1[1]) * (x - p3[0]) + (p1[0] - p3[0]) * (y - p3[1])) / d
            g = 1 - a - b
            if a >= 0 and b >= 0 and g >= 0:
                px(x, y, c)


def burst(cx, cy, r, c, spikes=8):
    for i in range(spikes):
        a1 = 2 * math.pi * i / spikes
        a2 = 2 * math.pi * (i + 0.5) / spikes
        tip = (cx + int(r * math.cos(a1)), cy + int(r * math.sin(a1)))
        base1 = (cx + int(r * 0.35 * math.cos(a2 - 0.35)),
                 cy + int(r * 0.35 * math.sin(a2 - 0.35)))
        base2 = (cx + int(r * 0.35 * math.cos(a2 + 0.35)),
                 cy + int(r * 0.35 * math.sin(a2 + 0.35)))
        triangle(tip, base1, base2, c)
    circle(cx, cy, int(r * 0.32), c)


# 5x7 bitmap font, written by hand.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
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
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00010", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "00000", "00100"),
    ',': ("00000", "00000", "00000", "00000", "00000", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ':': ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '(': ("00011", "00100", "01000", "01000", "01000", "00100", "00011"),
    ')': ("11000", "00100", "00010", "00010", "00010", "00100", "11000"),
    '/': ("00001", "00001", "00010", "00010", "00100", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
}


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c, align="left"):
    s = s.upper()
    w = text_w(s, scale)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    for ch in s:
        glyph = FONT.get(ch, FONT[' '])
        for row in range(7):
            for col in range(5):
                if glyph[row][col] == '1':
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return w


def wrap_text(s, max_w, scale):
    words = s.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines

# ---------- Illustrations (each drawn inside its panel's art box) ----------

def art_cop31(x, y, w, h):
    # Conference hall: globe above a long table, flags, a torn document.
    rect(x, y, w, h, (30, 52, 84))
    circle(x + w // 2, y + 62, 52, BLUE)
    ellipse(x + w // 2 - 18, y + 44, 16, 10, GREEN)
    ellipse(x + w // 2 + 16, y + 78, 18, 9, GREEN)
    ellipse(x + w // 2 - 26, y + 82, 10, 7, GREEN)
    circle(x + w // 2, y + 62, 52, INK, fill=False)
    # Crack across the globe: no deal
    line(x + w // 2 - 40, y + 30, x + w // 2 - 8, y + 58, RED, 4)
    line(x + w // 2 - 8, y + 58, x + w // 2 + 12, y + 44, RED, 4)
    line(x + w // 2 + 12, y + 44, x + w // 2 + 38, y + 74, RED, 4)
    # Table and flags
    rect(x + 20, y + h - 46, w - 40, 46, (88, 62, 40))
    for i, c in enumerate((BLUE, RED, GREEN, GOLD, TEAL)):
        fx = x + 44 + i * 62
        vline(fx, y + h - 84, y + h - 46, INK)
        triangle((fx, y + h - 84), (fx, y + h - 68), (fx + 26, y + h - 76), c)
    # Torn white document on the table
    rect(x + w - 118, y + h - 40, 92, 30, WHITE)
    triangle((x + w - 118, y + h - 40), (x + w - 96, y + h - 40),
             (x + w - 108, y + h - 22), (30, 52, 84))
    line(x + w - 110, y + h - 30, x + w - 60, y + h - 30, INK, 2)
    line(x + w - 110, y + h - 22, x + w - 70, y + h - 22, INK, 2)


def art_bahrain(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + w - 56, y + 30, 20, GOLD)
    # Base buildings and watchtower
    rect(x + 16, y + h - 52, 150, 52, GREY)
    for bx in (26, 56, 86, 116):
        rect(x + bx, y + h - 42, 16, 16, INK)
    rect(x + 186, y + h - 72, 32, 72, BLUE)
    rect(x + 195, y + h - 64, 14, 12, WHITE)
    vline(x + 202, y + h - 100, y + h - 72, INK)
    triangle((x + 202, y + h - 100), (x + 202, y + h - 86),
             (x + 226, y + h - 93), RED)
    # Missile streaking down
    line(x + w - 140, y + 10, x + w - 58, y + h - 64, INK, 5)
    triangle((x + w - 140, y + 10), (x + w - 128, y + 20),
             (x + w - 152, y + 18), INK)
    # Explosion where it lands
    burst(x + w - 66, y + h - 48, 28, ORANGE)
    burst(x + w - 66, y + h - 48, 15, RED)
    circle(x + w - 104, y + h - 66, 12, SMOKE)
    circle(x + w - 84, y + h - 78, 14, SMOKE)


def art_dymer(x, y, w, h):
    rect(x, y, w, h, (216, 208, 190))
    rect(x, y + h - 24, w, 24, (90, 86, 80))
    for i in range(5):
        rect(x + 18 + i * 58, y + h - 13, 28, 4, (220, 216, 200))
    # Intact block
    rect(x + 24, y + 26, 84, h - 50, BLUE)
    for wy in (38, 60):
        for wx in (34, 60):
            rect(x + wx, y + wy, 14, 12, WHITE)
    # Damaged block, top corner broken off
    rect(x + 128, y + 48, 96, h - 72, (150, 60, 50))
    triangle((x + 128, y + 48), (x + 176, y + 20), (x + 224, y + 48), INK)
    rect(x + 142, y + 62, 14, 12, WHITE)
    rect(x + 172, y + 62, 14, 12, WHITE)
    rect(x + 244, y + 16, 72, h - 40, GREY)
    rect(x + 254, y + 28, 13, 11, WHITE)
    rect(x + 278, y + 28, 13, 11, WHITE)
    # Rubble
    triangle((x + 120, y + h - 24), (x + 152, y + h - 48),
             (x + 186, y + h - 24), (120, 110, 95))
    triangle((x + 178, y + h - 24), (x + 200, y + h - 42),
             (x + 224, y + h - 24), (140, 128, 112))
    # Smoke
    circle(x + 176, y + 30, 13, SMOKE)
    circle(x + 198, y + 18, 15, SMOKE)
    # Warning triangle
    triangle((x + w - 58, y + h - 52), (x + w - 28, y + h - 52),
             (x + w - 43, y + h - 76), RED)
    rect(x + w - 46, y + h - 70, 6, 11, WHITE)
    rect(x + w - 46, y + h - 55, 6, 5, WHITE)


def art_benghazi(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + 44, y + 28, 16, GOLD)
    # Sea
    rect(x, y + h - 30, w, 30, BLUE)
    for i in range(4):
        hline(x + 12 + i * 74, x + 56 + i * 74, y + h - 20, WHITE)
        hline(x + 30 + i * 74, x + 66 + i * 74, y + h - 10, WHITE)
    # Warship (deck, tower, mast all inside the 100px box)
    rect(x + 60, y + h - 56, 190, 28, GREY)
    triangle((x + 60, y + h - 56), (x + 60, y + h - 28), (x + 96, y + h - 28), GREY)
    rect(x + 110, y + h - 74, 60, 20, DARK)
    vline(x + 140, y + h - 84, y + h - 74, INK)
    circle(x + 140, y + h - 88, 4, RED)
    # Drone above, diving in
    circle(x + w - 80, y + 26, 5, INK)
    line(x + w - 96, y + 22, x + w - 64, y + 22, INK, 3)
    line(x + w - 80, y + 10, x + w - 80, y + 42, INK, 3)
    line(x + w - 80, y + 32, x + 210, y + h - 48, INK, 2)
    # Blast on the deck
    burst(x + 210, y + h - 48, 20, ORANGE)
    burst(x + 210, y + h - 48, 10, RED)
    circle(x + 236, y + h - 72, 12, SMOKE)
    circle(x + 256, y + h - 82, 14, SMOKE)


def art_house(x, y, w, h):
    rect(x, y, w, h, (24, 38, 64))
    # Capitol dome (kept inside the 100px art box)
    rect(x + w // 2 - 110, y + h - 40, 220, 40, WHITE)
    for i in range(7):
        rect(x + w // 2 - 96 + i * 28, y + h - 32, 12, 24, DARK)
    ellipse(x + w // 2, y + h - 36, 80, 36, WHITE)
    rect(x + w // 2 - 80, y + h - 40, 160, 8, WHITE)
    rect(x + w // 2 - 3, y + h - 84, 6, 14, WHITE)
    circle(x + w // 2, y + h - 86, 4, GOLD)
    # Ballot box with a big check
    rect(x + w - 150, y + h - 66, 110, 66, RED)
    rect(x + w - 128, y + h - 78, 66, 14, RED)
    line(x + w - 138, y + h - 34, x + w - 112, y + h - 12, WHITE, 6)
    line(x + w - 112, y + h - 12, x + w - 58, y + h - 56, WHITE, 6)
    # Stars
    burst(x + 60, y + 34, 14, GOLD, spikes=5)
    burst(x + w - 60, y + 30, 11, GOLD, spikes=5)


def art_mercury(x, y, w, h):
    rect(x, y, w, h, (12, 12, 24))
    # Stars
    for sx, sy in ((30, 20), (70, 44), (120, 16), (w - 40, 26), (w - 90, 60),
                   (50, 76), (w - 130, 84), (150, 70)):
        circle(x + sx, y + sy, 2, WHITE)
    # Sun glow top right
    circle(x + w - 46, y + 26, 20, GOLD)
    circle(x + w - 46, y + 26, 12, (255, 220, 120))
    # Mercury, cratered (r 40 fits the 100px box)
    circle(x + w // 2 - 40, y + 52, 40, (150, 140, 130))
    circle(x + w // 2 - 58, y + 40, 8, (120, 110, 100))
    circle(x + w // 2 - 26, y + 64, 10, (120, 110, 100))
    circle(x + w // 2 - 52, y + 66, 5, (130, 120, 110))
    circle(x + w // 2 - 18, y + 34, 6, (130, 120, 110))
    # Probe with solar panels, above the planet
    rect(x + w // 2 + 66, y + 22, 26, 16, GOLD)
    rect(x + w // 2 + 34, y + 25, 32, 10, BLUE)
    rect(x + w // 2 + 92, y + 25, 32, 10, BLUE)
    line(x + w // 2 + 79, y + 38, x + w // 2 + 40, y + 24, WHITE, 2)
    # Orbit arc around the planet
    for a in range(0, 180, 4):
        ang = math.radians(a)
        px(int(x + w // 2 - 40 + 58 * math.cos(ang)),
           int(y + 52 + 22 * math.sin(ang)), GREY)


# ---------- Layout ----------

def panel(x, y, w, h, kicker, headline, body, art):
    rect(x, y, w, h, WHITE)
    for i in range(h):
        px(x, y + i, INK)
        px(x + w - 1, y + i, INK)
    for i in range(w):
        px(x + i, y, INK)
        px(x + i, y + h - 1, INK)
    art(x + 8, y + 8, w - 16, 100)
    draw_text(x + 12, y + 116, kicker, 2, RED)
    hl = wrap_text(headline, w - 24, 3)
    yy = y + 136
    for ln in hl[:2]:
        draw_text(x + 12, yy, ln, 3, INK)
        yy += 24
    bl = wrap_text(body, w - 24, 2)
    yy = y + 136 + 24 * len(hl[:2]) + 6
    for ln in bl[:4]:
        draw_text(x + 12, yy, ln, 2, INK)
        yy += 16


def main():
    # Masthead
    draw_text(512, 26, "THE WORLD TODAY", 7, INK, align="center")
    for yy in (84, 88):
        hline(28, 995, yy, RED)
    draw_text(512, 100, "SUNDAY 22 NOVEMBER 2026", 3, RED, align="center")
    draw_text(512, 126, "SIX STORIES FROM AROUND THE WORLD", 2, GREY,
              align="center")

    # Lead story: COP31
    lx, ly, lw, lh = 28, 152, 968, 248
    rect(lx, ly, lw, lh, WHITE)
    for i in range(lh):
        px(lx, ly + i, INK)
        px(lx + lw - 1, ly + i, INK)
    for i in range(lw):
        px(lx + i, ly, INK)
        px(lx + i, ly + lh - 1, INK)
    art_cop31(lx + 10, ly + 10, 380, lh - 20)
    tx = lx + 410
    draw_text(tx, ly + 16, "CLIMATE - ANTALYA, TURKEY", 2, RED)
    draw_text(tx, ly + 44, "COP31 CLIMATE TALKS", 4, INK)
    draw_text(tx, ly + 80, "END WITH NO DEAL", 4, INK)
    lead_body = ("The UN climate summit in Antalya ended on Sunday with no "
                 "agreement, two days into overtime, after the EU and allies "
                 "rejected a final text with no mention of fossil fuels.")
    bl = wrap_text(lead_body, lw - 430, 2)
    yy = ly + 128
    for ln in bl[:5]:
        draw_text(tx, yy, ln, 2, INK)
        yy += 16
    draw_text(tx, ly + lh - 30, "THE SUMMIT COLLAPSED - DAY 17 OF 17", 2, GREY)

    # Row A: three panels
    row_y, row_h = 414, 270
    panel(28, row_y, 313, row_h, "GULF - BAHRAIN",
          "IRAN STRIKE HITS BAHRAIN SITE",
          "Bahrain says an Iranian strike hit a civilian site, wounding two "
          "people, one critically.", art_bahrain)
    panel(355, row_y, 313, row_h, "WAR - UKRAINE",
          "DRONE HITS FLATS NEAR KYIV",
          "A Russian drone hit a five-storey block in Dymer, "
          "near Kyiv. 14 people are missing.", art_dymer)
    panel(682, row_y, 313, row_h, "SEA - LIBYA",
          "WARSHIP HIT AT BENGHAZI",
          "Libya says a Russian corvette at Benghazi was hit by a "
          "suspected Ukrainian sea drone.", art_benghazi)

    # Row B: two wide panels
    row2_y = 698
    panel(28, row2_y, 477, row_h, "POLITICS - USA",
          "DEMOCRATS WIN BIGGEST HOUSE MAJORITY SINCE 1992",
          "Chuck Hubbard beat Virginia Foxx in North Carolina after a "
          "recount, giving Democrats at least 258 House seats.",
          art_house)
    panel(519, row2_y, 477, row_h, "SPACE - MERCURY",
          "BEPICOLOMBO ENTERS ORBIT AROUND MERCURY",
          "The European-Japanese BepiColombo probe entered orbit around "
          "Mercury on Sunday, after a seven-year journey.", art_mercury)

    # Footer
    draw_text(512, 984, "THE WORLD TODAY - SUNDAY 22 NOVEMBER 2026", 2, INK,
              align="center")

    # PNG encode (filter 0, zlib level 9, deterministic)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)
        raw.extend(buf[yy * W * 3:(yy + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "entry.png"), "wb") as f:
        f.write(png)
    print("wrote entry.png", len(png), "bytes")


if __name__ == "__main__":
    main()
