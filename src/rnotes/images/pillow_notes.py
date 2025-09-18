from PIL import Image, ImageDraw, ImageFont

im = Image.open("../../../tests/test_data/img/pillow_notes.png")
draw = ImageDraw.Draw(im)
print(im.format, im.size, im.mode)
