"""
Convert a photo into ASCII art sized for the profile SVG (25 rows x 44 cols).

Usage:
    pip install pillow
    python ascii_gen.py path/to/photo.jpg

Prints the ASCII art to the terminal. Paste the rows into the <tspan> lines
of dark_mode.svg and light_mode.svg (one row per tspan, y = 30, 50, ... 510).

Tips for best results:
- Crop the photo tight around head and shoulders before converting.
- A plain background converts cleanest; the script treats very bright or
  very saturated background pixels as empty space.
"""
import sys
from PIL import Image

COLS = 44
ROWS = 25
# darkest -> lightest; characters chosen to match the hand-drawn style
RAMP = "@Nmkwj|;,'` "
# each character cell is taller than wide; sample accordingly
CHAR_ASPECT = 2.2


def to_ascii(path):
    img = Image.open(path).convert("RGB")
    w, h = img.size
    hsv = img.convert("HSV")
    cell_w = w / COLS
    cell_h = h / ROWS
    lines = []
    for row in range(ROWS):
        line = ""
        for col in range(COLS):
            x = int((col + 0.5) * cell_w)
            y = int((row + 0.5) * cell_h)
            r, g, b = img.getpixel((x, y))
            _, s, v = hsv.getpixel((x, y))
            # saturated bright pixels are likely a colored backdrop -> blank
            if s > 150 and v > 150:
                line += " "
                continue
            luma = 0.299 * r + 0.587 * g + 0.114 * b
            idx = int(luma / 256 * len(RAMP))
            line += RAMP[min(idx, len(RAMP) - 1)]
        lines.append(line.rstrip())
    return lines


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    for line in to_ascii(sys.argv[1]):
        print(line)
