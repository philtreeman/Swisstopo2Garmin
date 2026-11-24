#!/usr/bin/env python3
"""DSKIMG/GMP-Hülle für SwissTOPO2026 Raster ohne die 3,5-GB-Garmin-Vorlage.

Die Binärstubben `_raster_img_head.bin` und `_raster_gmp_stub.bin` sind
strukturelle Header (Magic, TRE/RGN/LBL-Gerüst), ohne JPEG-Kartendaten und
ohne Copyright-Texte. Sie stammen aus der Analyse des Formats; die Pixel
kommen ausschliesslich von swisstopo WMTS.
"""
from __future__ import annotations

import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
BLOCK = 65536
HEAD_TMPL = HERE / "_raster_img_head.bin"
GMP_STUB = HERE / "_raster_gmp_stub.bin"

# Family/Product: gleiche ID wie beim Slot-Ersatz (kein SQL nötig).
PRODUCT_ID = 1
FAMILY_ID = 0x5354  # 21332
LIST_NAME = b"SwissTOPO2026 Raster"
assert len(LIST_NAME) == 20
MPS_NAME = LIST_NAME.ljust(27)  # wie im Original-MPS (27 Byte inkl. NUL-Pad)


def deg_to_garmin32(deg: float) -> int:
    v = int(round(deg / 360.0 * 2**32)) & 0xFFFFFFFF
    return v


def deg_to_garmin24(deg: float) -> bytes:
    v = (int(round(deg / 360.0 * 2**32)) >> 8) & 0xFFFFFF
    return v.to_bytes(3, "little")


def pack_box_nesw(west: float, south: float, east: float, north: float) -> bytes:
    """16 Bytes N,E,S,W als Garmin-32-Bit-Winkel."""
    return struct.pack(
        "<IIII",
        deg_to_garmin32(north),
        deg_to_garmin32(east),
        deg_to_garmin32(south),
        deg_to_garmin32(west),
    )


def patch_tre_bounds(stub: bytearray, west: float, south: float, east: float, north: float) -> None:
    tre = struct.unpack_from("<I", stub, 0x19)[0]
    stub[tre + 0x15:tre + 0x18] = deg_to_garmin24(north)
    stub[tre + 0x18:tre + 0x1B] = deg_to_garmin24(east)
    stub[tre + 0x1B:tre + 0x1E] = deg_to_garmin24(south)
    stub[tre + 0x1E:tre + 0x21] = deg_to_garmin24(west)


def build_index(boxes_and_lens: list[tuple[tuple[float, float, float, float], int]]) -> bytes:
    """Eine Indexkopie: [coords][len][06b3][14 Byte] … in JPEG-Reihenfolge."""
    # Mid-Felder: im Original variabel; Konstante aus dem Stub-Kachelformat.
    mid = bytes.fromhex("dfff17ff07336378e20700e02b01")
    assert len(mid) == 14
    out = bytearray()
    for box, ln in boxes_and_lens:
        out += pack_box_nesw(*box)
        out += struct.pack("<I", ln)
        out += b"\x06\xb3"
        out += mid
    return bytes(out)


def fat_entry(name: str, ext: str, size: int, part: int, blocks: list[int]) -> bytes:
    ent = bytearray(512)
    ent[0] = 1
    ent[1:9] = name.encode("ascii").ljust(8)[:8]
    ent[9:12] = ext.encode("ascii").ljust(3)[:3]
    struct.pack_into("<I", ent, 0x0C, size)
    ent[0x11] = part
    off = 0x20
    for b in blocks:
        struct.pack_into("<H", ent, off, b)
        off += 2
    if off <= 510:
        struct.pack_into("<H", ent, off, 0xFFFF)
    return bytes(ent)


def build_mps(segment_names: list[str]) -> bytes:
    """MPS: ein F-Record + ein L-Record je GMP-Segment."""
    fam = struct.pack("<HH", PRODUCT_ID, FAMILY_ID)
    name27 = MPS_NAME[:27]
    frec = b"F" + struct.pack("<H", 32) + fam + name27 + b"\x00"
    out = bytearray(frec)
    # Schlussbytes wie im Original-L-Record (Karten-IDs/Flags, Gerät akzeptiert sie).
    l_tail = bytes.fromhex("0000408a020100000000")
    for name in segment_names:
        seg = name.encode("ascii")[:8].ljust(8, b"\x00")
        payload = fam + struct.pack("<I", 0) + name27 + seg + l_tail
        payload = payload[:54].ljust(54, b"\x00")
        out += b"L" + struct.pack("<H", 54) + payload
    return bytes(out)


def build_gmp(
    west: float,
    south: float,
    east: float,
    north: float,
    tiles: list[tuple[tuple[float, float, float, float], bytes]],
) -> bytes:
    """GMP: Stub + 3× Index + JPEGs. lengths müssen eindeutig sein (Padding)."""
    stub = bytearray(GMP_STUB.read_bytes())
    patch_tre_bounds(stub, west, south, east, north)

    used = set()
    packed = []
    for box, jpg in tiles:
        blob = jpg
        # Nach EOI mit Nullen verlängern, bis die Länge einzigartig ist.
        while len(blob) in used or len(blob) < 128:
            blob += b"\x00"
        used.add(len(blob))
        packed.append((box, blob))

    index = build_index([(b, len(j)) for b, j in packed])
    # Original hat drei Indexkopien hintereinander.
    body = index + index + index + b"".join(j for _, j in packed)
    return bytes(stub) + body


def write_img(path: str | Path, gmps: list[tuple[str, bytes]]) -> None:
    """Schreibt eine DSKIMG mit MPS und den GMP-Kacheln."""
    if not HEAD_TMPL.is_file() or not GMP_STUB.is_file():
        raise SystemExit(
            f"Format-Stubben fehlen ({HEAD_TMPL.name}, {GMP_STUB.name}). "
            "Liegen unter scripts/ und gehören ins Repo."
        )
    head = bytearray(HEAD_TMPL.read_bytes())
    head[0x49:0x5D] = LIST_NAME.ljust(20, b"\x00")
    head[0x65:0x83] = b" " * (0x83 - 0x65)

    names = [n for n, _ in gmps]
    mps = build_mps(names)
    mps_block = 3
    data_block = 4

    # Blockkette je Datei
    def pad_blocks(data: bytes) -> tuple[bytes, list[int], int]:
        nonlocal data_block
        n = (len(data) + BLOCK - 1) // BLOCK
        blocks = list(range(data_block, data_block + n))
        data_block += n
        pad = data + b"\x00" * (n * BLOCK - len(data))
        return pad, blocks, n

    mps_pad = mps + b"\x00" * (BLOCK - len(mps))
    fat = bytearray()
    fat += fat_entry("TOPO_SWI", "MPS", len(mps), 0, [mps_block])
    payloads = [mps_pad]
    for name, gmp in gmps:
        pad, blocks, _ = pad_blocks(gmp)
        chunks = [blocks[i:i + 240] for i in range(0, len(blocks), 240)]
        for part, chunk in enumerate(chunks):
            fat += fat_entry(name, "GMP", len(gmp) if part == 0 else 0, part, chunk)
        payloads.append(pad)

    # FAT hinter Spezial-Eintrag bei 0x1000; Einträge ab 0x1200.
    # Head-Vorlage endet bei 0x1200; wir hängen FAT + Padding bis Block 3 an.
    file_head = bytearray(head)
    # Blocks 0..2: head spans block0; special dir uses blocks 1,2; MPS at 3.
    # Physikalisch: Bytes 0 .. 3*BLOCK-1 vor MPS.
    pre = bytearray(3 * BLOCK)
    pre[: len(file_head)] = file_head
    pre[0x1200:0x1200 + len(fat)] = fat

    with open(path, "wb") as f:
        f.write(pre)
        for p in payloads:
            f.write(p)
