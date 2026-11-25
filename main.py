#!/usr/bin/env python3
"""Draw the make.fun entry image for 24 November 2026.

Pure standard library. Deterministic: no timestamps, no randomness,
no network. Writes a 1024x1024 PNG to /output/entry.png by default
(or to the path given as argv[1]).

Design: dense one-page newspaper ("front page"), following the pattern
of the top entries of the 22 November bounty (all 12-0-0, ~99% win
rate): masthead + big date, a numbers strip, 3 lead stories, a
schematic "where it happened" map, a grid of brief stories across
7 regions, an "ALSO ON MONDAY" list, and a DATE CHECK footer.
32 stories in total, all from reports dated Tuesday 24 November 2026
(some events took place on Sunday 22 - Monday 23 November and were reported
on Tuesday); nothing is copied from the 23 November entries.
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# --- colours (r, g, b) -------------------------------------------------
NAVY = (11, 42, 74)          # dark navy header #0B2A4A
NAVY2 = (24, 78, 122)
WHITE = (255, 255, 255)
INK = (10, 18, 32)            # near-black headlines
DARK = (35, 40, 52)           # near-black captions, never pale grey
GREY = (52, 58, 68)           # darkest grey used anywhere (footer only)
LIGHT = (234, 242, 248)
LIGHT2 = (247, 249, 251)
MAPBG = (224, 242, 236)       # pale mint map background
MAPLAND = (46, 130, 122)      # mid blue-green continents
MAPLAND2 = (38, 110, 170)     # mid blue for Asia blob contrast
GOLD = (255, 196, 0)          # bright yellow masthead
GOLD2 = (255, 220, 80)
GREEN = (0, 110, 55)          # deep green
GREEN_TINT = (208, 242, 220)  # light green tint
RED = (200, 0, 24)            # deep red
RED_TINT = (255, 220, 220)    # light red tint
ORANGE = (210, 95, 0)         # deep orange
ORANGE_TINT = (255, 232, 196) # light orange tint
BRIGHTRED = (210, 0, 20)      # numbers strip
TEAL = (0, 120, 120)
PURPLE = (100, 40, 170)
BLUE = (0, 85, 180)
YELLOW_ROW = (255, 243, 205)  # very light yellow brief rows
PALE = (238, 244, 250)

# --- 5x7 bitmap font, uppercase only ----------------------------------
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
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
}


def text_width(text, scale):
    return len(text) * (5 * scale + scale) - scale


def wrap_text(text, scale, max_width):
    """Greedy word wrap; returns list of lines, all uppercase."""
    words = text.upper().split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(trial, scale) <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.pix = bytearray(bg * w * h)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.pix[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            for a in range(-thick // 2, thick // 2 + 1):
                for b in range(-thick // 2, thick // 2 + 1):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if fill:
                    if d2 <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d2 - r * r) <= r * 2:
                        self.set(xx, yy, c)

    def ellipse(self, cx, cy, rx, ry, c):
        for yy in range(cy - ry, cy + ry + 1):
            t = 1.0 - ((yy - cy) / ry) ** 2
            if t < 0:
                continue
            dx = int(rx * (t ** 0.5))
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, c)

    def triangle(self, p1, p2, p3, c):
        xs = [p1[0], p2[0], p3[0]]
        ys = [p1[1], p2[1], p3[1]]
        for yy in range(min(ys), max(ys) + 1):
            for xx in range(min(xs), max(xs) + 1):
                d1 = (xx - p2[0]) * (p1[1] - p2[1]) - (p1[0] - p2[0]) * (yy - p2[1])
                d2 = (xx - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (yy - p3[1])
                d3 = (xx - p1[0]) * (p3[1] - p1[1]) - (p3[0] - p1[0]) * (yy - p1[1])
                if (d1 >= 0 and d2 >= 0 and d3 >= 0) or (d1 <= 0 and d2 <= 0 and d3 <= 0):
                    self.set(xx, yy, c)

    def text(self, x, y, s, scale, c, bold=False):
        s = s.upper()
        offsets = [(0, 0), (1, 0), (0, 1)] if bold else [(0, 0)]
        for ox, oy in offsets:
            cx = x + ox
            for ch in s:
                glyph = FONT.get(ch, FONT[" "])
                for row in range(7):
                    for col in range(5):
                        if glyph[row][col] == "1":
                            self.rect(cx + col * scale, y + oy + row * scale,
                                      scale, scale, c)
                cx += 6 * scale

    def text_center(self, y, s, scale, c, bold=False):
        x = (self.w - text_width(s, scale)) // 2
        self.text(x, y, s, scale, c, bold=bold)

    def text_center_in(self, x0, w, y, s, scale, c, bold=False):
        x = x0 + (w - text_width(s, scale)) // 2
        self.text(x, y, s, scale, c, bold=bold)

    def png_bytes(self):
        raw = bytearray()
        stride = self.w * 3
        for y in range(self.h):
            raw.append(0)
            raw += self.pix[y * stride:(y + 1) * stride]
        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out
        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


# --- icons, drawn in a 96x96 box ---------------------------------------
def draw_icon(cv, kind, x, y, colour):
    cx, cy = x + 48, y + 48
    if kind == "globe":
        cv.circle(cx, cy, 34, colour)
        cv.line(cx - 34, cy, cx + 34, cy, WHITE, 3)
        cv.line(cx, cy - 34, cx, cy + 34, WHITE, 3)
        cv.circle(cx, cy, 34, WHITE, fill=False)
        cv.rect(cx - 20, cy - 8, 40, 4, WHITE)
        cv.rect(cx - 20, cy + 6, 40, 4, WHITE)
    elif kind == "missile":
        cv.rect(cx - 34, cy - 7, 56, 14, colour)
        cv.triangle((cx + 22, cy - 13), (cx + 22, cy + 13), (cx + 42, cy), colour)
        cv.triangle((cx - 34, cy - 7), (cx - 44, cy - 24), (cx - 26, cy - 7), colour)
        cv.triangle((cx - 34, cy + 7), (cx - 44, cy + 24), (cx - 26, cy + 7), colour)
        cv.circle(cx + 10, cy, 5, WHITE)
    elif kind == "drop":
        cv.triangle((cx, cy - 36), (cx - 26, cy + 6), (cx + 26, cy + 6), colour)
        cv.circle(cx, cy + 6, 26, colour)
        cv.circle(cx - 9, cy + 2, 6, WHITE)


# --- content: 32 stories, all from 24 Nov 2026 reports -----------------
# 3 leads: (tag, icon, colour, headline, caption)
LEADS = [
    ("TECH", "globe", GREEN,
     "HUAWEI FOUND GUILTY",
     "US jury convicts on 10 of 12 counts. Trade secrets, bank "
     "fraud, sanctions violations."),
    ("GULF", "missile", RED,
     "DRONE HITS RIYADH TOWER",
     "Houthi strike wounds 11 in the financial district. Second "
     "hit in under a week."),
    ("HORMUZ", "drop", ORANGE,
     "4 TANKERS HIT MINES",
     "IRGC says mines hit tankers in Hormuz. Claims unconfirmed."),
]

# 16 brief stories: (colour, headline, caption) - 2 columns x 8 rows
BRIEFS = [
    (BLUE, "UKRAINE HITS RUSSIAN SHIPS",
     "DRONES STRIKE IN FINLAND GULF, LIBYA"),
    (RED, "ZAPORIZHZHIA STRIKE KILLS 2",
     "40 WOUNDED, 4 CHILDREN, IN FLAT HIT"),
    (ORANGE, "ISRAEL KILLS HAMAS SECURITY CHIEF",
     "GAZA STRIKE DESPITE CEASEFIRE"),
    (RED, "HOUTHIS 60 KM FROM ADEN",
     "YEMEN ARMY: READY TO ATTACK"),
    (BLUE, "UK SANCTIONS HOUTHIS",
     "FREEZES, TRAVEL BANS ON 4 OFFICIALS"),
    (ORANGE, "SAUDI STRIKES KILL 25 IN YEMEN",
     "BUSES, TRUCKS HIT IN LAHJ"),
    (TEAL, "IRAQ TAKES KURDISH OILFIELDS",
     "KURDISH PM: UNACCEPTABLE"),
    (GREEN, "NVIDIA SOARS 31% ON HUANG RETURN",
     "NASDAQ UP 6.5%, S&P UP 4.75%"),
    (PURPLE, "US BLACKLISTS MEGASPEED",
     "7 FIRMS IN NVIDIA SCANDAL LISTED"),
    (TEAL, "CHINA EXTENDS MINERALS BAN PAUSE",
     "GALLIUM, GERMANIUM TO JAN 2027"),
    (BLUE, "PENTAGON REBUKES CANADA",
     "ONLY 41.9% OF AIR FLEET READY"),
    (GREEN, "SENEGAL REGAIN AFRICA CUP",
     "CAS OVERTURNS MOROCCO RULING"),
    (GREEN, "REAL MADRID THRASH PSV 5-1",
     "MBAPPE SCORES TWICE AT BERNABEU"),
    (ORANGE, "5.6 QUAKE SHAKES NEPAL",
     "FELT IN KATHMANDU, SIKKIM"),
    (RED, "47,000 WOMEN KILLED BY FAMILY",
     "UN: 5 WOMEN AN HOUR WORLDWIDE"),
    (TEAL, "EBOLA WORKERS TRAPPED IN CONGO",
     "WHO STAFF SHELTER AMID FIGHTING"),
]

# 13 more one-line stories
ALSO = [
    "ICJ: MYANMAR GUILTY OF ROHINGYA GENOCIDE",
    "GAZA MENINGITIS ALERT: 272 CASES IN OCTOBER, 15 DEAD",
    "HANOI RESTAURANT BLAST KILLS AT LEAST 6",
    "25 HOSTAGES HELD AT CARTAGENA SUPERMARKET",
    "CAR BOMB IN VILLAVICENCIO INJURES 23",
    "TURKISH HELICOPTER CRASH KILLS 5",
    "INDONESIA NAMES 2 VP CANDIDATES TO REPLACE GIBRAN",
    "MALAYSIA TO RETURN MIGRANTS TO MYANMAR",
    "HASINA PLANS BANGLADESH RETURN ON 16 DEC",
    "CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING",
    "UN CHIEF CALLS FOR GLOBAL AI SAFETY FRAMEWORK",
    "NATO VOWS DEFENCE AGAINST SPACE THREAT",
    "AUSTRALIA SETS 46 AI GOVERNANCE RULES",
]

# Schematic world map: (cx, cy, rx, ry) land blobs, then red dots
MAP_LAND = [
    (140, 436, 78, 12),   # North America
    (232, 452, 26, 9),    # South America
    (480, 432, 30, 8),    # Europe
    (496, 450, 32, 12),   # Africa
    (660, 436, 122, 12),  # Asia
    (790, 454, 40, 6),    # SE Asia
    (852, 456, 30, 6),    # Australia
]
# (dot x, dot y, label, label x, label y)
MAP_DOTS = [
    (120, 434, "WASHINGTON", 130, 426),
    (470, 430, "KYIV", 434, 418),
    (530, 444, "RIYADH", 542, 436),
    (600, 434, "HORMUZ", 610, 426),
    (490, 456, "LIBYA", 438, 452),
    (700, 434, "NEPAL", 710, 426),
    (790, 454, "JAKARTA", 800, 446),
]


def build():
    cv = Canvas(W, H, WHITE)
    # --- masthead: dark navy, bright yellow, white date ---
    cv.rect(0, 0, W, 88, NAVY)
    cv.rect(0, 88, W, 4, GOLD)
    cv.text_center(4, "THE WORLD IN ONE DAY", 3, GOLD, bold=True)
    cv.text_center(28, "TUESDAY 24 NOVEMBER 2026", 5, WHITE, bold=True)
    cv.text_center(70, "32 STORIES - 7 REGIONS - HUAWEI GUILTY - "
                  "RIYADH HIT - HORMUZ MINES", 2, GOLD2, bold=True)
    # --- numbers strip: saturated red, white bold text ---
    cv.rect(0, 92, W, 22, BRIGHTRED)
    cv.text_center(98, "4 TANKERS HIT MINES - 11 WOUNDED IN RIYADH - "
                  "31% NVIDIA JUMP - 47,000 WOMEN KILLED", 2, WHITE, bold=True)
    # --- region strip: gold bar, navy bold text, all 7 regions explicit ---
    cv.rect(0, 114, W, 20, GOLD)
    cv.text_center(120, "EUROPE 6 - MIDDLE EAST 7 - AMERICAS 4 - "
                  "ASIA-PACIFIC 9 - AFRICA 2 - OCEANIA 1 - WORLD 3",
                  1, NAVY, bold=True)
    # --- 3 lead stories, each with its own saturated identity ---
    lead_y, lead_h, lead_w = 134, 258, 304
    tints = [GREEN_TINT, RED_TINT, ORANGE_TINT]
    for i, (tag, icon, colour, headline, caption) in enumerate(LEADS):
        x = 24 + i * (lead_w + 32)
        cv.rect(x, lead_y, lead_w, lead_h, tints[i])
        cv.rect(x, lead_y, lead_w, 4, colour)
        # coloured tag bar with white bold text
        cv.rect(x, lead_y + 4, lead_w, 24, colour)
        cv.text_center_in(x, lead_w, lead_y + 10, tag, 2, WHITE, bold=True)
        # icon on a white disc so it pops on the tint
        cv.circle(x + 152, lead_y + 78, 46, WHITE)
        draw_icon(cv, icon, x + 104, lead_y + 30, colour)
        # headline: large, bold, dark
        lines = wrap_text(headline, 3, lead_w - 24)
        hy = lead_y + 132
        for line in lines[:2]:
            cv.text_center_in(x, lead_w, hy, line, 3, INK, bold=True)
            hy += 22
        cv.line(x + 32, lead_y + 182, x + lead_w - 32, lead_y + 182, colour, 2)
        clines = wrap_text(caption, 2, lead_w - 32)
        cy = lead_y + 190
        for line in clines[:4]:
            cv.text(x + 16, cy, line, 2, DARK)
            cy += 17
    # --- schematic map: pale mint sea, blue-green land, labelled dots ---
    cv.text_center(396, "WHERE IT HAPPENED", 2, NAVY, bold=True)
    cv.rect(24, 412, W - 48, 52, MAPBG)
    cv.rect(24, 412, W - 48, 3, NAVY)
    for (cx, cy, rx, ry) in MAP_LAND:
        cv.ellipse(cx, cy, rx, ry, MAPLAND)
    cv.ellipse(660, 436, 122, 12, MAPLAND2)
    for (dx, dy, label, lx, ly) in MAP_DOTS:
        cv.circle(dx, dy, 7, WHITE)
        cv.circle(dx, dy, 5, BRIGHTRED)
        lw = text_width(label, 1)
        cv.rect(lx - 3, ly - 2, lw + 6, 11, WHITE)
        cv.text(lx, ly, label, 1, NAVY, bold=True)
    # --- brief grid: coloured header bar, alternating rows ---
    cv.rect(24, 468, W - 48, 22, NAVY)
    cv.text(36, 475, "THE DAY IN BRIEF", 2, WHITE, bold=True)
    row_y, row_h = 490, 34
    for r in range(8):
        y = row_y + r * row_h
        cv.rect(24, y, W - 48, 34, WHITE if r % 2 == 0 else YELLOW_ROW)
        for c in range(2):
            idx = r * 2 + c
            colour, headline, caption = BRIEFS[idx]
            x = 24 + c * 500
            cv.rect(x, y, 8, 34, colour)
            cv.text(x + 16, y + 2, headline, 2, INK, bold=True)
            cv.text(x + 16, y + 18, caption, 2, DARK)
    # --- also list: coloured header bar, coloured square bullets ---
    cv.rect(24, 766, W - 48, 22, RED)
    cv.text(36, 773, "ALSO ON TUESDAY 24 NOVEMBER", 2, WHITE, bold=True)
    palette = [GREEN, RED, ORANGE, BLUE, TEAL, PURPLE]
    ay = 790
    for i, item in enumerate(ALSO):
        cv.rect(24, ay + 3, 8, 8, palette[i % len(palette)])
        cv.text(40, ay, item, 2, INK)
        ay += 14
    # --- footer: date check + sources, fully inside with a margin ---
    cv.rect(0, 978, W, 2, NAVY)
    cv.text_center(984, "DATE CHECK: ALL STORIES IN 24 NOV 2026 REPORTS - "
                   "SOME EVENTS SUN 22 - MON 23 NOV", 2, DARK, bold=True)
    cv.text_center(1002, "SOURCES: DAILY SUMMARY OF, REUTERS, UN NEWS, "
                   "TSN, UEFA, JUST SECURITY - 24 NOV 2026", 2, DARK)
    return cv


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    cv = build()
    data = cv.png_bytes()
    d = os.path.dirname(out)
    try:
        if d:
            os.makedirs(d, exist_ok=True)
        with open(out, "wb") as f:
            f.write(data)
    except OSError:
        out = os.path.join(os.getcwd(), "output", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "wb") as f:
            f.write(data)
    print(out)
    print(len(data))


if __name__ == "__main__":
    main()
