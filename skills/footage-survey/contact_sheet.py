#!/usr/bin/env python3
"""Contact sheets from frames BashCutPro rendered, and the batch that renders them. Standard library only.

  contact_sheet.py plan --item ID --seconds 95.2 --count 12 --dir /abs/tmp/frames [--from S --to S]
      prints one command_batch `steps` list of file.exportFrame (target "source"), times evenly spread
  contact_sheet.py plan --program --at 1.5,4.2,9.8 --dir /abs/tmp/cuts
      the same for the edit (target "program") at given timeline seconds, or --seconds/--count spread over it
  contact_sheet.py sheet /abs/tmp/frames/*.png -o /abs/tmp/sheet.png [--cols 4] [--width 320]
      tiles the PNGs in name order, each cell numbered in its corner; prints the sheet path and one line per cell

`plan` names files <item>-<seconds>.png (program-<seconds>.png), so `sheet` can print each cell's source second. Frames from MCP
`render_frame` saved as PNG tile the same way. Reads 8 or 16-bit PNG (grey, RGB, palette, with alpha; not
interlaced), writes 8-bit RGB PNG."""
import argparse, glob, json, os, re, struct, sys, zlib

TICKS = 254016000000  # per second
# 3x5 digits for the cell numbers, one row of three bits per line.
DIGITS = {"0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111",
          "4": "101101111001001", "5": "111100111001111", "6": "111100111101111", "7": "111001010010010",
          "8": "111101111101111", "9": "111101111001111"}


def read_png(path):
    """(width, height, rows of RGB bytes)."""
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path}: not a PNG")
    pos, idat, palette = 8, [], None
    while pos < len(data):
        size, tag = struct.unpack(">I4s", data[pos:pos + 8])
        body = data[pos + 8:pos + 8 + size]
        if tag == b"IHDR":
            w, h, depth, ctype, _, _, interlace = struct.unpack(">IIBBBBB", body)
        elif tag == b"PLTE":
            palette = body
        elif tag == b"IDAT":
            idat.append(body)
        pos += 12 + size
    if interlace or depth not in (8, 16) and ctype != 3 or ctype == 3 and depth != 8:
        raise ValueError(f"{path}: interlaced or unsupported bit depth")
    chans = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
    bpp = chans * depth // 8
    raw, stride = zlib.decompress(b"".join(idat)), w * bpp
    prev, rows, i = bytearray(stride), [], 0
    for _ in range(h):
        f, line = raw[i], bytearray(raw[i + 1:i + 1 + stride])
        i += 1 + stride
        for x in range(stride):  # undo the PNG row filter
            a = line[x - bpp] if x >= bpp else 0
            b, c = prev[x], prev[x - bpp] if x >= bpp else 0
            if f == 1:
                line[x] = (line[x] + a) & 255
            elif f == 2:
                line[x] = (line[x] + b) & 255
            elif f == 3:
                line[x] = (line[x] + (a + b) // 2) & 255
            elif f == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[x] = (line[x] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 255
        prev = line
        px = line[::2] if depth == 16 else line  # 16-bit: keep the high byte
        if ctype == 3:
            rgb = b"".join(palette[3 * v:3 * v + 3] for v in px)
        elif ctype in (0, 4):
            g = px[::chans]
            rgb = bytes(v for v in g for _ in range(3))
        else:
            rgb = bytes(px) if chans == 3 else bytes(b for k in range(0, len(px), 4) for b in px[k:k + 3])
        rows.append(rgb)
    return w, h, rows


def write_png(path, w, h, rows):
    def chunk(tag, body):
        return struct.pack(">I", len(body)) + tag + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)
    raw = b"".join(b"\x00" + bytes(r) for r in rows)
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def scaled(w, h, rows, cw):
    """Nearest-neighbour resize to width cw, aspect kept."""
    ch = max(1, round(h * cw / w))
    xs = [min(w - 1, int((x + 0.5) * w / cw)) * 3 for x in range(cw)]
    out = []
    for y in range(ch):
        src = rows[min(h - 1, int((y + 0.5) * h / ch))]
        out.append(bytes(b for x in xs for b in src[x:x + 3]))
    return cw, ch, out


def stamp(canvas, x0, y0, text, scale):
    """White digits on a black plate at (x0, y0) of a canvas of bytearray rows."""
    pw, ph = (len(text) * 4 + 1) * scale, 7 * scale
    for y in range(y0, min(y0 + ph, len(canvas))):
        end = min(x0 + pw, len(canvas[y]) // 3)
        canvas[y][x0 * 3:end * 3] = bytes(3 * (end - x0))
    for n, d in enumerate(text):
        for k, bit in enumerate(DIGITS[d]):
            if bit == "1":
                gx, gy = x0 + (1 + n * 4 + k % 3) * scale, y0 + (1 + k // 3) * scale
                for y in range(gy, gy + scale):
                    if y < len(canvas):
                        canvas[y][gx * 3:(gx + scale) * 3] = b"\xff" * (3 * scale)


def cmd_plan(o):
    if o.at:
        times = [float(t) for t in o.at.split(",")]
    else:
        if o.seconds is None:
            sys.exit("plan needs --seconds (with --count) or --at")
        start, end = o.start or 0.0, o.to if o.to is not None else o.seconds
        times = [start + (end - start) * (i + 0.5) / o.count for i in range(o.count)]
    name = "program" if o.program else re.sub(r"[^A-Za-z0-9_-]", "_", o.item)
    target = {"target": "program"} if o.program else {"target": "source", "item": o.item}
    steps = [{"id": "file.exportFrame", "params": dict(target, time=round(t * TICKS), format="png",
                                                        path=os.path.join(o.dir, f"{name}-{t:08.2f}.png"))}
             for t in times]
    print(json.dumps(steps, indent=1))


def cmd_sheet(o):
    files = sorted(f for p in o.frames for f in (glob.glob(p) or [p]))
    if not files:
        sys.exit("no frames")
    cells = []
    for f in files:
        try:
            cells.append((f, scaled(*read_png(f), o.width)))
        except (OSError, ValueError, KeyError, zlib.error) as e:
            print(f"skipped {f}: {e}", file=sys.stderr)
    if not cells:
        sys.exit("no readable frames")
    gap, cols = 4, min(o.cols, len(cells))
    ch = max(c[1][1] for c in cells)
    nrows = (len(cells) + cols - 1) // cols
    W, H = cols * o.width + (cols + 1) * gap, nrows * ch + (nrows + 1) * gap
    canvas = [bytearray(b"\x20" * (3 * W)) for _ in range(H)]
    scale = max(2, o.width // 80)
    for n, (f, (cw, hh, rows)) in enumerate(cells):
        x0, y0 = gap + (n % cols) * (o.width + gap), gap + (n // cols) * (ch + gap)
        for y, r in enumerate(rows):
            canvas[y0 + y][x0 * 3:(x0 + cw) * 3] = r
        stamp(canvas, x0, y0, str(n + 1), scale)
    write_png(o.out, W, H, canvas)
    print(o.out)
    for n, (f, _) in enumerate(cells):
        m = re.search(r"-(\d+(?:\.\d+)?)\.png$", f)
        print(f"{n + 1} {os.path.basename(f)}" + (f"  {float(m.group(1)):.2f}s" if m else ""))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="print file.exportFrame steps for one media item or the edit")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--item", help="a media item (source frames)")
    g.add_argument("--program", action="store_true", help="the edit's composite (timeline seconds)")
    p.add_argument("--seconds", type=float, help="the item's (or the edit's) length")
    p.add_argument("--at", help="comma-separated seconds instead of --seconds/--count")
    p.add_argument("--count", type=int, default=12)
    p.add_argument("--dir", required=True, help="absolute folder for the PNGs")
    p.add_argument("--from", dest="start", type=float)
    p.add_argument("--to", type=float)
    s = sub.add_parser("sheet", help="tile PNGs into one numbered sheet")
    s.add_argument("frames", nargs="+")
    s.add_argument("-o", dest="out", required=True)
    s.add_argument("--cols", type=int, default=4)
    s.add_argument("--width", type=int, default=320, help="cell width in pixels")
    o = ap.parse_args(argv)
    cmd_plan(o) if o.cmd == "plan" else cmd_sheet(o)


if __name__ == "__main__":
    main()
