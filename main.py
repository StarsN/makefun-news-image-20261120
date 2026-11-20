#!/usr/bin/env python3
"""news-image-20261120: draw a 1024x1024 newspaper front page for
Friday 20 November 2026, entirely from code.

Standard library only. No network, no clock, no randomness:
running it twice produces byte-identical output.

The picture: masthead, the ICJ genocide verdict on Myanmar as the
top story (with a hand-drawn Peace Palace scene), and eight smaller
news panels covering markets, Ukraine, a cyclone in India, the US
Senate, Hormuz shipping, COP31, Berlin and the Nexperia chip row.
All facts were checked against real reporting on 20 November 2026
(Al Jazeera, Reuters, WSJ, The Hindu, IMD, Xinhua).
"""

import binascii
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
INK = (17, 17, 17)
RED = (176, 32, 32)
BLUE = (31, 78, 121)
SKY = (214, 230, 240)
GOLD = (184, 134, 11)
GREY = (120, 116, 104)
LIGHT = (232, 226, 210)

# ---------------------------------------------------------------- font
# Hand-written 5x7 bitmap font. Each glyph is 7 rows of 5 bits.
# Only uppercase is needed: text is upper-cased before drawing.
FONT = {
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
    "6": ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ">": ("10000", "01000", "00100", "00010", "00100", "01000", "10000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (6 units per char)."""
    return len(text) * 6 * scale


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = r, g, b

    def px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = color

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, color)

    def hline(self, x, y, w, color, t=1):
        self.rect(x, y, w, t, color)

    def vline(self, x, y, h, color, t=1):
        self.rect(x, y, t, h, color)

    def line(self, x0, y0, x1, y1, color, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.rect(x0 - t // 2, y0 - t // 2, t, t, color)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, color, fill=False):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d <= r * r:
                        self.px(xx, yy, color)
                else:
                    if r * r - 2 * r <= d <= r * r:
                        self.px(xx, yy, color)

    def poly(self, pts, color):
        """Filled polygon via scanline fill (convex or concave)."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    if y1 != y0:
                        xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for x in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.px(x, y, color)

    def text(self, x, y, s, scale, color):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + gx * scale, y + gy * scale,
                                  scale, scale, color)
            cx += 6 * scale
        return cx

    def text_center(self, cx, y, s, scale, color):
        self.text(cx - text_width(s, scale) // 2, y, s, scale, color)

    def wrap(self, text, max_width, scale):
        """Greedy word wrap; returns list of lines fitting max_width."""
        max_chars = max(1, max_width // (6 * scale))
        words, lines, cur = text.split(), [], ""
        for wd in words:
            trial = (cur + " " + wd).strip()
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
                while len(cur) > max_chars:  # very long token: hard split
                    lines.append(cur[:max_chars])
                    cur = cur[max_chars:]
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, text, max_width, scale, color, lh=None):
        if lh is None:
            lh = 7 * scale + 3
        yy = y
        for ln in self.wrap(text, max_width, scale):
            self.text(x, yy, ln, scale, color)
            yy += lh
        return yy


# ---------------------------------------------------------------- PNG
def write_png(path, cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)

# ---------------------------------------------------------------- scene
def draw_peace_palace(cv, x, y, w, h):
    """The Peace Palace, The Hague: pediment, columns, steps and the
    scales of justice in front. Pure geometry, no assets."""
    cv.rect(x, y, w, h, SKY)
    # sun
    cv.circle(x + w - 70, y + 42, 26, GOLD, fill=True)
    cv.circle(x + w - 70, y + 42, 20, (232, 196, 90), fill=True)
    # distant clouds
    for cx, cy in ((x + 90, y + 40), (x + 300, y + 26), (x + 620, y + 52)):
        cv.circle(cx, cy, 16, (255, 255, 255), fill=True)
        cv.circle(cx + 18, cy + 4, 12, (255, 255, 255), fill=True)
    ground = y + h - 46
    cv.rect(x, ground, w, h - (ground - y), (196, 186, 158))
    # building body: narrower, so the pediment reads as a roof
    bx, bw = x + 210, w - 420
    by, bh = y + 84, ground - y - 84
    cv.rect(bx, by, bw, bh, (238, 228, 200))
    cv.rect(bx - 6, by - 4, bw + 12, 8, INK)
    # pediment
    cv.poly([(bx - 16, by), (bx + bw // 2, by - 44),
             (bx + bw + 16, by)], (214, 200, 160))
    cv.circle(bx + bw // 2, by - 26, 12, GOLD, fill=True)
    cv.circle(bx + bw // 2, by - 26, 7, (232, 196, 90), fill=True)
    # columns, full height
    for i in range(4):
        cx = bx + 70 + i * (bw - 140) // 3
        cv.rect(cx - 14, by + 14, 28, bh - 14, (250, 244, 224))
        cv.rect(cx - 17, by + 10, 34, 6, INK)
        cv.rect(cx - 17, by + bh - 6, 34, 6, INK)
    # door
    cv.rect(bx + bw // 2 - 26, by + bh - 58, 52, 58, (90, 60, 40))
    cv.vline(bx + bw // 2, by + bh - 58, 58, GOLD, 2)
    # steps
    for i in range(3):
        cv.rect(bx - 30 - i * 14, ground - 8 - i * 8,
                bw + 60 + i * 28, 8, (210, 202, 176))
    # scales of justice, clear of the building, standing on the steps
    sx, sy = x + 108, ground - 8
    cv.rect(sx - 3, sy - 96, 6, 96, GOLD)                 # post
    cv.rect(sx - 16, sy - 6, 32, 6, GOLD)                 # base
    cv.circle(sx, sy - 100, 7, GOLD, fill=True)           # finial
    cv.hline(sx - 50, sy - 92, 100, GOLD, 4)              # beam
    for dx in (-50, 50):
        cv.line(sx + dx, sy - 90, sx + dx - 20, sy - 54, GOLD, 2)
        cv.line(sx + dx, sy - 90, sx + dx + 20, sy - 54, GOLD, 2)
        cv.line(sx + dx - 20, sy - 54, sx + dx + 20, sy - 54, GOLD, 3)
        cv.poly([(sx + dx - 22, sy - 54), (sx + dx + 22, sy - 54),
                 (sx + dx, sy - 36)], GOLD)
    # a small crowd: heads and shoulders along the bottom right
    for i, cx in enumerate(range(x + w - 300, x + w - 40, 34)):
        cv.circle(cx, ground - 26, 9, (60 + i * 8, 60, 60), fill=True)
        cv.poly([(cx - 13, ground - 4), (cx + 13, ground - 4),
                 (cx + 9, ground - 18), (cx - 9, ground - 18)],
                (70 + i * 6, 80, 110))
    # caption bar
    cv.rect(x, y + h - 22, w, 22, INK)
    cv.text(x + 10, y + h - 18, "THE PEACE PALACE, THE HAGUE - "
            "JUDGMENT READ OUT BY PRESIDENT YUJI IWASAWA", 1, PAPER)


# ---------------------------------------------------------------- panels
PANELS = [
    ("MARKETS - NEW YORK", "ANTHROPIC +17% IN RECORD IPO",
     "Claude maker Anthropic closes at $97.17 after pricing at $83, "
     "raising $81.3bn in the biggest IPO ever. The Dow sinks 1,100 "
     "points as the S&P 500 falls 2% for a fifth straight day.",
     "chart"),
    ("UKRAINE - KERCH", "THIRD BRIDGE STRIKE IN 4 DAYS",
     "Kyiv hits the Kerch Bridge again, halting rail traffic to "
     "Crimea. Putin vows a 'far more painful' reply and drops talk "
     "of a sea and energy truce.",
     "bridge"),
    ("WEATHER - INDIA", "CYCLONE AKVAN HITS ODISHA",
     "Landfall near Gopalpur with winds to 90 km/h. Nearly 300,000 "
     "people evacuated to 2,523 relief camps; 47 trains cancelled.",
     "storm"),
    ("WASHINGTON", "SENATE VOTES TO FREE EPSTEIN FILES",
     "Senators unanimously pass the House bill forcing the Justice "
     "Department to release files on financier Jeffrey Epstein.",
     "dome"),
    ("ENERGY - GULF", "HORMUZ TANKER ATTACKS GROW",
     "Iran steps up attacks on shipping in the Strait of Hormuz as "
     "oil prices slide. A Houthi missile hits Riyadh's tallest tower.",
     "flame"),
    ("CLIMATE - COP31", "FOSSIL PLEDGE DROPPED AT COP31",
     "Draft cover text drops references to a fossil-fuel phase-out "
     "and net-zero dates as the climate talks wrap up.",
     "leaf"),
    ("EUROPE - BERLIN", "ALLIES READY FOR TALKS WITH RUSSIA",
     "Ukraine's European allies meet in Berlin, back a united "
     "position for talks with Moscow and a 45bn euro EU loan.",
     "hands"),
    ("TECH - CHIPS", "NEXPERIA CHIP ROW PAUSED",
     "The Netherlands suspends its order over chipmaker Nexperia, "
     "a Wingtech unit. China welcomes the move.",
     "chip"),
]


def draw_icon(cv, x, y, kind):
    s = 30
    if kind == "chart":
        bars = (10, 18, 14, 24)
        for i, bh in enumerate(bars):
            cv.rect(x + 2 + i * 8, y + s - bh, 5, bh, BLUE)
        cv.line(x, y + s - 26, x + s, y + 2, RED, 2)
    elif kind == "bridge":
        cv.rect(x, y + 20, s, 4, INK)
        cv.line(x + 2, y + 22, x + 15, y + 6, INK, 2)
        cv.line(x + 28, y + 22, x + 15, y + 6, INK, 2)
        cv.vline(x + 5, y + 22, 8, INK, 2)
        cv.vline(x + 25, y + 22, 8, INK, 2)
    elif kind == "storm":
        cv.circle(x + 15, y + 15, 13, BLUE)
        cv.circle(x + 15, y + 15, 8, PAPER)
        cv.circle(x + 15, y + 15, 3, BLUE, fill=True)
        cv.line(x + 15, y + 2, x + 24, y + 10, BLUE, 2)
        cv.line(x + 15, y + 28, x + 6, y + 20, BLUE, 2)
    elif kind == "dome":
        cv.poly([(x + 15, y + 2), (x + 26, y + 12), (x + 4, y + 12)], BLUE)
        cv.rect(x + 4, y + 12, 22, 4, BLUE)
        cv.rect(x + 6, y + 16, 18, 12, BLUE)
        cv.rect(x + 2, y + 28, 26, 3, BLUE)
    elif kind == "flame":
        cv.poly([(x + 15, y + 2), (x + 25, y + 16), (x + 20, y + 26),
                 (x + 10, y + 26), (x + 5, y + 16)], RED)
        cv.poly([(x + 15, y + 12), (x + 20, y + 20), (x + 10, y + 20)],
                GOLD)
    elif kind == "leaf":
        cv.poly([(x + 4, y + 26), (x + 26, y + 4), (x + 26, y + 26)], (34, 120, 60))
        cv.line(x + 6, y + 24, x + 24, y + 6, PAPER, 2)
    elif kind == "hands":
        cv.circle(x + 10, y + 15, 8, BLUE)
        cv.circle(x + 20, y + 15, 8, RED)
        cv.rect(x + 8, y + 22, 14, 4, INK)
    elif kind == "chip":
        cv.rect(x + 7, y + 7, 16, 16, INK)
        cv.rect(x + 11, y + 11, 8, 8, PAPER)
        for i in range(3):
            cv.hline(x + 2, y + 10 + i * 5, 5, INK, 2)
            cv.hline(x + 23, y + 10 + i * 5, 5, INK, 2)


def draw_panel(cv, x, y, w, h, kicker, head, body, icon):
    cv.rect(x, y, w, h, (255, 255, 255))
    cv.rect(x, y, w, h, (255, 255, 255))
    cv.rect(x, y, 5, h, RED)
    cv.rect(x, y, w, 1, GREY)
    cv.rect(x, y + h - 1, w, 1, GREY)
    cv.rect(x + w - 1, y, 1, h, GREY)
    draw_icon(cv, x + w - 40, y + 8, icon)
    cv.text(x + 14, y + 8, kicker, 1, RED)
    cv.text(x + 14, y + 22, head, 1, INK)
    cv.hline(x + 14, y + 36, w - 60, LIGHT, 1)
    cv.para(x + 14, y + 42, body, w - 28, 1, (40, 40, 40), lh=10)

# ---------------------------------------------------------------- page
def draw_page(cv):
    M = 24                      # margin
    inner = W - 2 * M
    # frame
    cv.rect(6, 6, W - 12, H - 12, INK)
    cv.rect(10, 10, W - 20, H - 20, PAPER)
    cv.rect(14, 14, W - 28, H - 28, INK)
    cv.rect(16, 16, W - 32, H - 32, PAPER)

    # masthead
    cv.text_center(W // 2, 26, "THE WORLD TODAY", 5, INK)
    cv.hline(M, 74, inner, INK, 3)
    cv.text(M, 84, "VOL. I - NO. 324", 1, INK)
    cv.text_center(W // 2, 84, "FRIDAY 20 NOVEMBER 2026", 2, RED)
    cv.text(W - M - text_width("PRICE: ONE PICTURE", 1), 84,
            "PRICE: ONE PICTURE", 1, INK)
    cv.hline(M, 106, inner, INK, 1)

    # headline
    cv.text_center(W // 2, 118, "WORLD COURT: MYANMAR", 3, INK)
    cv.text_center(W // 2, 145, "COMMITTED GENOCIDE", 3, INK)
    cv.text_center(W // 2, 172, "AGAINST ROHINGYA", 3, INK)
    cv.text_center(W // 2, 206, "FIRST STATE EVER FOUND GUILTY - "
                   "9-6 VOTE - 10,000 KILLED IN 2017 - REPARATIONS ORDERED",
                   1, RED)

    # main picture
    draw_peace_palace(cv, M, 228, inner, 216)

    # main story text
    cv.hline(M, 456, inner, INK, 1)
    cv.para(M, 466,
            "THE HAGUE - The International Court of Justice ruled on "
            "Thursday that Myanmar committed genocide against the "
            "Rohingya in its 2017 crackdown, the first time the World "
            "Court has found a state guilty of the crime. By 9 votes to "
            "6, judges found security forces killed at least 10,000 "
            "people and ordered reparations, including the safe return "
            "of refugees.", inner, 1, INK, lh=11)

    # section label
    cv.hline(M, 528, inner, INK, 2)
    cv.text_center(W // 2, 536, "- ALSO IN THE NEWS -", 1, INK)
    cv.hline(M, 554, inner, INK, 1)

    # eight panels: 2 columns x 4 rows
    pw, ph, gap = (inner - 12) // 2, 90, 10
    for i, (kicker, head, body, icon) in enumerate(PANELS):
        px = M + (i % 2) * (pw + gap)
        py = 560 + (i // 2) * (ph + gap)
        draw_panel(cv, px, py, pw, ph, kicker, head, body, icon)

    # footer
    fy = 560 + 4 * ph + 3 * gap + 8
    cv.hline(M, fy, inner, INK, 2)
    cv.text_center(W // 2, fy + 8,
                   "SOURCES: AL JAZEERA - REUTERS - WSJ - THE HINDU - "
                   "IMD - XINHUA", 1, GREY)
    cv.text_center(W // 2, fy + 22,
                   "DRAWN ENTIRELY BY CODE - NO PHOTOS - NO NETWORK",
                   1, GREY)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        if os.path.isdir("/output"):
            out_dir = "/output"
        else:
            out_dir = "./out"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    cv = Canvas(W, H, PAPER)
    draw_page(cv)
    size = write_png(path, cv)
    print(f"wrote {path} ({cv.w}x{cv.h}, {size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
