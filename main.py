#!/usr/bin/env python3
"""THE WORLD TODAY - Tuesday 24 November 2026.

A one-page newspaper front page summing up the world's news of
Tuesday 24 November 2026: 32 stories, 7 regions. Drawn from scratch
with the standard library only: own bitmap font, own canvas, own
PNG encoder. Deterministic: no time, no randomness, no network.
Writes a 1024x1024 PNG to /output/entry.png, or to argv[1].
"""

import binascii
import os
import struct
import sys
import zlib

W = 1024
H = 1024

PAPER = (247, 243, 232)
INK = (20, 20, 20)
RED = (163, 22, 33)
BLUE = (29, 78, 137)
GREY = (96, 92, 82)
LIGHT = (233, 228, 214)
SEA = (214, 226, 232)
LAND = (198, 206, 178)
LANDLINE = (110, 118, 92)
WHITE = (255, 255, 255)

PIX = bytearray(W * H * 3)


def set_px(x, y, col):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i] = col[0]
        PIX[i + 1] = col[1]
        PIX[i + 2] = col[2]


def fill_rect(x, y, w, h, col):
    for yy in range(y, y + h):
        if yy < 0 or yy >= H:
            continue
        base = (yy * W + max(x, 0)) * 3
        for xx in range(max(x, 0), min(x + w, W)):
            PIX[base] = col[0]
            PIX[base + 1] = col[1]
            PIX[base + 2] = col[2]
            base += 3


def hline(x, y, w, col, t=1):
    fill_rect(x, y, w, t, col)


def vline(x, y, h, col, t=1):
    fill_rect(x, y, t, h, col)


def rect(x, y, w, h, col, t=1):
    hline(x, y, w, col, t)
    hline(x, y + h - t, w, col, t)
    vline(x, y, h, col, t)
    vline(x + w - t, y, h, col, t)


def line(x0, y0, x1, y1, col):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    while True:
        set_px(x, y, col)
        if x == x1 and y == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def disc(cx, cy, r, col):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                set_px(xx, yy, col)


def poly_fill(points, col):
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    top, bot = min(ys), max(ys)
    n = len(points)
    for y in range(top, bot + 1):
        xs = []
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if y0 == y1:
                continue
            if (y0 <= y < y1) or (y1 <= y < y0):
                xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            xa = int(xs[k])
            xb = int(xs[k + 1])
            for xx in range(xa, xb + 1):
                set_px(xx, y, col)


def poly_outline(points, col):
    n = len(points)
    for i in range(n):
        x0, y0 = points[i]
        x1, y1 = points[(i + 1) % n]
        line(x0, y0, x1, y1, col)


# ---------------------------------------------------------------- font
# A 5x7 bitmap font, drawn by hand here. Each glyph is 7 rows of 5
# cells; '#' is ink, '.' is empty. Only capitals, digits and a few
# punctuation marks: all page text is set in capitals, newspaper style.

FONT = {}


def _glyph(rows):
    return rows


FONT["A"] = _glyph([
    ".###.",
    "#...#",
    "#...#",
    "#####",
    "#...#",
    "#...#",
    "#...#",
])
FONT["B"] = _glyph([
    "####.",
    "#...#",
    "#...#",
    "####.",
    "#...#",
    "#...#",
    "####.",
])
FONT["C"] = _glyph([
    ".####",
    "#....",
    "#....",
    "#....",
    "#....",
    "#....",
    ".####",
])
FONT["D"] = _glyph([
    "####.",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "####.",
])
FONT["E"] = _glyph([
    "#####",
    "#....",
    "#....",
    "####.",
    "#....",
    "#....",
    "#####",
])
FONT["F"] = _glyph([
    "#####",
    "#....",
    "#....",
    "####.",
    "#....",
    "#....",
    "#....",
])
FONT["G"] = _glyph([
    ".####",
    "#....",
    "#....",
    "#..##",
    "#...#",
    "#...#",
    ".###.",
])
FONT["H"] = _glyph([
    "#...#",
    "#...#",
    "#...#",
    "#####",
    "#...#",
    "#...#",
    "#...#",
])
FONT["I"] = _glyph([
    ".###.",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    ".###.",
])
FONT["J"] = _glyph([
    "..###",
    "...#.",
    "...#.",
    "...#.",
    "...#.",
    "#..#.",
    ".##..",
])
FONT["K"] = _glyph([
    "#...#",
    "#..#.",
    "#.#..",
    "##...",
    "#.#..",
    "#..#.",
    "#...#",
])
FONT["L"] = _glyph([
    "#....",
    "#....",
    "#....",
    "#....",
    "#....",
    "#....",
    "#####",
])
FONT["M"] = _glyph([
    "#...#",
    "##.##",
    "#.#.#",
    "#.#.#",
    "#...#",
    "#...#",
    "#...#",
])
FONT["N"] = _glyph([
    "#...#",
    "##..#",
    "#.#.#",
    "#..##",
    "#...#",
    "#...#",
    "#...#",
])
FONT["O"] = _glyph([
    ".###.",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    ".###.",
])
FONT["P"] = _glyph([
    "####.",
    "#...#",
    "#...#",
    "####.",
    "#....",
    "#....",
    "#....",
])
FONT["Q"] = _glyph([
    ".###.",
    "#...#",
    "#...#",
    "#...#",
    "#.#.#",
    "#..#.",
    ".##.#",
])
FONT["R"] = _glyph([
    "####.",
    "#...#",
    "#...#",
    "####.",
    "#.#..",
    "#..#.",
    "#...#",
])
FONT["S"] = _glyph([
    ".####",
    "#....",
    "#....",
    ".###.",
    "....#",
    "....#",
    "####.",
])
FONT["T"] = _glyph([
    "#####",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
])
FONT["U"] = _glyph([
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    ".###.",
])
FONT["V"] = _glyph([
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    "#...#",
    ".#.#.",
    "..#..",
])
FONT["W"] = _glyph([
    "#...#",
    "#...#",
    "#...#",
    "#.#.#",
    "#.#.#",
    "##.##",
    "#...#",
])
FONT["X"] = _glyph([
    "#...#",
    "#...#",
    ".#.#.",
    "..#..",
    ".#.#.",
    "#...#",
    "#...#",
])
FONT["Y"] = _glyph([
    "#...#",
    "#...#",
    ".#.#.",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
])
FONT["Z"] = _glyph([
    "#####",
    "....#",
    "...#.",
    "..#..",
    ".#...",
    "#....",
    "#####",
])
FONT["0"] = _glyph([
    ".###.",
    "#...#",
    "#..##",
    "#.#.#",
    "##..#",
    "#...#",
    ".###.",
])
FONT["1"] = _glyph([
    "..#..",
    ".##..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    ".###.",
])
FONT["2"] = _glyph([
    ".###.",
    "#...#",
    "....#",
    "...#.",
    "..#..",
    ".#...",
    "#####",
])
FONT["3"] = _glyph([
    "####.",
    "....#",
    "....#",
    ".###.",
    "....#",
    "....#",
    "####.",
])
FONT["4"] = _glyph([
    "...#.",
    "..##.",
    ".#.#.",
    "#..#.",
    "#####",
    "...#.",
    "...#.",
])
FONT["5"] = _glyph([
    "#####",
    "#....",
    "####.",
    "....#",
    "....#",
    "#...#",
    ".###.",
])
FONT["6"] = _glyph([
    ".###.",
    "#....",
    "#....",
    "####.",
    "#...#",
    "#...#",
    ".###.",
])
FONT["7"] = _glyph([
    "#####",
    "....#",
    "...#.",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
])
FONT["8"] = _glyph([
    ".###.",
    "#...#",
    "#...#",
    ".###.",
    "#...#",
    "#...#",
    ".###.",
])
FONT["9"] = _glyph([
    ".###.",
    "#...#",
    "#...#",
    ".####",
    "....#",
    "....#",
    ".###.",
])
FONT[" "] = _glyph([
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
])
FONT["."] = _glyph([
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
    "..##.",
    "..##.",
])
FONT[","] = _glyph([
    ".....",
    ".....",
    ".....",
    ".....",
    "..##.",
    "..#..",
    ".#...",
])
FONT["-"] = _glyph([
    ".....",
    ".....",
    ".....",
    "#####",
    ".....",
    ".....",
    ".....",
])
FONT["'"] = _glyph([
    "..#..",
    "..#..",
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
])
FONT["!"] = _glyph([
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    "..#..",
    ".....",
    "..#..",
])
FONT["?"] = _glyph([
    ".###.",
    "#...#",
    "....#",
    "...#.",
    "..#..",
    ".....",
    "..#..",
])
FONT["/"] = _glyph([
    "....#",
    "....#",
    "...#.",
    "..#..",
    ".#...",
    "#....",
    "#....",
])
FONT["("] = _glyph([
    "...#.",
    "..#..",
    ".#...",
    ".#...",
    ".#...",
    "..#..",
    "...#.",
])
FONT[")"] = _glyph([
    ".#...",
    "..#..",
    "...#.",
    "...#.",
    "...#.",
    "..#..",
    ".#...",
])
FONT["%"] = _glyph([
    "#...#",
    "#..#.",
    "...#.",
    "..#..",
    ".#...",
    "#..#.",
    "#...#",
])
FONT["+"] = _glyph([
    ".....",
    "..#..",
    "..#..",
    "#####",
    "..#..",
    "..#..",
    ".....",
])
FONT["&"] = _glyph([
    ".##..",
    "#..#.",
    "#..#.",
    ".#...",
    "#.#.#",
    "#..#.",
    ".##.#",
])
FONT["="] = _glyph([
    ".....",
    ".....",
    "#####",
    ".....",
    "#####",
    ".....",
    ".....",
])
FONT[";"] = _glyph([
    ".....",
    "..##.",
    "..##.",
    ".....",
    "..##.",
    "..#..",
    ".#...",
])
FONT[":"] = _glyph([
    ".....",
    "..##.",
    "..##.",
    ".....",
    "..##.",
    "..##.",
    ".....",
])
FONT["*"] = _glyph([
    ".....",
    ".#.#.",
    "..#..",
    "#####",
    "..#..",
    ".#.#.",
    ".....",
])
FONT['"'] = _glyph([
    ".#.#.",
    ".#.#.",
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
])
FONT["_"] = _glyph([
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
    ".....",
    "#####",
])
FONT["<"] = _glyph([
    "....#",
    "...#.",
    "..#..",
    ".#...",
    "..#..",
    "...#.",
    "....#",
])
FONT[">"] = _glyph([
    "#....",
    ".#...",
    "..#..",
    "...#.",
    "..#..",
    ".#...",
    "#....",
])
FONT["$"] = _glyph([
    "..#..",
    ".####",
    "#.#.#",
    ".###.",
    "..#.#",
    "####.",
    "..#..",
])
FONT["@"] = _glyph([
    ".###.",
    "#...#",
    "#.###",
    "#.#.#",
    "#.###",
    "#....",
    ".###.",
])
FONT["["] = _glyph([
    ".###.",
    ".#...",
    ".#...",
    ".#...",
    ".#...",
    ".#...",
    ".###.",
])
FONT["]"] = _glyph([
    ".###.",
    "...#.",
    "...#.",
    "...#.",
    "...#.",
    "...#.",
    ".###.",
])


# ------------------------------------------------------------ text out
def draw_char(x, y, ch, scale, col):
    rows = FONT.get(ch, FONT["A"])
    for r in range(7):
        row = rows[r].ljust(5, ".")
        for c in range(5):
            if row[c] == "#":
                fill_rect(x + c * scale, y + r * scale, scale, scale, col)


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(x, y, s, scale, col, bold=False):
    s = s.upper()
    cx = x
    for ch in s:
        draw_char(cx, y, ch, scale, col)
        if bold:
            draw_char(cx + max(1, scale // 2), y, ch, scale, col)
        cx += 6 * scale
    return cx


def draw_centred(cx, y, s, scale, col, bold=False):
    draw_text(cx - text_w(s, scale) // 2, y, s, scale, col, bold)


def draw_right(rx, y, s, scale, col, bold=False):
    draw_text(rx - text_w(s, scale), y, s, scale, col, bold)


def wrap(s, scale, maxw):
    words = s.upper().split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if text_w(trial, scale) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(x, y, s, scale, maxw, col, max_lines=None, leading=None):
    if leading is None:
        leading = 7 * scale + 3
    lines = wrap(s, scale, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(x, y + i * leading, ln, scale, col)
    return y + len(lines) * leading


def draw_wrapped_centred(cx, y, s, scale, maxw, col, max_lines=None):
    lines = wrap(s, scale, maxw)
    if max_lines is not None:
        lines = lines[:max_lines]
    leading = 7 * scale + 3
    for i, ln in enumerate(lines):
        draw_centred(cx, y + i * leading, ln, scale, col)
    return y + len(lines) * leading


# ------------------------------------------------------------ png out
def _chunk(kind, data):
    crc = binascii.crc32(kind + data) & 0xFFFFFFFF
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", crc)


def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(PIX[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)
    head = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    out = b"\x89PNG\r\n\x1a\n"
    out += _chunk(b"IHDR", head)
    out += _chunk(b"IDAT", comp)
    out += _chunk(b"IEND", b"")
    return out


def save(path):
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png_bytes())

# ------------------------------------------------------------ the news
# All 32 stories first reported Tuesday 24 November 2026 (see
# SOURCES.md). Three leads, sixteen briefs, thirteen also. Seven
# regions: Europe 6, Middle East 7, Americas 4, Asia-Pacific 9,
# Africa 2, Oceania 1, World 3.

LEADS = [
    (
        "UNITED STATES - VERDICT",
        "HUAWEI GUILTY ON 10 OF 12 COUNTS",
        "A US JURY CONVICTS HUAWEI OF TRADE-SECRET THEFT, BANK "
        "FRAUD AND SANCTIONS VIOLATIONS, AND ACQUITS IT OF "
        "RACKETEERING.",
    ),
    (
        "SAUDI ARABIA - DRONE ATTACK",
        "DRONE HITS RIYADH PIF TOWER; 11 WOUNDED",
        "A SUSPECTED HOUTHI DRONE STRIKES A TOWER IN RIYADH'S "
        "KING ABDULLAH FINANCIAL DISTRICT. THE SECOND STRIKE IN "
        "UNDER A WEEK.",
    ),
    (
        "STRAIT OF HORMUZ - MINES",
        "4 TANKERS HIT MINES AND CATCH FIRE",
        "IRAN'S IRGC SAYS FOUR TANKERS HIT NAVAL MINES IN THE "
        "STRAIT AND CAUGHT FIRE. THE MINE CLAIMS ARE UNCONFIRMED.",
    ),
]

NUMBERS = [
    ("4", "TANKERS HIT BY MINES IN THE STRAIT OF HORMUZ"),
    ("11", "WOUNDED IN THE RIYADH PIF TOWER ATTACK"),
    ("25", "HOSTAGES HELD AT A CARTAGENA SUPERMARKET"),
    ("47,000", "WOMEN KILLED BY PARTNERS OR FAMILY IN A YEAR - UN"),
    ("5.6", "MAGNITUDE OF THE EARTHQUAKE IN EASTERN NEPAL"),
    ("+31%", "NVIDIA SHARE JUMP AS HUANG RETURNS AS CEO"),
]

BRIEFS = [
    ("UKRAINE HITS RUSSIAN SHIPS",
     "KYIV ACKNOWLEDGES A DRONE STRIKE ON THE CARGO SHIP SPARTA II; "
     "NAVAL DRONES HIT SHIPS OFF LIBYA."),
    ("ZAPORIZHZHIA STRIKE",
     "OVERNIGHT RUSSIAN ATTACK KILLS 2 AND WOUNDS 40, INCLUDING "
     "FOUR CHILDREN."),
    ("ISRAEL KILLS HAMAS SECURITY CHIEF",
     "BRIG. GEN. NAEEM ABU NAHEL KILLED IN GAZA DESPITE THE "
     "CEASEFIRE SINCE OCTOBER 2025."),
    ("HOUTHIS 60 KM FROM ADEN",
     "YEMEN'S MILITARY SAYS HOUTHI FIGHTERS ARE READY TO ATTACK "
     "THE TEMPORARY CAPITAL."),
    ("UK SANCTIONS HOUTHIS",
     "ASSET FREEZES AND TRAVEL BANS ON THE HOUTHIS AND FOUR SENIOR "
     "OFFICIALS."),
    ("SAUDI STRIKES KILL 25 IN YEMEN",
     "STRIKES ON BUSES AND TRUCKS IN WADI MAABAQ, LAHJ; SIX "
     "WOUNDED, 25 DEAD OR MISSING."),
    ("IRAQ TAKES KURDISH OILFIELDS",
     "BAGHDAD ORDERS FEDERAL CONTROL OF OILFIELDS; KURDISH PM CALLS "
     "IT UNACCEPTABLE."),
    ("NVIDIA SURGES 31%",
     "SHARES JUMP AS JENSEN HUANG RETURNS AS CEO; NASDAQ UP 6.5%, "
     "S&P 500 UP 4.75%."),
    ("US BLACKLISTS MEGASPEED",
     "SINGAPORE FIRM AT THE CENTRE OF THE NVIDIA SCANDAL JOINS THE "
     "US ENTITY LIST."),
    ("CHINA EXTENDS MINERALS BAN PAUSE",
     "SUSPENSION OF THE GALLIUM, GERMANIUM AND ANTIMONY EXPORT BAN "
     "EXTENDED TO 27 JANUARY 2027."),
    ("PENTAGON REBUKES CANADA",
     "US SAYS CANADA FALLS SHORT AS A DEFENCE PARTNER; ONLY 41.9% "
     "OF ITS AIR FLEET SERVICEABLE."),
    ("SENEGAL REGAIN AFRICA CUP",
     "CAS OVERTURNS THE RULING THAT GAVE THE TROPHY TO MOROCCO; "
     "SENEGAL'S 1-0 WIN REINSTATED."),
    ("REAL MADRID THRASH PSV 5-1",
     "MBAPPE SCORES TWICE AT THE BERNABEU; REAL STAY PERFECT, "
     "5 WINS FROM 5."),
    ("5.6 QUAKE SHAKES NEPAL",
     "EPICENTRE NEAR THE TIBET BORDER; FELT IN KATHMANDU, SIKKIM "
     "AND BANGLADESH. NO CASUALTIES."),
    ("5 WOMEN KILLED EVERY HOUR",
     "UN: 47,000 WOMEN AND GIRLS KILLED BY PARTNERS OR FAMILY "
     "LAST YEAR."),
    ("EBOLA WORKERS TRAPPED IN CONGO",
     "HEALTH WORKERS SHELTER IN A HOSPITAL IN ITURI FOR OVER "
     "48 HOURS AMID FIGHTING."),
]

ALSO = [
    "20. ICJ: MYANMAR GUILTY OF ROHINGYA GENOCIDE, 9-6 RULING",
    "21. GAZA MENINGITIS ALERT: 272 CASES IN OCTOBER, 15 DEAD",
    "22. HANOI RESTAURANT BLAST KILLS AT LEAST 6",
    "23. GUNMEN HOLD 25 HOSTAGES AT CARTAGENA SUPERMARKET",
    "24. CAR BOMB IN VILLAVICENCIO INJURES 23",
    "25. TURKISH HELICOPTER CRASH KILLS 5",
    "26. INDONESIA NAMES 2 CANDIDATES TO REPLACE VP GIBRAN",
    "27. MALAYSIA TO SEND THOUSANDS OF MIGRANTS BACK TO MYANMAR",
    "28. HASINA PLANS RETURN TO BANGLADESH ON 16 DECEMBER",
    "29. CHINA SENTENCES OFFICIAL TO DEATH FOR SPYING",
    "30. UN CHIEF CALLS FOR GLOBAL AI SAFETY FRAMEWORK",
    "31. NATO VOWS DEFENCE AGAINST SPACE THREAT",
    "32. AUSTRALIA SETS OUT 46 AI GOVERNANCE RECOMMENDATIONS",
]

# Schematic continents, drawn as rough polygons inside the map box.
CONTINENTS = [
    [(70, 375), (150, 362), (235, 368), (255, 392), (215, 415),
     (175, 428), (130, 420), (85, 405)],
    [(255, 362), (275, 358), (285, 368), (265, 375)],
    [(235, 432), (275, 428), (295, 448), (275, 482), (250, 478),
     (232, 455)],
    [(470, 368), (520, 358), (548, 372), (535, 392), (500, 396),
     (478, 382)],
    [(478, 408), (540, 402), (568, 428), (548, 468), (512, 478),
     (488, 442)],
    [(552, 362), (700, 352), (775, 368), (760, 398), (700, 418),
     (640, 412), (585, 398), (555, 380)],
    [(700, 425), (725, 420), (730, 432), (705, 436)],
    [(735, 438), (755, 435), (758, 445), (738, 448)],
    [(705, 452), (752, 448), (765, 466), (730, 480), (700, 470)],
]

# (x, y, label, label dx, label dy) - places in the day's news.
DOTS = [
    (522, 376, "KYIV", 8, -3),
    (490, 370, "LONDON", -52, -3),
    (588, 402, "RIYADH", 8, -14),
    (612, 406, "HORMUZ", 10, 4),
    (556, 392, "GAZA", -38, -3),
    (600, 430, "ADEN", 8, -3),
    (452, 420, "SENEGAL", -62, -3),
    (525, 448, "ITURI", 8, -3),
    (668, 392, "KATHMANDU", 8, -3),
    (700, 408, "HANOI", 8, -3),
    (150, 438, "CARTAGENA", 8, -3),
    (738, 466, "CANBERRA", 8, -3),
]

# ------------------------------------------------------------ layout
MARGIN = 28
RIGHT = 996


def section_head(y, text, note=None):
    draw_text(MARGIN, y, text, 2, RED, bold=True)
    if note:
        draw_right(RIGHT, y + 3, note, 1, GREY)
    hline(MARGIN, y + 20, RIGHT - MARGIN, INK, 2)


def draw_masthead():
    fill_rect(0, 0, W, 6, INK)
    draw_centred(W // 2, 16, "THE WORLD TODAY", 7, INK)
    draw_text(MARGIN, 38, "VOL. II", 1, GREY)
    draw_right(RIGHT, 38, "TUESDAY EDITION", 1, GREY)
    hline(MARGIN, 74, RIGHT - MARGIN, INK, 3)
    hline(MARGIN, 79, RIGHT - MARGIN, RED, 1)
    draw_text(MARGIN, 88, "TUESDAY 24 NOVEMBER 2026", 2, INK, bold=True)
    draw_right(RIGHT, 88, "32 STORIES - 7 REGIONS", 2, INK, bold=True)
    hline(MARGIN, 108, RIGHT - MARGIN, INK, 1)


def draw_numbers():
    y = 116
    box_w = 156
    gap = 6
    for i, (big, label) in enumerate(NUMBERS):
        x = MARGIN + i * (box_w + gap)
        rect(x, y, box_w, 54, GREY, 1)
        draw_centred(x + box_w // 2, y + 6, big, 2, RED, bold=True)
        draw_wrapped_centred(x + box_w // 2, y + 27, label, 1,
                             box_w - 10, GREY, max_lines=2)


def draw_leads():
    section_head(178, "THE LEADS")
    xs = [28, 357, 686]
    for col, (kicker, head, body) in enumerate(LEADS):
        x = xs[col]
        draw_text(x, 206, kicker, 1, RED, bold=True)
        draw_wrapped(x, 218, head, 2, 310, INK, max_lines=2, leading=17)
        draw_wrapped(x, 256, body, 1, 310, INK, max_lines=5, leading=10)
    vline(347, 206, 100, LIGHT, 1)
    vline(676, 206, 100, LIGHT, 1)


def draw_map():
    section_head(322, "WHERE IT HAPPENED", "SCHEMATIC MAP - NOT TO SCALE")
    rect(MARGIN, 342, RIGHT - MARGIN, 146, INK, 1)
    fill_rect(MARGIN + 1, 343, RIGHT - MARGIN - 2, 144, SEA)
    for poly in CONTINENTS:
        poly_fill(poly, LAND)
        poly_outline(poly, LANDLINE)
    draw_text(95, 392, "N. AMERICA", 1, GREY)
    draw_text(228, 458, "S. AMERICA", 1, GREY)
    draw_text(505, 435, "AFRICA", 1, GREY)
    draw_text(640, 378, "ASIA", 1, GREY)
    draw_text(700, 478, "AUSTRALIA", 1, GREY)
    for (dx, dy, label, lx, ly) in DOTS:
        disc(dx, dy, 5, INK)
        disc(dx, dy, 3, RED)
        draw_text(dx + lx, dy + ly, label, 1, INK, bold=True)


def draw_briefs():
    section_head(496, "THE DAY IN BRIEF - 16 STORIES")
    xs = [28, 273, 518, 763]
    ys = [522, 592, 662, 732]
    for i, (head, body) in enumerate(BRIEFS):
        col = i % 4
        row = i // 4
        x = xs[col]
        y = ys[row]
        draw_text(x, y, "%02d" % (i + 4), 1, RED, bold=True)
        draw_wrapped(x + 20, y, head, 1, 213, INK, max_lines=2, leading=10)
        draw_wrapped(x, y + 22, body, 1, 233, INK, max_lines=3, leading=10)
    for vx in (261, 506, 751):
        vline(vx, 522, 276, LIGHT, 1)
    for hy in (588, 658, 728):
        hline(MARGIN, hy, RIGHT - MARGIN, LIGHT, 1)


def draw_also():
    section_head(806, "ALSO ON TUESDAY 24 NOVEMBER")
    for i, item in enumerate(ALSO):
        col = i // 7
        row = i % 7
        x = MARGIN if col == 0 else 524
        draw_text(x, 832 + row * 19, item, 1, INK)


def draw_footer():
    hline(MARGIN, 972, RIGHT - MARGIN, INK, 2)
    draw_wrapped(MARGIN, 980,
                 "DATE CHECK: THE ICJ GENOCIDE RULING WAS HANDED DOWN ON "
                 "19 NOVEMBER; IT DROVE THE NEWS OF 24 NOVEMBER. UKRAINE "
                 "SHIP STRIKES WERE ON 22 NOVEMBER, ACKNOWLEDGED ON "
                 "24 NOVEMBER. THE VILLAVICENCIO BOMB WAS ON MONDAY NIGHT, "
                 "REPORTED ON TUESDAY.",
                 1, RIGHT - MARGIN, INK, max_lines=2, leading=10)
    draw_text(MARGIN, 1002,
              "SOURCES: DAILY SUMMARY OF, REUTERS, UN NEWS, TSN, "
              "THE GLOBAL EYE, JUST SECURITY - SEE SOURCES.MD",
              1, GREY)


def build():
    fill_rect(0, 0, W, H, PAPER)
    draw_masthead()
    draw_numbers()
    draw_leads()
    draw_map()
    draw_briefs()
    draw_also()
    draw_footer()


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "/output/entry.png"
    build()
    save(out)


if __name__ == "__main__":
    main()
