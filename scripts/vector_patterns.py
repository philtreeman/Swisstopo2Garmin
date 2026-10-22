"""32x32-Muster der Flaechen (gemeinsam fuer make_vector_typ.py und compare_vector.py). 'b' = Hintergrund, 'f' = Vordergrund."""
import random
from vector_palette import *  # noqa: F401,F403


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
    "0x4e": ("Reben, Obst", REBEN_BG, REBEN, grid(kind="bolts")),
    "0x51": ("Feuchtgebiet", BG, FEUCHT, grid(0.22, 3, 3)),
    "0x52": ("Fels", FELS, FELS_TEXTUR, grid(0.34, 5, 7, kind="meander")),
    "0x53": ("Geroell", BG, WEG_FEST, grid(0.14, 1, 5)),
}
