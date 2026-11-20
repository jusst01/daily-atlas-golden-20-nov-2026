#!/usr/bin/env python3
"""THE DAILY ATLAS - front page renderer for news-image-20261120.

Draws a flat, clean 1024x1024 newspaper front page carrying 33 stories.
Pillow + numpy only; run once at build time to produce entry.png.
"""

import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")
OUT = os.path.join(HERE, "entry.png")

W = H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
CARD = (255, 253, 246)
INK = (22, 28, 26)
GREY = (104, 100, 90)
ACCENT = (27, 78, 66)
TEAL = (44, 96, 88)
NAVY = (38, 58, 92)
BORDER = (196, 190, 176)
DC_RED = (172, 62, 44)
MAP_BG = (240, 238, 230)
PILL = (90, 88, 80)
MUTED_GREY = (90, 88, 80)
RED_LINE = (204, 68, 50)

CONT = {
    "Americas": (168, 62, 44),
    "Europe": (58, 84, 128),
    "Mideast": (186, 122, 38),
    "Africa": (122, 106, 52),
    "Asia": (116, 80, 148),
    "Oceania": (44, 124, 134),
}
CONT_ORDER = ["Americas", "Europe", "Mideast", "Africa", "Asia", "Oceania"]

# ---------------------------------------------------------------- type
FONT_DIR = "/usr/share/fonts/truetype/dejavu/"
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_I = os.path.join(FONT_DIR, "DejaVuSerif-Italic.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
if not os.path.exists(SERIF_I):
    SERIF_I = SERIF  # italic file absent on this build host

_fonts = {}


def F(path, size):
    key = (path, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(path, size)
    return _fonts[key]


# ---------------------------------------------------------------- canvas
IMG = Image.new("RGB", (W, H), PAPER)
DR = ImageDraw.Draw(IMG)

CLIPS = []
NUM_DRAWN = set()
ART_USED = set()
REGIONS_DRAWN = []
STAT_CELLS = []
CHIPS_DRAWN = []


def fail(msg):
    CLIPS.append(msg)
    print("FAIL:", msg, file=sys.stderr)


# ---------------------------------------------------------------- helpers
def wrap(text, font, max_width):
    """Greedy word wrap using measured text length."""
    words = text.split()
    lines = []
    cur = ""
    for wd in words:
        trial = wd if not cur else cur + " " + wd
        if DR.textlength(trial, font=font) <= max_width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def block(x, y, w, text, font, line_height, max_y, fill=INK, anchor="la"):
    """Draw wrapped lines while the next line still fits at or below max_y."""
    lines = wrap(text, font, w)
    cy = y
    for ln in lines:
        if cy > max_y:
            fail("CLIP at (%s,%s): %r (max_y=%s)" % (x, round(y, 1), ln[:42], max_y))
            break
        DR.text((x, cy), ln, font=font, fill=fill, anchor=anchor)
        cy += line_height
    return cy


def chip(cx, cy, r, n, fill):
    """Filled number circle, white bold numeral centred."""
    DR.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill)
    f = F(SANS_B, max(4.0, r * 2 * 0.56))
    DR.text((cx, cy), str(n), font=f, fill=(255, 255, 255), anchor="mm")
    NUM_DRAWN.add(n)


def mute(col, toward=PAPER, amount=0.52):
    return tuple(int(round(c + (t - c) * amount)) for c, t in zip(col, toward))


# ---------------------------------------------------------------- banners
def banner(x, y, w, h, kind):
    """Flat procedural banner strip for a grid card."""
    s = h / 34.0                     # detail scale for 34px strips
    ls = 7.5 if h <= 44 else max(8.0, min(12.0, h * 0.33))
    lab = F(SANS_B, ls)
    lf = F(SANS_B, max(6.0, ls - 1.4))
    pale = (240, 236, 226)
    DR.rectangle([x, y, x + w, y + h], fill=pale)

    def L(txt, col, xx=None, yy=None):
        DR.text((xx if xx is not None else x + 4, yy if yy is not None else y + 2),
                txt, font=lab, fill=col, anchor="la")

    if kind == "markets":
        DR.rectangle([x, y, x + w, y + h], fill=(24, 26, 34))
        pts = [(x + w * 0.44, y + h * 0.30), (x + w * 0.58, y + h * 0.46),
               (x + w * 0.68, y + h * 0.38), (x + w * 0.80, y + h * 0.62),
               (x + w * 0.93, y + h * 0.72)]
        DR.line(pts, fill=RED_LINE, width=max(2, int(1.6 * s)))
        ax, ay = pts[-1]
        a = max(3.0, 3.2 * s)
        DR.polygon([(ax, ay + a * 0.6), (ax - a, ay - a * 0.5), (ax - a * 0.1, ay - a * 1.1)],
                   fill=RED_LINE)
        DR.rectangle([x + w * 0.40, y + h * 0.74, x + w * 0.96, y + h * 0.76], fill=(58, 62, 70))
        L("ASIA ROUT", RED_LINE)

    elif kind == "ipo":
        DR.rectangle([x, y, x + w, y + h], fill=pale)
        base = y + h - 3
        bw = w * 0.09
        for i, hh in enumerate((0.26, 0.42, 0.58)):
            bx = x + w * 0.62 + i * bw * 1.15
            DR.rectangle([bx, base - h * hh, bx + bw, base], fill=ACCENT)
        top = base - h * 0.58
        pole_x = x + w * 0.62 + 2 * bw * 1.15 + bw * 0.5
        DR.line([(pole_x, top), (pole_x, top - h * 0.20)], fill=INK, width=1)
        DR.polygon([(pole_x, top - h * 0.20), (pole_x + w * 0.045, top - h * 0.15),
                    (pole_x, top - h * 0.10)], fill=ACCENT)
        DR.rectangle([x + w * 0.60, base, x + w * 0.97, base + 1.5], fill=(120, 116, 104))
        L("ANT · INDEXES", INK)

    elif kind == "games":
        bands = [(58, 40, 80), (96, 54, 92), (140, 70, 92), (186, 96, 82),
                 (214, 132, 74), (232, 178, 74)]
        bh = h / 6.0
        for i, c in enumerate(bands):
            DR.rectangle([x, y + i * bh, x + w, y + (i + 1) * bh + 0.6], fill=c)
        sun_r = h * 0.30
        DR.ellipse([x + w * 0.70 - sun_r, y + h * 0.52 - sun_r,
                    x + w * 0.70 + sun_r, y + h * 0.52 + sun_r], fill=(250, 232, 190))
        for px, sc in ((x + w * 0.87, 1.0), (x + w * 0.945, 0.75)):
            tx = px
            ty = y + h * 0.30 * (1.0 / sc if sc else 1)
            ty = y + h - h * 0.10 * sc
            DR.line([(tx, y + h), (tx, ty)], fill=(18, 14, 20), width=max(1, int(1.6 * s)))
            for ang in (-2.5, -2.0, -1.5):
                ex = tx + math.cos(ang) * w * 0.035 * sc
                ey = ty + math.sin(ang) * w * 0.035 * sc
                DR.line([(tx, ty), (ex, ey)], fill=(18, 14, 20), width=max(1, int(1.4 * s)))
        L("$2.36BN DAY ONE", (255, 255, 255))

    elif kind == "oil":
        DR.rectangle([x, y, x + w, y + h], fill=(44, 92, 140))
        DR.rectangle([x, y + h * 0.70, x + w, y + h], fill=(36, 78, 120))
        hull = [(x + w * 0.42, y + h * 0.74), (x + w * 0.93, y + h * 0.74),
                (x + w * 0.88, y + h * 0.93), (x + w * 0.47, y + h * 0.93)]
        DR.polygon(hull, fill=(24, 34, 44))
        DR.rectangle([x + w * 0.56, y + h * 0.60, x + w * 0.66, y + h * 0.74], fill=(58, 70, 82))
        dx = x + w * 0.78
        DR.line([(dx, y + h * 0.74), (dx, y + h * 0.52)], fill=(210, 214, 218), width=1)
        for o in (-0.03, 0.0):
            DR.line([(dx, y + h * 0.56), (dx + w * o, y + h * 0.62)], fill=(210, 214, 218), width=1)
        L("BRENT $92.22", (255, 255, 255))

    elif kind == "diplomacy":
        DR.rectangle([x, y, x + w, y + h], fill=pale)
        ty = y + h * 0.62
        DR.rectangle([x + w * 0.34, ty, x + w * 0.94, ty + max(1.5, 1.6 * s)], fill=INK)
        for i in range(3):
            cx = x + w * (0.44 + i * 0.16)
            DR.rectangle([cx - w * 0.026, ty - h * 0.20, cx + w * 0.026, ty - h * 0.04], fill=(176, 170, 156))
        for i, col in enumerate((NAVY, ACCENT)):
            fx = x + w * (0.70 + i * 0.12)
            DR.line([(fx, ty), (fx, ty - h * 0.42)], fill=(110, 106, 96), width=1)
            DR.polygon([(fx, ty - h * 0.42), (fx + w * 0.055, ty - h * 0.35),
                        (fx, ty - h * 0.28)], fill=col)
        L("EUROPE · TALKS", INK)

    elif kind == "drones":
        DR.rectangle([x, y, x + w, y + h], fill=(52, 58, 66))
        for i in range(3):
            cx = x + w * (0.62 + i * 0.13)
            cy = y + h * (0.58 if i != 1 else 0.40)
            a = h * 0.16
            DR.line([(cx - a, cy - a * 0.6), (cx + a, cy + a * 0.6)], fill=(228, 228, 220), width=max(1, int(1.4 * s)))
            DR.line([(cx - a, cy + a * 0.6), (cx + a, cy - a * 0.6)], fill=(228, 228, 220), width=max(1, int(1.4 * s)))
            for rx, ry in ((-a, -a * 0.6), (a, -a * 0.6), (-a, a * 0.6), (a, a * 0.6)):
                rr = max(1.2, 1.5 * s)
                DR.ellipse([cx + rx - rr, cy + ry - rr, cx + rx + rr, cy + ry + rr], fill=(228, 228, 220))
        L("1,000+ DRONES", (255, 255, 255))

    elif kind == "space":
        DR.rectangle([x, y, x + w, y + h], fill=(16, 20, 38))
        stars = [(0.58, 0.22), (0.66, 0.72), (0.74, 0.34), (0.82, 0.62),
                 (0.88, 0.26), (0.95, 0.70), (0.70, 0.86), (0.92, 0.44)]
        for sx, sy in stars:
            DR.ellipse([x + w * sx, y + h * sy, x + w * sx + 1.4, y + h * sy + 1.4], fill=(226, 228, 236))
        for gx, gy in ((0.63, 0.46), (0.86, 0.62)):
            cx, cy = x + w * gx, y + h * gy
            for rr, st, en in ((h * 0.20, 200, 340), (h * 0.20, 20, 160)):
                DR.arc([cx - rr, cy - rr, cx + rr, cy + rr], st, en, fill=(198, 202, 220), width=1)
            DR.ellipse([cx - 1, cy - 1, cx + 1, cy + 1], fill=(236, 236, 244))
        L("MILKY WAY", (255, 255, 255))

    elif kind == "youth":
        DR.rectangle([x, y, x + w, y + h], fill=pale)
        base = y + h * 0.92
        for i, col in enumerate((NAVY, ACCENT)):
            fx = x + w * (0.72 + i * 0.15)
            DR.line([(fx, base), (fx, base - h * 0.56)], fill=(110, 106, 96), width=max(1, int(1.5 * s)))
            DR.rectangle([fx, base - h * 0.56, fx + w * 0.085, base - h * 0.30], fill=col)
        L("YOUTH MOBILITY", INK)

    elif kind == "fuel":
        DR.rectangle([x, y, x + w, y + h], fill=(30, 30, 30))
        amber = (226, 168, 62)
        bx, by = x + w * 0.74, y + h * 0.30
        bw, bh = w * 0.075, h * 0.52
        DR.rounded_rectangle([bx, by, bx + bw, by + bh], radius=1.5, fill=amber)
        DR.rectangle([bx + bw * 0.16, by + bh * 0.10, bx + bw * 0.62, by + bh * 0.34], fill=(30, 30, 30))
        DR.line([(bx + bw, by + bh * 0.18), (bx + bw + w * 0.035, by + bh * 0.05),
                 (bx + bw + w * 0.035, by + bh * 0.72)], fill=amber, width=max(1, int(1.5 * s)))
        DR.rectangle([bx + bw * 0.20, by + bh, bx + bw * 0.80, by + bh + 1.5], fill=amber)
        L("MALAWI · FUEL", amber)

    elif kind == "protest":
        DR.rectangle([x, y, x + w, y + h], fill=pale)
        base = y + h * 0.92
        for i in range(4):
            cx = x + w * (0.60 + i * 0.09)
            DR.ellipse([cx - h * 0.055, base - h * 0.52, cx + h * 0.055, base - h * 0.41], fill=INK)
            DR.line([(cx, base - h * 0.41), (cx, base - h * 0.10)], fill=INK, width=max(1, int(1.5 * s)))
            DR.line([(cx, base - h * 0.10), (cx - h * 0.07, base)], fill=INK, width=1)
            DR.line([(cx, base - h * 0.10), (cx + h * 0.07, base)], fill=INK, width=1)
        for i, (px, ph) in enumerate(((0.735, 0.46), (0.885, 0.40))):
            cx = x + w * px
            DR.line([(cx, y + h * 0.22), (cx, base - h * 0.20)], fill=(120, 116, 104), width=1)
            DR.rectangle([cx - w * 0.055, y + h * 0.22, cx + w * 0.055, y + h * (0.22 + ph * 0.42)],
                         fill=(255, 253, 246), outline=INK, width=1)
        L("TOKYO · 13,000", INK)

    elif kind == "boat":
        DR.rectangle([x, y, x + w, y + h], fill=(44, 92, 140))
        wy = y + h * 0.74
        for i in range(2):
            DR.line([(x + w * (0.46 + i * 0.02), wy + i * h * 0.12),
                     (x + w * 0.95, wy + i * h * 0.12)], fill=(226, 236, 240), width=1)
        hull = [(x + w * 0.60, y + h * 0.56), (x + w * 0.86, y + h * 0.50),
                (x + w * 0.92, y + h * 0.68), (x + w * 0.58, y + h * 0.72)]
        DR.polygon(hull, fill=(238, 234, 220))
        DR.polygon([(x + w * 0.70, y + h * 0.56), (x + w * 0.70, y + h * 0.36),
                    (x + w * 0.80, y + h * 0.52)], fill=(222, 216, 200))
        L("SENEGAL · BOAT", (255, 255, 255))

    elif kind == "phones":
        DR.rectangle([x, y, x + w, y + h], fill=(52, 58, 66))
        bag = [(x + w * 0.68, y + h * 0.30), (x + w * 0.94, y + h * 0.30),
               (x + w * 0.90, y + h * 0.92), (x + w * 0.72, y + h * 0.92)]
        DR.polygon(bag, outline=(238, 238, 232))
        DR.line([(x + w * 0.70, y + h * 0.42), (x + w * 0.92, y + h * 0.42)], fill=(238, 238, 232), width=1)
        DR.line([(x + w * 0.70, y + h * 0.34), (x + w * 0.92, y + h * 0.34)], fill=(238, 238, 232), width=1)
        px, py = x + w * 0.795, y + h * 0.56
        DR.rounded_rectangle([px - w * 0.022, py - h * 0.14, px + w * 0.022, py + h * 0.16],
                             radius=1.5, fill=(255, 255, 255))
        L("BAG YOUR PHONES", (255, 255, 255))

    else:
        DR.rectangle([x, y, x + w, y + h], fill=pale)
        DR.text((x + 4, y + 2), kind.upper(), font=lf, fill=INK, anchor="la")


# ---------------------------------------------------------------- map data
# 36 rows x 73 columns; row index 0 is the top.  Each row lists land spans.
LAND = {
    1: [(8, 11), (27, 30), (48, 50), (59, 61)],
    2: [(1, 6), (9, 23), (26, 31), (44, 70)],
    3: [(1, 7), (8, 25), (27, 31), (38, 70)],
    4: [(2, 8), (9, 26), (28, 30), (37, 70)],
    5: [(3, 8), (10, 26), (31, 31), (37, 70)],
    6: [(5, 8), (11, 25), (32, 33), (34, 70)],
    7: [(10, 24), (32, 32), (33, 69)],
    8: [(10, 23), (32, 45), (46, 66)],
    9: [(10, 23), (33, 44), (45, 66)],
    10: [(10, 23), (33, 43), (44, 63)],
    11: [(10, 22), (32, 38), (39, 47), (48, 64)],
    12: [(11, 21), (33, 53), (55, 62)],
    13: [(11, 17), (33, 48), (49, 53), (54, 60)],
    14: [(13, 16), (33, 45), (49, 52), (55, 60)],
    15: [(11, 11), (34, 45), (50, 51), (56, 58)],
    16: [(34, 44), (46, 47), (56, 58), (60, 61)],
    17: [(34, 45), (56, 62)],
    18: [(35, 45), (58, 63)],
    19: [(17, 22), (35, 45), (58, 64)],
    20: [(17, 23), (37, 44), (60, 66)],
    21: [(18, 23), (38, 44), (64, 68)],
    22: [(18, 24), (38, 44), (60, 67)],
    23: [(18, 24), (39, 44), (46, 46), (60, 68)],
    24: [(18, 24), (39, 44), (46, 46), (59, 68)],
    25: [(18, 23), (39, 44), (46, 46), (59, 67)],
    26: [(18, 23), (40, 44), (60, 66)],
    27: [(18, 22), (40, 43), (61, 65)],
    28: [(18, 22), (40, 43), (61, 65), (71, 71)],
    29: [(19, 21), (40, 42), (62, 64)],
    30: [(19, 21), (40, 42), (62, 63), (71, 72)],
    31: [(19, 20), (63, 63)],
    32: [(19, 20), (70, 71)],
    33: [(19, 19)],
    34: [(19, 19)],
    35: [(19, 19)],
    36: [(19, 19)],
}
MAP_COLS, MAP_ROWS = 73, 36


def cell_lonlat(row, col):
    return -168 + (col + 0.5) * (360.0 / MAP_COLS), 78 - (row + 0.5) * (134.0 / MAP_ROWS)


def cell_continent(lon, lat):
    if lon < -30:
        return "Americas"
    if lon >= 112 and lat < -11:
        return "Oceania"
    if lon >= 52:
        return "Asia"
    if lat >= 42:
        return "Europe"
    if lon >= 20 and lat >= 12:
        return "Mideast"
    if lat >= 35:
        return "Europe"
    return "Africa"


# ---------------------------------------------------------------- story data
# Featured: (num, kicker, tag, tag colour, chip, headline, summary, art kind)
FEATURED = [
    (1, "KYIV · WAR", "THREE BRIDGES IN ONE NIGHT", DC_RED,
     "CONFIRMED · REUTERS", "Kyiv's bridges hit in one night",
     "Russia's overnight barrage damages three Dnipro crossings · Podilskyi, "
     "Darnytskyi and Southern. Three water workers killed, about 15 injured.",
     "bridges"),
    (2, "GOPALPUR · STORM", "LANDFALL AT DAWN", (44, 92, 140),
     "CONFIRMED · IMD", "Cyclone Akvan comes ashore",
     "Akvan crosses the Odisha coast weakened to 70-80 km/h, below forecast. "
     "300,000+ evacuated; no major damage reported.",
     "cyclone"),
    (3, "ANTALYA · CLIMATE", "FINAL DAY · NO DEAL", ACCENT,
     "CONFIRMED · REUTERS", "COP31's last day, no deal",
     "The revised draft drops every mention of fossil fuels. 92,000 attendees · "
     "the largest COP ever; talks may run into the weekend.",
     "cop31"),
]

# Grid: (num, kicker, headline, summary, banner kind, chip)
GRID = [
    (4, "ASIA · MARKETS", "Asia's AI rout deepens",
     "Nikkei −4.9% and KOSPI −5.5%; Hang Seng nears bear ground. SoftBank plunges 16%.",
     "markets", "CONFIRMED · EXCHANGES"),
    (5, "NEW YORK · TECH", "Anthropic joins the big indexes",
     "A day after its record Nasdaq debut, ANT is added to the MSCI and FTSE indexes.",
     "ipo", "CONFIRMED · WIRES"),
    (6, "WORLDWIDE · GAMES", "GTA VI's $2.36bn first day",
     "Sensor Tower estimates 24.58M copies sold on launch day · a record.",
     "games", "ESTIMATES · SENSOR TOWER"),
    (7, "RIYADH · ENERGY", "Oil edges up on supply fears",
     "Brent +0.3% to $92.22; Saudi defences down four more Houthi missiles.",
     "oil", "CONFIRMED · REUTERS"),
    (8, "EUROPE · DIPLOMACY", "Europe reaches for a seat",
     "Leaders say Europe is ready to join talks with Russia on ending the war.",
     "diplomacy", "CONFIRMED · BBC"),
    (9, "LONDON · DEFENCE", "Britain's £260m drone pledge",
     "More than 1,000 drones for Ukraine in a new £260M package.",
     "drones", "CONFIRMED · WIRES"),
    (10, "SCIENCE · SPACE", "Two hidden companions found",
     "Rubin Observatory preview data reveals two ultra-faint Milky Way satellites.",
     "space", "CONFIRMED · UW"),
    (11, "LONDON · EUROPE", "UK and EU agree youth mobility",
     "London and Brussels are set to agree a youth mobility scheme.",
     "youth", "CONFIRMED · BBC"),
    (12, "MALAWI · CRISIS", "Fuel crisis turns violent",
     "A deepening fuel shortage triggers violence and economic strain.",
     "fuel", "CONFIRMED · WIRES"),
    (13, "TOKYO · PROTEST", "13,000 march in Tokyo",
     "Protesters rally against the Takaichi government's policies.",
     "protest", "CONFIRMED · WIRES"),
    (14, "SENEGAL · MIGRATION", "Boat capsize kills four",
     "A boat capsizes off Senegal as the migration surge continues.",
     "boat", "CONFIRMED · WIRES"),
    (15, "WASHINGTON · PRESS", "Bag your phones",
     "The White House orders journalists to bag their phones after the China trip.",
     "phones", "CONFIRMED · WIRES"),
]

# Briefs
BRIEFS = [
    (16, "Brussels: Coordinated European youth action day – living costs, housing and education; more planned for the weekend"),
    (17, "Genoa: The airport suspends flights after unidentified drones are detected"),
    (18, "France: One dead and 15 injured in a fire at an 18-storey apartment building"),
    (19, "New Caledonia: A 5.6-magnitude earthquake strikes near the islands"),
    (20, "Washington: The US sanctions the Comancheros biker network and an ’Ndrangheta web, its Toronto faction included"),
    (21, "Washington: Trump announces a posthumous pardon for baseball legend Pete Rose"),
    (22, "San Salvador: Bukele formally registers to seek a third presidential term"),
    (23, "Warsaw: Poland prepares a $50bn nuclear-power deal with US firms"),
    (24, "Menlo Park: Meta revises its 2030 climate targets amid its AI infrastructure expansion"),
    (25, "New Delhi: India-Japan 2+2 – Japanese forces will train at Indian ranges; missile and maritime tech agreed"),
    (26, "Amsterdam: 'The Year of the Ghost' wins Best Film at the IDFA documentary festival"),
    (27, "Cincinnati: Fiona the hippo dies at the zoo, days after swallowing a visitor's hat"),
    (28, "Washington: The White House taps Kirsten Davies as national cyber director after widespread outages"),
    (29, "Washington: The Senate nears a vote on a permitting bill to speed power-plant and transmission reviews"),
    (30, "South Pacific: Cyclone Xavier – RSMC Nadi issues bulletin 39; island warning levels unchanged"),
    (31, "Paris: Macron backs Philippe Diallo's bid for the FIFA presidency"),
    (32, "Formula 1: Verstappen backs F1's plan to press ahead with its Middle East races despite the war"),
    (33, "Washington: The US war with Iran has cost over $48bn so far, officials say"),
]

# Pins: story -> (lon, lat, dx, dy)
PINS = {
    1: (30.5, 50.4, 6, -6), 2: (84.9, 19.3, 6, 4), 3: (30.7, 36.9, -8, -6),
    4: (139.7, 35.7, 0, -9), 5: (-74.0, 40.7, -4, -9), 6: (-80.2, 25.8, 0, -6),
    7: (46.7, 24.6, 4, 0), 8: (13.4, 52.5, 8, -6), 9: (-0.1, 51.5, -8, -8),
    10: (-70.7, -30.2, 0, -6), 11: (4.35, 50.85, -12, 6), 12: (33.8, -13.97, 6, 4),
    13: (139.7, 35.7, 13, 7), 14: (-17.4, 14.7, -6, 0), 15: (-77.0, 38.9, -12, -8),
    16: (4.35, 50.85, 10, 10), 17: (8.9, 44.4, 6, 6), 18: (2.35, 48.85, -10, -10),
    19: (165.5, -21.5, 0, -6), 20: (-77.0, 38.9, 13, 8), 21: (-77.0, 38.9, -14, 6),
    22: (-89.2, 13.7, 0, 6), 23: (21.0, 52.2, 10, -4), 24: (-122.2, 37.5, -6, -6),
    25: (77.2, 28.6, -8, -6), 26: (4.9, 52.4, -14, -12), 27: (-84.5, 39.1, 6, 8),
    28: (-77.0, 38.9, 0, -14), 29: (-77.0, 38.9, 14, -6), 30: (178.4, -18.1, 0, -6),
    31: (2.35, 48.85, 12, 8), 32: (54.4, 24.5, 8, 6), 33: (-77.0, 38.9, -6, 12),
}

PIN_CONT = {
    1: "Europe", 2: "Asia", 3: "Mideast", 4: "Asia", 5: "Americas", 6: "Americas",
    7: "Mideast", 8: "Europe", 9: "Europe", 10: "Americas", 11: "Europe",
    12: "Africa", 13: "Asia", 14: "Africa", 15: "Americas", 16: "Europe",
    17: "Europe", 18: "Europe", 19: "Oceania", 20: "Americas", 21: "Americas",
    22: "Americas", 23: "Europe", 24: "Americas", 25: "Asia", 26: "Europe",
    27: "Americas", 28: "Americas", 29: "Americas", 30: "Oceania", 31: "Europe",
    32: "Mideast", 33: "Mideast",
}

REGIONS = [("ASIA 4", CONT["Asia"], 4), ("MIDDLE EAST 4", CONT["Mideast"], 4),
           ("EUROPE 10", CONT["Europe"], 10), ("AFRICA 2", CONT["Africa"], 2),
           ("AMERICAS 10", CONT["Americas"], 10), ("OCEANIA 2", CONT["Oceania"], 2),
           ("GLOBAL 1", MUTED_GREY, 1)]

STATS = [
    ("3", "Kyiv bridges damaged in one night"),
    ("300,000+", "evacuated ahead of Cyclone Akvan"),
    ("−4.9%", "the Nikkei 225 on Friday"),
    ("$2.36bn", "GTA VI estimated first-day sales"),
    ("0", "fossil-fuel mentions in COP31's draft"),
    ("£260m", "Britain's drone package for Ukraine"),
]

DATE_CHECK = (
    "Left out on purpose · they broke on other days: the Houthi strike on "
    "Riyadh's PIF Tower (Thu 19 Nov) · the Tbilisi gas blast, six dead "
    "(Thu 19 Nov) · the ICJ genocide ruling on Myanmar (Thu 19 Nov) · "
    "the Shenzhen three-way summit (Thu 19 Nov) · GTA VI's launch day itself "
    "(Thu 19 Nov) · Nvidia's record quarter (Tue 17 Nov) · the Siberia "
    "An-12 crash, 19 killed (Tue 17 Nov)."
)

FOOTER_A = "CLAIM = one side's account, not independently confirmed."
FOOTER_B = (
    "Every story happened or was first reported on Friday 20 November 2026 · "
    "Disputed claims are attributed · Sources: Reuters · AP · BBC · "
    "IMD · CNBC · Sensor Tower · UN News"
)


# ---------------------------------------------------------------- masthead
def draw_masthead():
    DR.text((24, 3), "THE WORLD'S NEWS IN ONE PICTURE",
            font=F(SANS_B, 12.5), fill=ACCENT, anchor="la")
    DR.text((1000, 3), "33 STORIES · ONE PAGE",
            font=F(SANS_B, 12.5), fill=INK, anchor="ra")

    size = 54
    while size > 40:
        f = F(SERIF_B, size)
        if DR.textlength("THE DAILY ATLAS", font=f) <= 900:
            break
        size -= 2
    title_size = size
    DR.text((512, 13), "THE DAILY ATLAS", font=F(SERIF_B, title_size),
            fill=INK, anchor="ma")

    r1 = 13 + title_size + 6
    DR.rectangle([24, r1, 1000, r1 + 2], fill=ACCENT)
    DR.rectangle([24, r1 + 5, 1000, r1 + 5], fill=ACCENT)

    dy = r1 + 9
    DR.text((512, dy), "Friday 20 November 2026",
            font=F(SERIF_B, 21), fill=ACCENT, anchor="ma")

    sy = dy + 27
    DR.text((24, sy), "EVERY STORY REPORTED ON THE DAY",
            font=F(SANS, 10.5), fill=GREY, anchor="la")
    DR.text((1000, sy), "FRIDAY EDITION · NO. 20",
            font=F(SANS_B, 11), fill=INK, anchor="ra")
    return sy


# ---------------------------------------------------------------- region bar
def draw_region_bar(rb_y):
    x0, x1, hgt = 24, 1000, 21
    total = x1 - x0
    counts = [r[2] for r in REGIONS]
    csum = float(sum(counts))
    widths = [total * c / csum for c in counts]
    # Each segment must be at least 52px AND wide enough for its white label.
    # Any shortfall is taken proportionally from the segments above their minimum.
    mins = [max(52.0, DR.textlength(r[0], font=F(SANS_B, 10)) + 8.0) for r in REGIONS]
    for _ in range(40):
        short = [i for i, wd in enumerate(widths) if wd < mins[i] - 1e-9]
        if not short:
            break
        deficit = sum(mins[i] - widths[i] for i in short)
        donors = [i for i, wd in enumerate(widths) if wd > mins[i] + 1e-9]
        pool = sum(widths[i] - mins[i] for i in donors)
        if pool <= 1e-9:
            break
        for i in short:
            widths[i] = mins[i]
        for i in donors:
            widths[i] -= deficit * (widths[i] - mins[i]) / pool
    assert sum(widths) <= total + 0.01, sum(widths)
    for (label, _col, _n), wd in zip(REGIONS, widths):
        assert DR.textlength(label, font=F(SANS_B, 10)) <= wd - 4, \
            "region label %r too wide for %.1fpx segment" % (label, wd)
    cx = x0
    for (label, col, _n), wd in zip(REGIONS, widths):
        DR.rectangle([cx, rb_y, cx + wd - 0.5, rb_y + hgt], fill=col)
        DR.text((cx + wd / 2.0, rb_y + hgt / 2.0), label,
                font=F(SANS_B, 10), fill=(255, 255, 255), anchor="mm")
        REGIONS_DRAWN.append(label)
        cx += wd


# ---------------------------------------------------------------- stat strip
def draw_stat_strip(st_y):
    hgt = 42
    DR.rectangle([24, st_y, 1000, st_y + hgt], fill=CARD, outline=BORDER, width=1)
    cellw = (1000 - 24) / 6.0
    for i, (val, cap) in enumerate(STATS):
        cx0 = 24 + i * cellw
        if i:
            DR.rectangle([cx0, st_y, cx0, st_y + hgt], fill=BORDER)
        ccx = cx0 + cellw / 2.0
        DR.text((ccx, st_y + 3), val, font=F(SERIF_B, 19), fill=ACCENT, anchor="ma")
        f = F(SANS, 8)
        lines = wrap(cap, f, cellw - 10)
        ly = st_y + 27
        for ln in lines:
            if ly + 9 > st_y + hgt + 0.01:
                fail("STAT caption overflows cell %d: %r" % (i, ln))
            DR.text((ccx, ly), ln, font=f, fill=INK, anchor="ma")
            ly += 9.5
        if ly - 9.5 + 8 > st_y + hgt + 0.01:
            fail("STAT caption bottom beyond strip in cell %d" % i)
        STAT_CELLS.append(val)


# ---------------------------------------------------------------- featured
CARD_W, CARD_H = 317, 162
FEAT_TOP = 74


def load_art(kind, w=317, h=74):
    path = os.path.join(ASSETS, kind + ".jpg")
    if not os.path.exists(path):
        fail("missing artwork %s" % path)
        return Image.new("RGB", (w, h), (210, 206, 194))
    im = Image.open(path).convert("RGB")
    im = ImageOps.fit(im, (w, h), method=Image.LANCZOS, centering=(0.5, 0.42))
    ART_USED.add(kind)
    return im


def source_chip(x_right, top, bottom, text, size, pad, fill):
    """Rounded pill spanning exactly [top, bottom], right edge at x_right."""
    f = F(SANS_B, size)
    pw = DR.textlength(text, font=f) + pad
    DR.rounded_rectangle([x_right - pw, top, x_right, bottom], radius=7, fill=fill)
    DR.text((x_right - pw / 2.0, (top + bottom) / 2.0), text, font=f,
            fill=(255, 255, 255), anchor="mm")
    CHIPS_DRAWN.append(text)
    return pw


def draw_featured(fy):
    for i, (num, kick, tag, tagcol, chip_txt, head, summ, art) in enumerate(FEATURED):
        x = 24 + i * 329
        y = fy
        DR.rectangle([x, y, x + CARD_W, y + CARD_H], fill=CARD)

        IMG.paste(load_art(art, CARD_W, FEAT_TOP), (x, y))

        # tag bar over the lower part of the artwork
        DR.rectangle([x, y + 48, x + CARD_W, y + FEAT_TOP], fill=tagcol)
        strip = INK if tagcol == ACCENT else ACCENT
        DR.rectangle([x, y + 48, x + 5, y + FEAT_TOP], fill=strip)
        DR.text((x + 14, y + 61), tag, font=F(SANS_B, 12), fill=(255, 255, 255), anchor="lm")

        chip(x + 18, y + 86, 9.5, num, ACCENT)
        DR.text((x + 34, y + 86), kick, font=F(SANS_B, 10.5), fill=ACCENT, anchor="lm")
        source_chip(x + 309, y + 78, y + 94, chip_txt, 8, 14, PILL)

        end = block(x + 10, y + 96, 297, head, F(SERIF_B, 17), 18, y + 133)
        block(x + 10, end + 1, 297, summ, F(SERIF, 9.5), 11.5, y + 160)

        # border last so the artwork paste cannot erase the card edge
        DR.rectangle([x, y, x + CARD_W, y + CARD_H], outline=BORDER, width=1)

# ---------------------------------------------------------------- grid
GW, GH = 238, 84


def draw_grid(gy):
    DR.rectangle([24, gy - 8, 1000, gy - 8], fill=INK)
    for i, (num, kick, head, summ, kind, chip_txt) in enumerate(GRID):
        col, row = i % 4, i // 4
        x = 24 + col * 246
        y0 = gy + row * 92
        DR.rectangle([x, y0, x + GW, y0 + GH], fill=CARD, outline=BORDER, width=1)
        banner(x + 1, y0 + 1, GW - 2, 34, kind)
        chip(x + 13, y0 + 41, 6, num, ACCENT)
        kick_f = F(SANS_B, 8)
        DR.text((x + 24, y0 + 41), kick, font=kick_f, fill=ACCENT, anchor="lm")
        is_claim = chip_txt.startswith("CLAIM")
        # Source chip right-anchored at x+230; step the size down only as far as
        # needed so it clears the kicker (largest size that fits wins).
        kend = x + 24 + DR.textlength(kick, font=kick_f)
        for cs in (7.0, 6.75, 6.5, 6.25, 6.0):
            cf = F(SANS_B, cs)
            cw = DR.textlength(chip_txt, font=cf)
            if x + 230 - cw >= kend + 4:
                break
        assert x + 230 - cw >= kend + 2, "grid chip %r collides with kicker" % chip_txt
        DR.text((x + 230, y0 + 41), chip_txt, font=cf,
                fill=DC_RED if is_claim else GREY, anchor="rm")
        CHIPS_DRAWN.append(chip_txt)
        end = block(x + 8, y0 + 47, 222, head, F(SERIF_B, 12), 12.5, y0 + 72)
        block(x + 8, end, 222, summ, F(SERIF, 8.5), 9.5, y0 + 83)


# ---------------------------------------------------------------- map
def draw_map(map_x, map_y, map_w, map_h):
    DR.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=MAP_BG, outline=BORDER, width=1)
    cw = map_w / float(MAP_COLS)
    ch = map_h / float(MAP_ROWS)
    for row, spans in LAND.items():
        for a, b in spans:
            for col in range(a, b + 1):
                lon, lat = cell_lonlat(row, col)
                cont = cell_continent(lon, lat)
                cx = map_x + col * cw
                cy = map_y + row * ch
                DR.rectangle([cx, cy, cx + cw + 0.6, cy + ch + 0.6],
                             fill=mute(CONT[cont]))
    for num in sorted(PINS):
        lon, lat, dx, dy = PINS[num]
        px = map_x + (lon + 168) / 360.0 * map_w + dx
        py = map_y + (78 - lat) / 134.0 * map_h + dy
        chip(px, py, 7, num, CONT[PIN_CONT[num]])


# ---------------------------------------------------------------- briefs
BRIEF_X = [24, 196, 368, 540]
BRIEF_W = 150


def brief_heights(size):
    f = F(SANS, size)
    out = []
    for _n, txt in BRIEFS:
        lines = wrap(txt, f, BRIEF_W)
        out.append(len(lines) * (size + 2))
    return out


def choose_briefs(avail):
    """Largest font size whose tallest column fits; then the most balanced breaks."""
    for size in (9.5, 9.25, 9.0, 8.75, 8.5, 8.25, 8.0):
        hs = brief_heights(size)
        n = len(hs)
        best = None
        for a in range(3, 8):
            for b in range(a + 3, min(n, a + 8)):
                for c in range(b + 3, min(n, b + 8)):
                    d = n - c
                    if not (3 <= d <= 7):
                        continue
                    groups = [(0, a), (a, b), (b, c), (c, n)]
                    colh = [sum(hs[s:e]) + 2 * (e - s) for s, e in groups]
                    tallest = max(colh)
                    if tallest <= avail:
                        key = (tallest - min(colh), tallest)
                        if best is None or key < best[0]:
                            best = (key, tallest, groups, colh)
        if best is not None:
            return best[1], size, best[2], best[3]
    return None


def draw_briefs(band_x, top_y, avail):
    pick = choose_briefs(avail)
    if pick is None:
        fail("no brief layout fits above y=930")
        return 0
    tallest, size, groups, colh = pick
    counts = [e - s for s, e in groups]
    pad = max(0.0, (215 - tallest)) / float(max(counts))
    lh = size + 2
    f = F(SANS, size)

    for ci, (s, e) in enumerate(groups):
        x = BRIEF_X[ci]
        y = top_y
        for bi in range(s, e):
            num, txt = BRIEFS[bi]
            chip(x + 7, y + 6, 6.5, num, ACCENT)
            lines = wrap(txt, f, BRIEF_W)
            ly = y
            for ln in lines:
                DR.text((x + 18, ly), ln, font=f, fill=INK, anchor="la")
                ly += lh
            y += len(lines) * lh + 2 + pad
            if bi != e - 1:
                dy = y - pad - 1.5
                dx = x + 2
                while dx < x + BRIEF_W + 12:
                    DR.rectangle([dx, dy, dx + 1.5, dy + 1], fill=BORDER)
                    dx += 5
    band_h = tallest + pad * max(counts)
    return band_h


# ---------------------------------------------------------------- lower page
def draw_lower(fy):
    gy = fy + CARD_H + 16
    draw_grid(gy)

    by = gy + 3 * GH + 2 * 8 + 12
    DR.rectangle([24, by, 1000, by], fill=INK)
    hy = by + 8

    DR.text((700, hy), "WHERE IT HAPPENED", font=F(SANS_B, 12), fill=ACCENT, anchor="la")
    DR.text((24, hy), "ALSO ON FRIDAY 20 NOVEMBER", font=F(SANS_B, 12), fill=INK, anchor="la")

    # legend centred on x=512
    fl = F(SANS, 8.5)
    items = [(nm, DR.textlength(nm, font=fl) + 7 + 4) for nm in CONT_ORDER]
    total = sum(wd for _n, wd in items) + 10 * (len(items) - 1)
    lx = 512 - total / 2.0
    for nm, wd in items:
        DR.ellipse([lx, hy + 5, lx + 7, hy + 12], fill=CONT[nm])
        DR.text((lx + 11, hy + 11), nm, font=fl, fill=INK, anchor="lm")
        lx += wd + 10

    my = hy + 22
    map_x, map_w = 700, 300
    avail = 930 - my
    band_h = draw_briefs(24, my, avail)
    draw_map(map_x, my, map_w, band_h)

    dc_y = my + band_h + 8
    DR.rectangle([24, dc_y, 1000, dc_y + 36], fill=CARD, outline=DC_RED, width=2)
    DR.rectangle([24, dc_y, 86, dc_y + 36], fill=DC_RED)
    DR.text((55, dc_y + 6), "DATE", font=F(SANS_B, 10.5), fill=(255, 255, 255), anchor="ma")
    DR.text((55, dc_y + 19), "CHECK", font=F(SANS_B, 10.5), fill=(255, 255, 255), anchor="ma")
    fdc = F(SANS, 9)
    dlines = wrap(DATE_CHECK, fdc, 896)
    if len(dlines) > 2:
        fail("DATE CHECK needs %d lines (max 2)" % len(dlines))
    for i, ln in enumerate(dlines[:2]):
        DR.text((96, dc_y + 5 + i * 12), ln, font=fdc, fill=INK, anchor="la")

    fy2 = dc_y + 42
    DR.rectangle([24, fy2, 1000, fy2], fill=INK)
    DR.text((512, fy2 + 5), FOOTER_A, font=F(SERIF_I, 9.5), fill=INK, anchor="ma")
    DR.text((512, fy2 + 21), FOOTER_B, font=F(SANS, 8.5), fill=GREY, anchor="ma")
    return dc_y + 42, len(dlines)


# ---------------------------------------------------------------- build
def main():
    sy = draw_masthead()
    rb_y = sy + 15
    draw_region_bar(rb_y)
    st_y = rb_y + 27
    draw_stat_strip(st_y)
    fy = st_y + 50
    draw_featured(fy)
    last, dlines_count = draw_lower(fy)

    IMG.save(OUT, "PNG", optimize=True)

    # ---- assertions
    assert not CLIPS, "CLIP failures: %s" % CLIPS[:3]
    assert NUM_DRAWN == set(range(1, 34)), "missing numbers: %s" % (set(range(1, 34)) - NUM_DRAWN)
    assert ART_USED == {"bridges", "cyclone", "cop31"}, ART_USED
    assert len(REGIONS_DRAWN) == 7, REGIONS_DRAWN
    assert len(STAT_CELLS) == 6, STAT_CELLS
    assert len(CHIPS_DRAWN) == 15, len(CHIPS_DRAWN)
    assert last <= 1020, "footer overruns canvas: %s" % last

    sz = os.path.getsize(OUT)
    with open(OUT, "rb") as fh:
        magic = fh.read(8)
    assert magic[:4] == b"\x89PNG", magic
    assert IMG.size == (1024, 1024)
    assert sz <= 1048576, sz
    print("entry.png %dx%d %d bytes" % (IMG.size[0], IMG.size[1], sz))
    print("SUMMARY: no CLIP failures; all %d story numbers drawn; featured art %s loaded; %d region segments drawn; %d stat cells drawn; DATE CHECK lines: %d; %d card source chips drawn." % (
        len(NUM_DRAWN), sorted(ART_USED), len(REGIONS_DRAWN), len(STAT_CELLS), dlines_count, len(CHIPS_DRAWN)))


if __name__ == "__main__":
    main()
