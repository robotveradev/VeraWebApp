import math
from random import random
from PIL import Image, ImageDraw, ImageColor
from io import BytesIO
import ctypes
import base64
import logging

log = logging.getLogger('blockies')

DEFAULT_SIZE = 8
DEFAULT_SCALE = 4

DEFAULT_RANDSEED_LEN = 4


def zero_fill_right_shift(num, shift):
    if num < 0:
        num += 4294967296
    if num > 4294967295:
        num = int(bin(num)[-32:], 2)
    return num >> shift


def int32(num):
    return ctypes.c_int32(num).value


class Context:

    def __init__(self, seed, randseed_len=DEFAULT_RANDSEED_LEN):
        randseed = self.randseed = [0] * randseed_len
        for i in range(len(seed)):
            randseed[i % randseed_len] = int32(randseed[i % randseed_len] << 5) - randseed[i % randseed_len] + ord(
                seed[i])

    def rand(self):
        randseed = self.randseed
        t = int32(randseed[0] ^ (randseed[0] << 11))

        for i in range(0, len(randseed) - 1):
            randseed[i] = randseed[i + 1]

        idx = len(randseed) - 1
        randseed[idx] = int32(randseed[idx]) ^ (int32(randseed[idx]) >> 19) ^ t ^ (t >> 8)
        return zero_fill_right_shift(randseed[idx], 0) / zero_fill_right_shift((1 << 31), 0)

    def create_color(self):

        h = math.floor(self.rand() * 360)
        s = ((self.rand() * 60) + 40)
        l = ((self.rand() + self.rand() + self.rand() + self.rand()) * 25)
        # round percentages as PIL doesn't like them
        hsl = "hsl({},{}%,{}%)".format(h, round(s), round(l))
        try:
            return ImageColor.getrgb(hsl)
        except:
            log.exception("produced invalid color: {}".format(hsl))
            return (0, 0, 0)

    def create_image_data(self, size):
        width = size
        height = size

        data_width = math.ceil(width / 2)
        mirror_width = size - data_width

        data = []

        for y in range(0, height):
            row = [math.floor(self.rand() * 2.3) for _ in range(data_width)]
            r = row[:mirror_width]
            r.reverse()
            row.extend(r)
            data.extend(row)

        return data


def create(seed=None, color=None, bgcolor=None, size=DEFAULT_SIZE, scale=DEFAULT_SCALE, spotcolor=None, format='PNG'):
    seed = seed or hex(math.floor(random() * math.pow(10, 16)))
    ctx = Context(seed)
    color = color or ctx.create_color()
    if isinstance(color, str):
        color = ImageColor.getrgb(color)
    bgcolor = bgcolor or ctx.create_color()
    if isinstance(bgcolor, str):
        bgcolor = ImageColor.getrgb(bgcolor)
    spotcolor = spotcolor or ctx.create_color()
    if isinstance(spotcolor, str):
        spotcolor = ImageColor.getrgb(spotcolor)

    image_data = ctx.create_image_data(size)

    width = math.sqrt(len(image_data))
    width = int(width)
    render_size = width * scale
    image = Image.new('RGB', (render_size, render_size), bgcolor)
    draw = ImageDraw.Draw(image)

    for i, val in enumerate(image_data):
        if val == 0:
            continue

        row = i // width
        col = i % width

        fillcolor = color if val == 1 else spotcolor
        draw.rectangle(((col * scale, row * scale), (col * scale + scale, row * scale + scale)), fill=fillcolor)

    stream = BytesIO()
    image.save(stream, format=format, optimize=True)
    return stream.getvalue()


def png_to_data_uri(data):
    return "data:image/png;base64,{}".format(base64.b64encode(data).decode('ascii'))
