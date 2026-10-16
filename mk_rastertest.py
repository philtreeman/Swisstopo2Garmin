#!/usr/bin/env python3
"""Ganze Schweiz: JPEGs in TopoCHProV5raster.img durch swisstopo ersetzen.

Die JPEGs bleiben in den originalen Längenslots (nach dem EOI mit Nullen
aufgefüllt). shortcut: Slots, die zu klein für ein neues Bild sind, behalten
das alte JPEG. Grössere Bilder bräuchten einen neu geschriebenen Index.
"""
import io, math, os, struct, time, urllib.error, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

SRC = "TopoCHProV5raster.img"
DST = "out/TopoCH-swisstopo.img"
CACHE = "out/wmts"
BLOCK = 65536
LAYER = "ch.swisstopo.pixelkarte-farbe-pk25.noscale"
URL = "https://wmts.geo.admin.ch/1.0.0/{layer}/default/current/3857/{z}/{x}/{y}.jpeg"
OLD_NAME = b"TOPO Switzerland PRO Raster"
NEW_NAME = b"SWISSTOPO".ljust(len(OLD_NAME))
# Familie 0x1151 ist das gekaufte Produkt und hängt an den SQL-Dateien.
# 21332 gehört zu keinem Garmin-Produkt, die Karte bleibt eine einzelne IMG.
OLD_ID = b"\x01\x00\x51\x11"
NEW_ID = b"\x01\x00\x54\x53"
_TILES = {}


def deg32(v):
    if v >= 0x80000000:
        v -= 1 << 32
    return v * 360 / 2**32


def deg24(v):
    return ((v & 0xFFFFFF) << 8) * 360 / 2**32


def ll_tile(lon, lat, z):
    n = 2**z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def zoom_for(west, south, east, north, pw, ph):
    """Gröbster WMTS-Zoom, der höchstens doppelt so fein ist wie das Zielbild. Deckel 16."""
    lat = (north + south) / 2
    mpp = min((east - west) * 111320 * math.cos(math.radians(lat)) / max(pw, 1),
              (north - south) * 110540 / max(ph, 1))
    mpp = max(mpp, 0.4)
    for z in range(16, 7, -1):
        src = 156543.03 * math.cos(math.radians(lat)) / 2**z
        if src >= mpp / 2:
            return z
    return 8


def tile_path(z, x, y):
    return os.path.join(CACHE, str(z), str(x), f"{y}.jpg")


def ensure_tiles(coords):
    missing = [c for c in coords if not os.path.exists(tile_path(*c))]

    def one(c):
        z, x, y = c
        path = tile_path(z, x, y)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        url = URL.format(layer=LAYER, z=z, x=x, y=y)
        err = None
        for i in range(4):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    data = r.read()
                if data[:2] != b"\xff\xd8":
                    break
                with open(path, "wb") as f:
                    f.write(data)
                return
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    Image.new("RGB", (256, 256), (236, 233, 216)).save(path, "JPEG", quality=40)
                    return
                err = e
                time.sleep(1 + i)
            except Exception as e:
                err = e
                time.sleep(1 + i)
        raise RuntimeError(f"WMTS {z}/{x}/{y}: {err}")

    if missing:
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(one, missing))


def wmts(z, x, y):
    key = (z, x, y)
    img = _TILES.get(key)
    if img is None:
        if len(_TILES) > 500:
            _TILES.clear()
        img = Image.open(tile_path(z, x, y)).convert("RGB")
        _TILES[key] = img
    return img


def render(box, size):
    west, south, east, north = box
    z = zoom_for(west, south, east, north, size[0], size[1])
    x0f, y0f = ll_tile(west, north, z)
    x1f, y1f = ll_tile(east, south, z)
    xs = range(math.floor(x0f), math.floor(x1f) + 1)
    ys = range(math.floor(y0f), math.floor(y1f) + 1)
    if len(xs) > 24 or len(ys) > 24:
        raise RuntimeError(f"Ausschnitt zu gross: {len(xs)}x{len(ys)} Kacheln bei Zoom {z}")
    canvas = Image.new("RGB", (256 * len(xs), 256 * len(ys)))
    x0, y0 = xs[0], ys[0]
    for x in xs:
        for y in ys:
            canvas.paste(wmts(z, x, y), ((x - x0) * 256, (y - y0) * 256))
    crop = canvas.crop((
        round((x0f - x0) * 256), round((y0f - y0) * 256),
        round((x1f - x0) * 256), round((y1f - y0) * 256),
    ))
    return crop.resize(size, Image.Resampling.LANCZOS), z


def jpeg_wh(blob):
    k = blob.find(b"\xff\xc0")
    if k < 0 or k + 9 > len(blob):
        return 512, 512
    h = int.from_bytes(blob[k + 5:k + 7], "big")
    w = int.from_bytes(blob[k + 7:k + 9], "big")
    return w, h


def encode_jpeg(img, q):
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=q, optimize=True)
    data = buf.getvalue()
    # APP0 (JFIF) ist für den Decoder unnötig und spart bei sehr kleinen Slots Bytes.
    if data[2:4] == b"\xff\xe0":
        n = int.from_bytes(data[4:6], "big")
        data = data[:2] + data[4 + n:]
    return data


def fit_jpeg(img, limit):
    trials = [img]
    if min(img.size) >= 32:
        small = img.resize((max(8, img.width // 4), max(8, img.height // 4)), Image.Resampling.BOX)
        trials.append(small.resize(img.size, Image.Resampling.NEAREST))
    trials.append(Image.new("RGB", img.size, (236, 233, 216)))
    for trial in trials:
        for q in (70, 45, 25, 12, 5, 1):
            data = encode_jpeg(trial, q)
            if len(data) <= limit:
                return data
    return None


def jpeg_end(buf, off):
    i = off + 2
    while i < len(buf) - 1:
        if buf[i] != 0xFF:
            return None
        while buf[i] == 0xFF:
            i += 1
        m = buf[i]
        i += 1
        if m == 0xDA:
            while i < len(buf) - 1:
                if buf[i] == 0xFF:
                    nxt = buf[i + 1]
                    if nxt == 0x00:
                        i += 2
                        continue
                    if nxt == 0xD9:
                        return i + 2
                    if 0xD0 <= nxt <= 0xD7:
                        i += 2
                        continue
                    return None
                i += 1
            return None
        if m in (0xD8, 0xD9, 0x01) or 0xD0 <= m <= 0xD7:
            continue
        i += int.from_bytes(buf[i:i + 2], "big")
    return None


def u32(buf, off):
    return struct.unpack_from("<I", buf, off)[0]


def box_at(gmp, pos, stride):
    o = pos + stride - 16
    n, e, s_, w = (deg32(u32(gmp, o + 4 * i)) for i in range(4))
    if 45 < s_ < n < 49 and 5 < w < e < 11 and (n - s_) < 1.5 and (e - w) < 1.5:
        return w, s_, e, n
    return None


def jpeg_slots(gmp):
    sois, lens, s = [], [], 0
    while True:
        i = gmp.find(b"\xff\xd8\xff", s)
        if i < 0:
            break
        end = jpeg_end(gmp, i)
        if not end or end <= i:
            s = i + 3
            continue
        sois.append(i)
        lens.append(end - i)
        s = end
    assert sois and all(n > 100 for n in lens)
    return sois, lens


def tre_box(gmp):
    b = gmp[0xF0:0xF0 + 0x21]
    n = deg24(int.from_bytes(b[0x15:0x18], "little"))
    e = deg24(int.from_bytes(b[0x18:0x1B], "little"))
    s_ = deg24(int.from_bytes(b[0x1B:0x1E], "little"))
    w = deg24(int.from_bytes(b[0x1E:0x21], "little"))
    return w, s_, e, n


def index_boxes(gmp, lens):
    """Erste Indexkopie. Eintrag meist 35–40 Bytes.

    Die Ecken stehen in den 16 Bytes unmittelbar vor der JPEG-Länge.
    Die 16 Bytes am Ende des Eintrags sind die Nachbarspalte im Osten
    (in Baden rund 970 m). Ein Übersichtseintrag ohne lesbare Ecken
    bekommt die Umrandung der ganzen Kachel.
    """
    from collections import Counter, defaultdict
    want = set(lens)
    limit = gmp.find(b"\xff\xd8\xff")
    if limit < 0:
        limit = len(gmp)
    good, odd = set(), set()
    for pos in range(0, max(0, limit - 40)):
        if u32(gmp, pos) not in want:
            continue
        tag = gmp[pos + 4:pos + 6]
        if tag == b"\x06\xb3":
            good.add(pos)
        elif tag == b"\x0d\x01":
            odd.add(pos)
    if not good:
        raise AssertionError("kein Index")

    def advance(pos):
        if pos in odd:
            for st in range(35, 64):
                if pos + st in good:
                    return pos + st
            return None
        cands = [pos + d for d in range(35, 41) if pos + d in good or pos + d in odd]
        if len(cands) > 1:
            cands.sort(key=lambda c: sum(
                1 for d in range(35, 41) if c + d in good or c + d in odd), reverse=True)
        return cands[0] if cands else None

    def walk(head):
        seq, pos = [head], head
        while len(seq) < len(lens):
            nxt = advance(pos)
            if nxt is None:
                break
            seq.append(nxt)
            pos = nxt
        return seq

    heads = [p for p in sorted(good)
             if not any(p - d in good or p - d in odd for d in range(35, 41))]
    seq = None
    for head in heads:
        trial = walk(head)
        if Counter(u32(gmp, p) for p in trial) == Counter(lens):
            seq = trial
            break
    if seq is None:
        raise AssertionError("Index und JPEG-Längen passen nicht")
    fallback = tre_box(gmp)
    recs = []
    for pos in seq:
        # box_at(pos-36, 36) liest genau die 16 Bytes vor der Länge.
        box = box_at(gmp, pos - 36, 36) if pos >= 36 else None
        recs.append((u32(gmp, pos), box or fallback))
    buckets = defaultdict(list)
    for ln, box in recs:
        buckets[ln].append(box)
    return [buckets[ln].pop(0) for ln in lens]


def fat_blocks(ent):
    out = []
    for off in range(0x20, 512, 2):
        v = struct.unpack_from("<H", ent, off)[0]
        if v == 0xFFFF:
            break
        out.append(v)
    return out


def list_gmps(path):
    with open(path, "rb") as f:
        f.seek(0x1200)
        ents = []
        for _ in range(400):
            ent = f.read(512)
            if not ent or ent[0] == 0:
                break
            if ent[0] != 1 or ent[9:12] != b"GMP":
                continue
            name = ent[1:9].decode().rstrip()
            ents.append((name, ent[0x11], u32(ent, 0x0C), fat_blocks(ent)))
    groups = {}
    for name, part, size, blocks in ents:
        groups.setdefault(name, []).append((part, size, blocks))
    out = []
    for name, parts in groups.items():
        parts.sort()
        size = parts[0][1]
        blocks = []
        for _, _, bl in parts:
            blocks.extend(bl)
        if size and blocks:
            out.append((name, size, blocks))
    return out


def read_chain(f, blocks, size):
    gmp = bytearray()
    for b in blocks:
        f.seek(b * BLOCK)
        gmp += f.read(BLOCK)
    return gmp[:size]


def write_chain(f, blocks, gmp):
    off = 0
    for b in blocks:
        chunk = gmp[off:off + BLOCK]
        if not chunk:
            break
        f.seek(b * BLOCK)
        f.write(chunk)
        off += len(chunk)


def mps_entry(path):
    with open(path, "rb") as f:
        f.seek(0x1200)
        for _ in range(8):
            ent = f.read(512)
            if ent[9:12] == b"MPS":
                return u32(ent, 0x0C), fat_blocks(ent)[0]
    raise SystemExit("MPS fehlt")


# Gleich lang mit Leerzeichen überschreiben. Kürzer würde die Offsets der Kachel verschieben.
NOTICES = (
    b"Copyright Garmin Ltd. or its subsidiaries.  All rights reserved.",
    b"Copying is expressly prohibited and may result in criminal charges and/or civil action being brought against you.",
    b"Schweiz Rasterkarte",
    b"Copyright 1995-2016 by GARMIN Corporation.",
)


def blank_lines(path):
    counts = {n: 0 for n in NOTICES}
    tail = max(len(n) for n in NOTICES) - 1
    with open(path, "r+b") as f:
        base, buf = 0, b""
        while True:
            chunk = f.read(8 * 1024 * 1024)
            buf += chunk
            limit = len(buf) if not chunk else len(buf) - tail
            for n in NOTICES:
                i = 0
                while True:
                    j = buf.find(n, i, limit)
                    if j < 0:
                        break
                    f.seek(base + j)
                    f.write(b" " * len(n))
                    counts[n] += 1
                    i = j + len(n)
            if not chunk:
                break
            base += limit
            buf = buf[limit:]
            f.seek(base + len(buf))
    if any(v != 190 for v in counts.values()):
        raise SystemExit(f"Hinweistexte nicht in allen Kacheln ersetzt: { {n[:24]: c for n, c in counts.items()} }")


def patch_names(path):
    size, block = mps_entry(path)
    with open(path, "r+b") as f:
        f.seek(0x49)
        f.write(b"SWISSTOPO".ljust(20, b"\x00"))
        f.seek(0x65)
        f.write(b" " * (0x83 - 0x65))
        f.seek(block * BLOCK)
        raw = bytearray(f.read(size))
        if OLD_NAME not in raw and NEW_NAME not in raw:
            raise SystemExit("Kartenname im MPS nicht gefunden")
        if OLD_ID not in raw and NEW_ID not in raw:
            raise SystemExit("Produktkennung im MPS nicht gefunden")
        raw = raw.replace(OLD_NAME, NEW_NAME).replace(OLD_ID, NEW_ID)
        if raw.count(NEW_ID) != 191 or OLD_ID in raw:
            raise SystemExit("Produktkennung nicht in allen 191 Kacheln ersetzt")
        f.seek(block * BLOCK)
        f.write(raw)


def coords_for(box, size):
    w, s_, e, n = box
    z = zoom_for(w, s_, e, n, size[0], size[1])
    x0, y0 = ll_tile(w, n, z)
    x1, y1 = ll_tile(e, s_, z)
    return {(z, x, y)
            for x in range(math.floor(x0), math.floor(x1) + 1)
            for y in range(math.floor(y0), math.floor(y1) + 1)}


def fill_gmp(gmp):
    sois, lens = jpeg_slots(gmp)
    boxes = index_boxes(gmp, lens)
    jobs, needed = [], set()
    for pos, box, ln in zip(sois, boxes, lens):
        wh = jpeg_wh(gmp[pos:pos + ln])
        needed |= coords_for(box, wh)
        jobs.append((pos, box, ln, wh))
    ensure_tiles(needed)
    kept = 0
    for pos, box, ln, wh in jobs:
        jpg = fit_jpeg(render(box, wh)[0], ln)
        if jpg is None:
            kept += 1
            continue
        gmp[pos:pos + ln] = jpg + b"\x00" * (ln - len(jpg))
    return len(jobs), kept


def probe():
    ok = fail = jpegs = 0
    with open(SRC, "rb") as f:
        for name, size, blocks in list_gmps(SRC):
            gmp = read_chain(f, blocks, size)
            try:
                sois, lens = jpeg_slots(gmp)
                boxes = index_boxes(gmp, lens)
                if name == "04956010":
                    # Dieses Bild zeigt Kappelerhof. Die Westkante liegt bei 8.282,
                    # die Bytes am Eintragsende wären die Spalte 970 m weiter östlich.
                    west = boxes[lens.index(93841)][0]
                    if not 8.28 < west < 8.29:
                        raise AssertionError(f"Baden-Spalte falsch, Westkante {west}")
                ok += 1
                jpegs += len(lens)
            except Exception as e:
                fail += 1
                print(f"FAIL {name} {type(e).__name__}: {e}", flush=True)
            if (ok + fail) % 20 == 0:
                print(f"{ok + fail}  ok {ok} fail {fail} jpegs {jpegs}", flush=True)
    print(f"fertig ok {ok} fail {fail} jpegs {jpegs}", flush=True)


DONE = "out/swisstopo.done"
BADEN = (8.306, 47.476)


def check_baden(tiles):
    """Mindestens ein Bild der Baden-Kacheln muss neu und als JPEG lesbar sein."""
    hits = 0
    with open(SRC, "rb") as src, open(DST, "rb") as dst:
        for name, size, blocks in tiles:
            head = read_chain(dst, blocks[:1], min(size, 0x120))
            w, s_, e, n = tre_box(head)
            if not (w <= BADEN[0] <= e and s_ <= BADEN[1] <= n):
                continue
            new = read_chain(dst, blocks, size)
            old = read_chain(src, blocks, size)
            sois, lens = jpeg_slots(new)
            mid = len(lens) // 2
            pos, ln = sois[mid], lens[mid]
            blob = bytes(new[pos:pos + ln])
            if blob == bytes(old[pos:pos + ln]):
                print(f"Baden-Kachel {name} unverändert", flush=True)
                continue
            im = Image.open(io.BytesIO(blob))
            im.load()
            assert im.size[0] >= 16 and im.size[1] >= 16
            hits += 1
            print(f"Baden-Prüfung {name} {im.size[0]}x{im.size[1]}", flush=True)
    if not hits:
        raise SystemExit("keine Baden-Kachel geprüft")


def main():
    import shutil
    os.makedirs("out", exist_ok=True)
    fresh = not os.path.exists(DST) or os.path.getsize(DST) != os.path.getsize(SRC)
    if fresh:
        print("kopiere Quelldatei", flush=True)
        shutil.copyfile(SRC, DST)
        if os.path.exists(DONE):
            os.remove(DONE)
    patch_names(DST)
    done = set()
    if os.path.exists(DONE):
        done = set(open(DONE).read().split())
    tiles = list_gmps(SRC)
    t0 = time.time()
    done_j = kept_n = skipped = 0
    with open(SRC, "rb") as src, open(DST, "r+b") as dst, open(DONE, "a") as mark:
        for i, (name, size, blocks) in enumerate(tiles, 1):
            if name in done:
                skipped += 1
                continue
            # Indexlängen gehören zu den Original-JPEGs. Die Zieldatei hat kürzere,
            # mit Nullen aufgefüllte Bilder, deren Länge der Index nicht mehr kennt.
            gmp = read_chain(src, blocks, size)
            try:
                nimg, kept = fill_gmp(gmp)
            except Exception as e:
                print(f"{i}/{len(tiles)} {name} übersprungen: {type(e).__name__}: {e}", flush=True)
                continue
            write_chain(dst, blocks, gmp)
            dst.flush()
            mark.write(name + "\n")
            mark.flush()
            done_j += nimg
            kept_n += kept
            dt = time.time() - t0
            print(f"{i}/{len(tiles)} {name} {nimg} Bilder, {kept} alt gelassen, "
                  f"{dt / 60:.0f} min", flush=True)
    size, block = mps_entry(DST)
    with open(DST, "rb") as f:
        f.seek(block * BLOCK)
        mps = f.read(size)
    assert NEW_NAME in mps and OLD_NAME not in mps
    assert os.path.getsize(DST) == os.path.getsize(SRC)
    blank_lines(DST)
    check_baden(tiles)
    print(DST, os.path.getsize(DST), "Bytes")
    print(f"{done_j} Bilder neu, {kept_n} Slots zu klein (altes Bild bleibt), {skipped} Kacheln schon fertig")


if __name__ == "__main__":
    import sys
    if "--probe" in sys.argv:
        probe()
    else:
        main()
