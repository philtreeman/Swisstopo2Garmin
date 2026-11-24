"""32x32-Muster der Flaechen nach der swisstopo-Zeichenerklaerung (gemeinsam fuer make_vector_typ.py und die Vorschau).
'b' = Hintergrund, 'f' = Vordergrund. Alle Muster sind regelmaessig oder mit festem Zufallsstartwert erzeugt (reproduzierbar)."""
import random
from vector_palette import *  # noqa: F401,F403


def _leer(): return [["b"] * 32 for _ in range(32)]


def _out(g): return ["".join(r) for r in g]


def punkte(n, gross=1, seed=0, abstand=2):
    """n Punkte (gross x gross Pixel) zufaellig, mit Mindestabstand (rund um das Muster herum, damit die Kachel nahtlos ist)"""
    rnd = random.Random(seed); g = _leer(); pts = []
    tries = 0
    while len(pts) < n and tries < 20000:
        tries += 1
        x, y = rnd.randrange(32), rnd.randrange(32)
        if any(min(abs(x - px), 32 - abs(x - px)) < gross + abstand - 1 and min(abs(y - py), 32 - abs(y - py)) < gross + abstand - 1 for px, py in pts):
            continue
        pts.append((x, y))
        for dy in range(gross):
            for dx in range(gross):
                g[(y + dy) % 32][(x + dx) % 32] = "f"
    return _out(g)


def raster_punkte(teilung, gross=1, versatz=0):
    """regelmaessiges Punktraster (Teilung in Pixel); jede zweite Reihe um 'versatz' Pixel verschoben (Obstanlage ohne, Baumschule mit)"""
    g = _leer()
    for r, y in enumerate(range(0, 32, teilung)):
        for x in range(versatz * (r % 2), 32, teilung):
            for dy in range(gross):
                for dx in range(gross):
                    g[(y + dy) % 32][(x + dx) % 32] = "f"
    return _out(g)


def reben():
    """Reben: kurze senkrechte Striche (4 px lang, Lücke 4 px), Spalten alle 4 px, jede zweite Spalte um 4 px versetzt"""
    g = _leer()
    for c, x in enumerate(range(1, 32, 4)):
        for y in range(32):
            if (y + 4 * (c % 2)) % 8 < 4:
                g[y][x] = "f"
    return _out(g)


def feucht():
    """Feuchtgebiet: kurze waagrechte Striche (3 px), Teilung 8 px, Reihen alle 4 px, Reihen versetzt"""
    g = _leer()
    for r, y in enumerate(range(0, 32, 4)):
        for x0 in range(0, 32, 8):
            for dx in range(3):
                g[y][(x0 + (r * 3) % 8 + dx) % 32] = "f"
    return _out(g)


def kreuze(teilung=8):
    """Friedhof: schwarze Kreuze (+, 3 x 3), Reihen versetzt"""
    g = _leer()
    for r, y in enumerate(range(1, 32, teilung)):
        for x in range(1 + (teilung // 2) * (r % 2), 32, teilung):
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                g[(y + dy) % 32][(x + dx) % 32] = "f"
    return _out(g)


def striche(dichte, laenge=3, seed=0):
    """Fels: kurze, leicht schraege schwarze Striche (Schraffur) mit Luecken; dichte = Anteil der Pixel"""
    rnd = random.Random(seed); g = _leer(); n = 0; ziel = int(1024 * dichte); tries = 0
    while n < ziel and tries < 20000:
        tries += 1
        x, y = rnd.randrange(32), rnd.randrange(32)
        d = rnd.choice((-1, 0, 1, 1))     # Neigung
        pts = [((x + k) % 32, (y + (k * d) // 2) % 32) for k in range(laenge + rnd.randrange(2))]
        if any(g[(py + dy) % 32][(px + dx) % 32] == "f" for px, py in pts for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
            continue
        for px, py in pts:
            g[py][px] = "f"
        n += len(pts)
    return _out(g)


def gletscher(dichte=0.07, seed=11):
    """Gletscher: spaerliche, kurze blaue Striche (Spalten, Eisstruktur) auf weiss, leicht gekruemmt und schraeg, unregelmaessig;
    dichte = Anteil der Pixel (LK25: blaue Strukturlinien auf weissem Grund)"""
    rnd = random.Random(seed); g = _leer(); n = 0; ziel = int(1024 * dichte); tries = 0
    while n < ziel and tries < 20000:
        tries += 1
        x, y = float(rnd.randrange(32)), float(rnd.randrange(32))
        L = rnd.randrange(5, 10)
        a = rnd.choice((-1, 1)) * rnd.uniform(0.25, 0.9)       # Schraege (Steigung dy/dx)
        kr = rnd.uniform(-0.08, 0.08)                          # Kruemmung
        pts = []
        for k in range(L):
            pts.append((int(round(x + k)) % 32, int(round(y + a * k + kr * k * k)) % 32))
        pts = list(dict.fromkeys(pts))
        if any(g[(py + dy) % 32][(px + dx) % 32] == "f" for px, py in pts for dy in (-2, -1, 0, 1, 2) for dx in (-2, -1, 0, 1, 2)):
            continue
        for px, py in pts:
            g[py][px] = "f"
        n += len(pts)
    return _out(g)


# Typ -> (Name, Hintergrund, Vordergrund, Muster)
PATTERNS = {
    "0x10e01": ("Wald offen", BG, GRUEN, punkte(20, 2, 1, 2)),          # 2 x 2 Punkte, ca. 8 % der Flaeche
    "0x10e02": ("Gebueschwald", BG, GRUEN, punkte(123, 1, 2, 1)),        # 1 x 1 Punkte, dichter, ca. 12 %
    "0x4f": ("Gehoelz, Hecke", BG, GRUEN, punkte(80, 1, 3, 1)),           # ca. 8 %
    "0x4e": ("Reben", WEISS, GRUEN, reben()),
    "0x10e08": ("Obstanlage", WEISS, GRUEN, raster_punkte(4, 1, 0)),     # 4 px Raster, 1 px Punkt
    "0x10e09": ("Baumschule", WEISS, GRUEN, raster_punkte(3, 1, 1)),     # dichter, Reihen versetzt (3 px)
    "0x51": ("Feuchtgebiet", BG, WASSER, feucht()),
    "0x1a": ("Friedhof", PARK, SCHWARZ, kreuze()),
    "0x10e04": ("Schrebergarten", PARK, SCHWARZ, raster_punkte(8, 2, 4)),
    "0x52": ("Fels", BG, SCHWARZ, striche(0.12, 3, 5)),                   # schwarze Striche, ca. 12 %
    "0x10e00": ("Gletscher, Schneefeld", WEISS, GLETSCHER_STRICH, gletscher()),
    "0x53": ("Geroell", BG, SCHWARZ, punkte(61, 1, 6, 2)),                # schwarze Punkte, Dichte 0.06
    "0x10e0a": ("Offenes Gebaeude, Treibhaus, Flugdach", WEISS, SCHWARZ,
                ["".join("f" if (x + y) % 4 == 0 else "b" for x in range(32)) for y in range(32)]),   # schwarze Schraffur auf weiss
}
