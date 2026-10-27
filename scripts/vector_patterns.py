"""32x32-Muster der Flaechen (gemeinsam fuer make_vector_typ.py und compare_vector.py). 'b' = Hintergrund, 'f' = Vordergrund."""
import random
from vector_palette import *  # noqa: F401,F403
import vector_pattern_tiles as T


def grid(density=0.0, run=1, seed=0, kind="strokes"):
    rnd = random.Random(seed)
    g = [["b"] * 32 for _ in range(32)]
    if kind == "grid":
        for y in range(32):
            for x in range(32):
                if (x + y) % 6 == 0 or (x - y) % 6 == 0:
                    g[y][x] = "f"
    elif kind == "bolts":                       # Reben: kleine Blitzstriche im Raster, jede zweite Reihe versetzt (wie Garmin)
        for r, y in enumerate(range(1, 32, 11)):
            for x in range(2 + (5 if r % 2 else 0), 32, 11):
                for dx, dy in ((2, 0), (1, 1), (2, 1), (0, 2), (1, 2), (0, 3), (1, 3), (0, 4)):
                    g[(y + dy) % 32][(x + dx) % 32] = "f"
    elif kind == "dots":                        # Obstanlage: verstreute 1- und 2-Pixel-Punkte, ca. 32 je 32 x 32 Pixel (an der Garmin-Karte gezaehlt:
        n = 6                                   # 3 % der Flaeche orange); 6 x 6 Zellen mit Zufallsversatz, etwa jede fuenfte Zelle bleibt leer
        for cy in range(n):
            for cx in range(n):
                if rnd.random() < 0.2:
                    continue
                x, y = int((cx + 0.1 + 0.8 * rnd.random()) * 32 / n), int((cy + 0.1 + 0.8 * rnd.random()) * 32 / n)
                size = 2 if rnd.random() < 0.4 else 1
                for dy in range(size):
                    for dx in range(size):
                        g[(y + dy) % 32][(x + dx) % 32] = "f"
    elif kind == "meander":                     # Fels: kurze, leicht gewellte Striche mit Luecke dazwischen (wie Garmin)
        todo, tries = int(32 * 32 * density / run), 0
        while todo > 0 and tries < 4000:
            tries += 1
            y0, x0 = rnd.randrange(32), rnd.randrange(32)
            pts, y = [], y0
            for k in range(run + rnd.randrange(3)):
                pts.append((y % 32, (x0 + k) % 32))
                if rnd.random() < 0.25:
                    y += rnd.choice((-1, 1))
            if any(g[(py + dy) % 32][(px + dx) % 32] == "f" for py, px in pts for dy in (-1, 0, 1) for dx in (-1, 0, 1)):
                continue
            for py, px in pts:
                g[py][px] = "f"
            todo -= 1
    else:
        for _ in range(int(32 * 32 * density / run)):
            y, x = rnd.randrange(32), rnd.randrange(32)
            for k in range(run):
                g[y][(x + k) % 32] = "f"
    return ["".join(r) for r in g]


# Typ -> (Name, Hintergrund, Vordergrund, Muster)
PATTERNS = {
    "0x4f": ("Gehoelz", BG, GEHOELZ, grid(0.30, 2, 1)),
    "0x4e": ("Reben, Obst", REBEN_BG, REBEN, T.REBEN),
    "0x10e08": ("Obstanlage", REBEN_BG, REBEN, grid(kind="dots", seed=11)),
    "0x10e09": ("Baumschule", REBEN_BG, "#5AA000", grid(kind="dots", seed=12)),
    "0x51": ("Feuchtgebiet", BG, FEUCHT, grid(0.22, 3, 3)),
    "0x52": ("Fels", FELS, FELS_TEXTUR, T.FELS),
    "0x53": ("Geroell", BG, WEG_FEST, grid(0.14, 1, 5)),
}
