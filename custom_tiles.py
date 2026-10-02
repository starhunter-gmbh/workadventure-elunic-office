"""Draw tilesets/elunic_custom.png: furniture the WA starter kit lacks (kicker, table tennis, TV, dart, rotated sofa)."""
from PIL import Image, ImageDraw

T = 32
COLS, ROWS = 8, 5
img = Image.new('RGBA', (COLS * T, ROWS * T), (0, 0, 0, 0))
d = ImageDraw.Draw(img)

def at(i):  # pixel origin of tile index i
    return (i % COLS) * T, (i // COLS) * T

# kicker 3x2 (tiles 0-2 / 8-10): wooden frame, green field, rods with players
x0, y0 = at(0)
d.rectangle([x0 + 4, y0 + 8, x0 + 3 * T - 5, y0 + 2 * T - 6], fill=(92, 58, 30), outline=(50, 30, 15))
d.rectangle([x0 + 10, y0 + 13, x0 + 3 * T - 11, y0 + 2 * T - 11], fill=(46, 140, 60))
d.line([x0 + 48, y0 + 13, x0 + 48, y0 + 2 * T - 11], fill=(230, 240, 230))
d.ellipse([x0 + 42, y0 + 30, x0 + 54, y0 + 42], outline=(230, 240, 230))
for i, rx in enumerate(range(x0 + 18, x0 + 3 * T - 12, 11)):
    d.line([rx, y0 + 4, rx, y0 + 2 * T - 2], fill=(190, 190, 200), width=2)
    col = (210, 40, 40) if i % 2 else (40, 70, 200)
    for py in (y0 + 22, y0 + 34, y0 + 46):
        d.rectangle([rx - 2, py - 2, rx + 2, py + 2], fill=col)
    d.rectangle([rx - 2, y0 + 1, rx + 2, y0 + 5], fill=(30, 30, 30))
    d.rectangle([rx - 2, y0 + 2 * T - 5, rx + 2, y0 + 2 * T - 1], fill=(30, 30, 30))

# table tennis 2x2 (tiles 3-4 / 11-12)
x0, y0 = at(3)
d.rectangle([x0 + 3, y0 + 3, x0 + 2 * T - 4, y0 + 2 * T - 8], fill=(30, 110, 70), outline=(240, 240, 240), width=2)
d.line([x0 + T, y0 + 3, x0 + T, y0 + 2 * T - 8], fill=(240, 240, 240))
d.rectangle([x0 + 1, y0 + T - 2, x0 + 2 * T - 2, y0 + T + 1], fill=(250, 250, 250))
for lx in (x0 + 6, x0 + 2 * T - 8):
    d.rectangle([lx, y0 + 2 * T - 8, lx + 2, y0 + 2 * T - 1], fill=(60, 60, 60))
d.ellipse([x0 + 44, y0 + 40, x0 + 49, y0 + 45], fill=(250, 140, 30))

# TV 1x3 on a left wall, screen facing right (tiles 5 / 13 / 21)
x0, y0 = at(5)
d.rectangle([x0 + 2, y0 + 2, x0 + 9, y0 + 3 * T - 3], fill=(25, 25, 30))
d.rectangle([x0 + 9, y0 + 4, x0 + 13, y0 + 3 * T - 5], fill=(40, 40, 48))
d.rectangle([x0 + 10, y0 + 6, x0 + 12, y0 + 3 * T - 7], fill=(70, 120, 190))

# dart board (tile 6)
x0, y0 = at(6)
for r, c in ((13, (30, 30, 30)), (11, (230, 210, 150)), (8, (200, 40, 40)), (5, (230, 210, 150)), (2, (40, 150, 60))):
    d.ellipse([x0 + 16 - r, y0 + 16 - r, x0 + 16 + r, y0 + 16 + r], fill=c)

# urinal on a left wall, facing right (tile 7)
x0, y0 = at(7)
d.rectangle([x0 + 1, y0 + 6, x0 + 4, y0 + 26], fill=(150, 160, 170))
d.rounded_rectangle([x0 + 3, y0 + 8, x0 + 16, y0 + 24], radius=6, fill=(235, 240, 245), outline=(150, 160, 170))
d.ellipse([x0 + 7, y0 + 12, x0 + 13, y0 + 20], fill=(200, 215, 225))

# 3-seat sofa (WA_Seats 1375-1377 / 1388-1390) rotated so it faces left: 2x3 at tiles 16-17 / 24-25 / 32-33
seats = Image.open('tilesets/WA_Seats.png').convert('RGBA')
sofa = seats.crop((0, 0, 3 * T, 2 * T)).rotate(-90, expand=True)   # 64x96, back on the right
x0, y0 = at(16)
img.alpha_composite(sofa, (x0, y0))

# sink (WA_Other_Furniture 282) turned towards a side wall: tile 19 back on the left, tile 20 back on the right
other = Image.open('tilesets/WA_Other_Furniture.png').convert('RGBA')
sink = other.crop((3 * T, 5 * T, 4 * T, 6 * T))
img.alpha_composite(sink.rotate(90), at(19)); img.alpha_composite(sink.rotate(-90), at(20))

img.save('tilesets/elunic_custom.png')
