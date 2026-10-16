#!/usr/bin/env python3
"""Eine Kachel aus TopoCHProV5raster.img mit swisstopo-Bildern neu füllen.

Die JPEGs bleiben in den originalen Längenslots (nach dem EOI mit Nullen
aufgefüllt). shortcut: andere Längen verschieben den Index; erst nach einem
erfolgreichen Edge-Test einen echten Schreiber bauen. Nur die Detailkachel,
die Baden enthält, nicht die ganze Schweiz.
"""
import io, math, struct, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw

SRC = "TopoCHProV5raster.img"
DST = "out/rastertest.img"
BLOCK = 65536
LAYER = "ch.swisstopo.pixelkarte-farbe-pk25.noscale"
URL = "https://wmts.geo.admin.ch/1.0.0/{layer}/default/current/3857/{z}/{x}/{y}.jpeg"
ZOOM = 16  # shortcut: 512px-Slot zeigt feineres Quellmaterial nur heruntergerechnet
BADEN = (8.306, 47.476)  # Innenstadt, nicht am Kachelrand
OLD_NAME = b"TOPO Switzerland PRO Raster"
NEW_NAME = b"RASTER TEST".ljust(len(OLD_NAME))


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


def download_all(coords):
    cache = {}

    def one(xy):
        z, x, y = xy
        url = URL.format(layer=LAYER, z=z, x=x, y=y)
        err = None
        for i in range(4):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    return xy, Image.open(io.BytesIO(r.read())).convert("RGB")
            except Exception as e:
                err = e
                time.sleep(2**i)
        raise SystemExit(f"WMTS {z}/{x}/{y}: {err}")

    with ThreadPoolExecutor(8) as ex:
        for xy, img in ex.map(one, coords):
            cache[xy] = img
    return cache


def render(box, cache, size):
    west, south, east, north = box
    x0f, y0f = ll_tile(west, north, ZOOM)
    x1f, y1f = ll_tile(east, south, ZOOM)
    xs = range(math.floor(x0f), math.floor(x1f) + 1)
    ys = range(math.floor(y0f), math.floor(y1f) + 1)
    canvas = Image.new("RGB", (256 * len(xs), 256 * len(ys)))
    x0, y0 = xs[0], ys[0]
    for x in xs:
        for y in ys:
            canvas.paste(cache[(ZOOM, x, y)], ((x - x0) * 256, (y - y0) * 256))
    crop = canvas.crop((
        round((x0f - x0) * 256), round((y0f - y0) * 256),
        round((x1f - x0) * 256), round((y1f - y0) * 256),
    ))
    img = crop.resize(size, Image.Resampling.LANCZOS)
    width = max(4, min(size) // 28)
    ImageDraw.Draw(img).rectangle((0, 0, size[0] - 1, size[1] - 1), outline=(255, 0, 255), width=width)
    return img


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
    trials.append(Image.new("RGB", img.size, (255, 0, 255)))
    for trial in trials:
        for q in (70, 40, 20, 8, 1):
            data = encode_jpeg(trial, q)
            if len(data) <= limit:
                return data
    raise SystemExit(f"JPEG passt in keinen Slot von {limit} Bytes")


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
    if 45 < s_ < n < 48 and 5 < w < e < 11 and (n - s_) < 0.5 and (e - w) < 0.5:
        return w, s_, e, n
    return None


def jpeg_slots(gmp):
    sois, s = [], 0
    while True:
        i = gmp.find(b"\xff\xd8\xff", s)
        if i < 0:
            break
        sois.append(i)
        s = i + 3
    lens = [jpeg_end(gmp, i) - i for i in sois]
    assert sois[0] + sum(lens) == jpeg_end(gmp, sois[-1])
    return sois, lens


def index_boxes(gmp, lens):
    """Erste Indexkopie. Einträge sind 36, 37 oder 38 Bytes, Koordinaten die letzten 16."""
    sig = struct.pack("<I", lens[0]) + b"\x06\xb3"
    start = gmp.find(sig)
    second = gmp.find(sig, start + 1)
    assert start > 0 and second > start
    want = set(lens)
    recs = []
    pos = start
    while pos < second:
        if gmp[pos + 4:pos + 6] == b"\x06\xb3" and u32(gmp, pos) in want:
            pick = None
            for stride in (36, 37, 38, 39, 40):
                box = box_at(gmp, pos, stride)
                if not box:
                    continue
                nxt = pos + stride
                if nxt + 6 <= second and gmp[nxt + 4:nxt + 6] == b"\x06\xb3" and u32(gmp, nxt) in want:
                    pick = (stride, box)
                    break
                if pick is None:
                    pick = (stride, box)
            if pick:
                recs.append((u32(gmp, pos), pick[1]))
                pos += pick[0]
                continue
        pos += 1
    from collections import Counter, defaultdict
    assert Counter(ln for ln, _ in recs) == Counter(lens)
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


def load_tile(point):
    lon, lat = point
    with open(SRC, "rb") as f:
        f.seek(0x1200)
        ents = []
        for _ in range(348):
            ent = f.read(512)
            if ent[0] != 1 or ent[9:12] != b"GMP":
                continue
            name = ent[1:9].decode().rstrip()
            size = u32(ent, 0x0C)
            part = ent[0x11]
            ents.append((name, part, size, fat_blocks(ent)))
    groups = {}
    for name, part, size, blocks in ents:
        groups.setdefault(name, []).append((part, size, blocks))
    best = None
    with open(SRC, "rb") as f:
        for name, parts in groups.items():
            parts.sort()
            size, blocks = parts[0][1], parts[0][2]
            if not size or not blocks:
                continue
            f.seek(blocks[0] * BLOCK + 0xF0)
            b = f.read(0x21)
            n = deg24(int.from_bytes(b[0x15:0x18], "little"))
            e = deg24(int.from_bytes(b[0x18:0x1B], "little"))
            s_ = deg24(int.from_bytes(b[0x1B:0x1E], "little"))
            w = deg24(int.from_bytes(b[0x1E:0x21], "little"))
            if w <= lon <= e and s_ <= lat <= n:
                area = (e - w) * (n - s_)
                if best is None or area < best[0]:
                    best = (area, name, (w, s_, e, n), parts)
    assert best, "keine Kachel enthält den Punkt"
    _, name, bounds, parts = best
    size = parts[0][1]
    blocks = []
    for _, _, bl in parts:
        blocks.extend(bl)
    gmp = bytearray()
    with open(SRC, "rb") as f:
        for b in blocks:
            f.seek(b * BLOCK)
            gmp += f.read(BLOCK)
    return name, bounds, gmp[:size]


def fat_entry(name, ext, size, part, blocks):
    ent = bytearray(512)
    ent[0] = 1
    ent[1:9] = name.encode().ljust(8)
    ent[9:12] = ext.encode()
    struct.pack_into("<I", ent, 0x0C, size)
    ent[0x11] = part
    off = 0x20
    for b in blocks:
        struct.pack_into("<H", ent, off, b)
        off += 2
    if off <= 510:
        struct.pack_into("<H", ent, off, 0xFFFF)
    return ent


def main():
    import os
    from collections import Counter
    os.makedirs("out", exist_ok=True)
    name, (tw, ts, te, tn), gmp = load_tile(BADEN)
    print(f"Kachel {name}  {tw:.3f},{ts:.3f} .. {te:.3f},{tn:.3f}  {len(gmp)} Bytes", flush=True)
    sois, lens = jpeg_slots(gmp)
    boxes = [( *b, ln) for b, ln in zip(index_boxes(gmp, lens), lens)]
    assert Counter(b[4] for b in boxes) == Counter(lens)

    needed = set()
    for w, s_, e, n, _ in boxes:
        x0, y0 = ll_tile(w, n, ZOOM)
        x1, y1 = ll_tile(e, s_, ZOOM)
        for x in range(math.floor(x0), math.floor(x1) + 1):
            for y in range(math.floor(y0), math.floor(y1) + 1):
                needed.add((ZOOM, x, y))
    print(f"{len(boxes)} Bilder, {len(needed)} WMTS-Kacheln", flush=True)
    cache = download_all(needed)

    pos = sois[0]
    for i, (w, s_, e, n, ln) in enumerate(boxes):
        wh = jpeg_wh(gmp[pos:pos + ln])
        jpg = fit_jpeg(render((w, s_, e, n), cache, wh), ln)
        gmp[pos:pos + ln] = jpg + b"\x00" * (ln - len(jpg))
        pos += ln
        print(f"  {i:02d} {len(jpg):6d}/{ln} {wh[0]}x{wh[1]}  {w:.3f},{s_:.3f} .. {e:.3f},{n:.3f}", flush=True)

    with open(SRC, "rb") as f:
        head = bytearray(f.read(0x1200))
        f.seek(3 * BLOCK)
        raw = f.read(10865)
    head += bytearray(3 * BLOCK - len(head))
    head[0x65:0x83] = b" RASTER TEST".ljust(0x83 - 0x65)
    off = 0
    frec = lrec = None
    while off + 3 <= len(raw):
        ln = int.from_bytes(raw[off + 1:off + 3], "little")
        rec = raw[off:off + 3 + ln]
        if rec[0] == ord("F") and frec is None:
            frec = rec
        if rec[0] == ord("L") and name.encode() in rec:
            lrec = rec
        off += 3 + ln
    assert frec and lrec, name
    mps = frec.replace(OLD_NAME, NEW_NAME) + lrec.replace(OLD_NAME, NEW_NAME)
    nblocks = (len(gmp) + BLOCK - 1) // BLOCK
    data_blocks = list(range(4, 4 + nblocks))
    chunks = [data_blocks[i:i + 240] for i in range(0, len(data_blocks), 240)]
    fat = fat_entry("TOPO_SWI", "MPS", len(mps), 0, [3])
    for part, chunk in enumerate(chunks):
        fat += fat_entry(name, "GMP", len(gmp) if part == 0 else 0, part, chunk)
    head[0x1200:0x1200 + len(fat)] = fat

    pad_gmp = bytes(gmp) + b"\x00" * (nblocks * BLOCK - len(gmp))
    with open(DST, "wb") as f:
        f.write(head)
        f.write(mps + b"\x00" * (BLOCK - len(mps)))
        f.write(pad_gmp)

    # Selbstcheck: Randpixel ist Magenta, Slot-Längen unverändert.
    with open(DST, "rb") as f:
        f.seek(4 * BLOCK)
        back = f.read(len(gmp))
    p = sois[0]
    for ln in (b[4] for b in boxes):
        slot = bytes(back[p:p + ln])
        im = Image.open(io.BytesIO(slot))
        r, g, b = im.getpixel((1, im.height // 2))[:3]
        assert r > 200 and g < 80 and b > 200, (r, g, b)
        p += ln
    print(DST, os.path.getsize(DST), "Bytes")
    print(f"Baden liegt in der Kachel ({tw:.3f}–{te:.3f} E, {ts:.3f}–{tn:.3f} N)")


if __name__ == "__main__":
    main()
