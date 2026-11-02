"""Draw the "Curved Widescreen" entity sprites (black/white, 4 directions) in the palette of the other elunic screens.

Down/Up: 64x32 (two tiles wide), Left/Right: 32x64 (side view, two tiles high). Run from this directory.
"""
from PIL import Image, ImageDraw

SCREEN, SCREEN_DARK, WINDOW, WINDOW_GREY = (127, 163, 191), (98, 126, 148), (247, 247, 247), (198, 209, 216)
SKIN = {
    'Black': dict(bezel=(100, 89, 114), back=(75, 65, 88), back_dark=(65, 56, 77), stand=(56, 56, 65), foot=(43, 43, 48)),
    'White': dict(bezel=(249, 249, 249), back=(232, 236, 240), back_dark=(198, 209, 216), stand=(170, 176, 186), foot=(150, 156, 166)),
}

def bow(x, w, depth):
    """Vertical offset of a gently curved edge: 0 at the ends, `depth` in the middle."""
    t = (x - w / 2) / (w / 2)
    return round(depth * (1 - t * t))

def front(c):
    im = Image.new('RGBA', (64, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in range(2, 62):                                   # curved panel: both edges bow up in the middle
        top, bottom = 5 + 2 - bow(x, 64, 2), 23 + 2 - bow(x, 64, 2)
        d.line([x, top, x, bottom], fill=c['bezel'])
        if 3 < x < 60: d.line([x, top + 2, x, bottom - 2], fill=SCREEN if 6 < x < 57 else SCREEN_DARK)
    d.rectangle([12, 10, 30, 19], fill=WINDOW); d.rectangle([12, 10, 30, 11], fill=WINDOW_GREY)
    d.rectangle([34, 9, 50, 16], fill=WINDOW_GREY); d.rectangle([36, 12, 48, 20], fill=WINDOW)
    d.rectangle([29, 25, 34, 28], fill=c['stand']); d.rectangle([22, 28, 41, 30], fill=c['foot'])
    return im

def back(c):
    im = Image.new('RGBA', (64, 32), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for x in range(2, 62):
        top, bottom = 5 + bow(x, 64, 2), 23 + bow(x, 64, 2)          # seen from behind the curve bows down
        d.line([x, top, x, bottom], fill=c['back'])
        d.point((x, bottom), fill=c['back_dark'])
    d.rectangle([24, 11, 39, 19], fill=c['back_dark'])                 # stand mount
    d.rectangle([29, 19, 34, 28], fill=c['stand']); d.rectangle([22, 28, 41, 30], fill=c['foot'])
    return im

def side(c, facing_left):
    im = Image.new('RGBA', (32, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for y in range(4, 56):                                   # thin panel, hollow towards the viewer (ends come forward)
        x = 14 + bow(y, 60, 3) if facing_left else 15 - bow(y, 60, 3)
        d.line([x, y, x + 3, y], fill=c['back'])
        d.point((x if facing_left else x + 3, y), fill=SCREEN)
    sx = 15
    d.rectangle([sx, 54, sx + 2, 59], fill=c['stand']); d.rectangle([sx - 5, 59, sx + 7, 61], fill=c['foot'])
    return im

for color, c in SKIN.items():
    front(c).save(f'CurvedScreen{color}Down.png')
    back(c).save(f'CurvedScreen{color}Up.png')
    side(c, True).save(f'CurvedScreen{color}Left.png')
    side(c, False).save(f'CurvedScreen{color}Right.png')
print('ok')
