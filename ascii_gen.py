"""
Convert a photo into ASCII art sized for the profile SVG (25 rows x 42 cols).

Usage:
    pip install pillow
    python ascii_gen.py path/to/photo.jpg [gamma]

Prints the ASCII art to the terminal. gamma (default 1.0) < 1 darkens
midtones (denser glyphs), > 1 lightens them.

Pipeline:
- samples the four image corners and chroma-keys anything close to that
  color as background (blank space)
- center-crops to the aspect ratio of the 42x25 character grid so the
  face is not stretched (character cells are ~2.3x taller than wide)
- area-averages down to one luma sample per character cell
- maps dark pixels to dense glyphs, light to sparse ("ink on paper" look)
"""
import sys
from PIL import Image, ImageOps

COLS = 37
ROWS = 25
CHAR_W, CHAR_H = 9.6, 20.0          # Consolas 16px cell in the SVG (incl. 109% size-adjust)
RAMP = "@Nm%kwj|(;:,'.` "           # dark -> light
BG_DIST = 90                        # max RGB distance to corner color = background


def key_background(img):
    """Return alpha mask: 0 where pixel matches corner (background) color."""
    w, h = img.size
    corners = [img.getpixel(p) for p in [(2, 2), (w - 3, 2), (2, h - 3), (w - 3, h - 3)]]
    cr = sum(c[0] for c in corners) / 4
    cg = sum(c[1] for c in corners) / 4
    cb = sum(c[2] for c in corners) / 4
    mask = Image.new("L", img.size, 255)
    px, mpx = img.load(), mask.load()
    for y in range(h):
        for x in range(w):
            r, g, b = px[x, y][:3]
            if ((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2) ** 0.5 < BG_DIST:
                mpx[x, y] = 0
    return mask


def to_ascii(path, gamma=1.0):
    img = Image.open(path).convert("RGB")
    mask = key_background(img)

    # center-crop to grid aspect so proportions survive rectangular cells
    grid_aspect = (COLS * CHAR_W) / (ROWS * CHAR_H)
    w, h = img.size
    target_w = int(h * grid_aspect)
    if target_w <= w:
        left = (w - target_w) // 2
        box = (left, 0, left + target_w, h)
    else:
        target_h = int(w / grid_aspect)
        top = (h - target_h) // 2
        box = (0, top, w, top + target_h)
    img, mask = img.crop(box), mask.crop(box)

    luma = ImageOps.autocontrast(img.convert("L"), cutoff=1)
    small = luma.resize((COLS, ROWS), Image.LANCZOS)
    msmall = mask.resize((COLS, ROWS), Image.LANCZOS)

    lines = []
    for y in range(ROWS):
        line = ""
        for x in range(COLS):
            if msmall.getpixel((x, y)) < 128:
                line += " "
                continue
            v = (small.getpixel((x, y)) / 255) ** gamma
            idx = int(v * (len(RAMP) - 1) + 0.5)
            line += RAMP[idx]
        lines.append(line.rstrip())
    return lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    g = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    for line in to_ascii(sys.argv[1], g):
        print(line)
