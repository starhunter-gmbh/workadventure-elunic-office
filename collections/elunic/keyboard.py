"""Rotate the keyboard sprite into the four entity directions. Run from this directory.

KeyboardRight.png is the source (14x40, top view, space bar on the right = the user sits to the right);
Down/Left/Up are 90 degree steps of it.
"""
from PIL import Image

src = Image.open('KeyboardRight.png').convert('RGBA')
src.transpose(Image.Transpose.ROTATE_270).save('KeyboardDown.png')   # space bar to the bottom
src.transpose(Image.Transpose.ROTATE_180).save('KeyboardLeft.png')
src.transpose(Image.Transpose.ROTATE_90).save('KeyboardUp.png')
print('ok')
