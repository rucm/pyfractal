import numpy as np
from numba import jit, guvectorize
from PIL import Image


# ------------------------------------ #
# Mandelbrot Set                       #
# ------------------------------------ #


@jit('i8(c16, i8)', nopython=True)
def __mandelbrot(c, steps):
    real, imag, nreal = 0.0, 0.0, 0.0
    for n in range(steps):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        if real * real + imag * imag > 4.0:
            return n
    return 0


@guvectorize(
    ['(c16[:],i8[:],f8[:])'],
    '(n),()->(n)',
    target='parallel')
def __mandelbrot_numpy(c, steps, output):
    _steps = steps[0]
    for i in range(c.shape[0]):
        output[i] = __mandelbrot(c[i], _steps)


def mandelbrot_set(xmin, xmax, ymin, ymax, size, steps):
    r1 = np.linspace(xmin, xmax, size, dtype='f8')
    r2 = np.linspace(ymin, ymax, size, dtype='f8')
    c = r1 + r2[:, None] * 1j
    n = __mandelbrot_numpy(c, steps)
    n = min_max_normalize(n, 0, 255).astype(np.uint8)
    return r1, r2, n


# ------------------------------------ #
# Julia Set                            #
# ------------------------------------ #


@jit('i8(c16, c16, i8)', nopython=True)
def __julia(z, c, steps):
    real, imag, nreal = z.real, z.imag, 0.0
    for n in range(steps):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        if real * real + imag * imag > 4.0:
            return n
    return 0


@guvectorize(
    ['(c16[:],c16[:],i8[:],f8[:])'],
    '(n),(),()->(n)',
    target='parallel')
def __julia_numpy(z, c, steps, output):
    steps = steps[0]
    _c = c[0]
    for i in range(z.shape[0]):
        output[i] = __julia(z[i], _c, steps)


def julia_set(xmin, xmax, ymin, ymax, cx, cy, size, steps):
    r1 = np.linspace(xmin, xmax, size, dtype='f8')
    r2 = np.linspace(ymin, ymax, size, dtype='f8')
    z = r1 + r2[:, None] * 1j
    n = __julia_numpy(z, cx + cy * 1j, steps)
    n = min_max_normalize(n, 0, 255).astype(np.uint8)
    return r1, r2, n


# ------------------------------------ #
# Easing                               #
# ------------------------------------ #


class Easing(object):

    @staticmethod
    def MethodList():
        import re
        list = dir(Easing())
        r = re.compile('(Fixed|Linear|In|Out)')
        return [x for x in list if r.match(x)]

    @staticmethod
    def Calc(name: str, t: float, total: float, mx: float, mn: float):
        return getattr(Easing, name)(t, total, mx, mn)

    @staticmethod
    def Fixed(t: float, total: float, mx: float, mn: float):
        return mx

    @staticmethod
    def InQuad(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        return dif * _t * _t + mn

    @staticmethod
    def OutQuad(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        return -dif * _t * (_t - 2) + mn

    @staticmethod
    def InOutQuad(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        if _t / 2 < 1:
            return dif / 2 * _t * _t + mn
        _t -= 1
        return -dif * (_t * (_t - 2) - 1) + mn

    @staticmethod
    def InCubic(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        return dif * _t * _t * _t + mn

    @staticmethod
    def OutCubic(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total - 1
        return dif * (_t * _t * _t + 1) + mn

    @staticmethod
    def InOutCubic(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        if _t / 2 < 1:
            return dif / 2 * _t * _t * _t + mn
        _t -= 2
        return dif / 2 * (_t * _t * _t + 2) + mn

    @staticmethod
    def InQuart(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        return dif * _t * _t * _t * _t + mn

    @staticmethod
    def OutQuart(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total - 1
        return -dif * (_t * _t * _t * _t - 1) + mn

    @staticmethod
    def InOutQuart(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        if _t / 2 < 1:
            return dif / 2 * _t * _t * _t * _t + mn
        _t -= 2
        return -dif / 2 * (_t * _t * _t * _t - 2) + mn

    @staticmethod
    def InQuint(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        return dif * _t * _t * _t * _t * _t + mn

    @staticmethod
    def OutQuint(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total - 1
        return dif * (_t * _t * _t * _t * _t + 1) + mn

    @staticmethod
    def InOutQuint(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        if _t / 2 < 1:
            return dif / 2 * _t * _t * _t * _t * _t + mn
        _t -= 2
        return dif / 2 * (_t * _t * _t * _t * _t + 2) + mn

    @staticmethod
    def InSine(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        return -dif * np.cos(t * np.radians(90) / total) + mx

    @staticmethod
    def OutSine(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        return dif * np.sin(t * np.radians(90) / total) + mn

    @staticmethod
    def InOutSine(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        return -dif / 2 * (np.cos(t * np.pi / total) - 1) + mn

    @staticmethod
    def InExp(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        if t == 0.0:
            return mn
        return dif * np.power(2, 10 * (t / total - 1)) + mn

    @staticmethod
    def OutExp(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        if t == total:
            return mx
        return dif * (-np.power(2, -10 * t / total) + 1) + mn

    @staticmethod
    def InOutExp(t: float, total: float, mx: float, mn: float):
        if t == 0.0:
            return mn
        elif t == total:
            return mx
        dif = mx - mn
        _t = t / total
        if _t / 2 < 1:
            return dif / 2 * np.power(2, 10 * (_t - 1)) + mn
        _t -= 1
        return dif / 2 * (-np.power(2, -10 * _t) + 2) + mn

    @staticmethod
    def InCirc(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        return -dif * (np.sqrt(1 - _t * _t) - 1) + mn

    @staticmethod
    def OutCirc(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total - 1
        return dif * np.sqrt(1 - _t * _t) + mn

    @staticmethod
    def InOutCirc(t: float, total: float, mx: float, mn: float):
        dif = mx - mn
        _t = t / total
        if _t / 2 < 1:
            return -dif / 2 * (np.sqrt(1 - _t * _t) - 1) + mn
        _t -= 2
        return dif / 2 * (np.sqrt(1 - _t * _t) + 1) + mn

    @staticmethod
    def Linear(t: float, total: float, mx: float, mn: float):
        return (mx - mn) * t / total + mn


# ------------------------------------ #
# Utility                              #
# ------------------------------------ #


def min_max_normalize(data, m=0, M=1, axis=None):
    mn = data.min(axis=axis, keepdims=True)
    mx = data.max(axis=axis, keepdims=True)
    return (data - mn) / (mx - mn) * (M - m) + m


__default = {
    'hue': {
        'range': [0.2, 1.0],
        'easing': 'OutExp'
    },
    'saturation': {
        'range': [1.0, 0.0],
        'easing': 'OutExp'
    },
    'brightness': {
        'range': [1.0, 0.0],
        'easing': 'Fixed'
    }
}


def create_palette(option: dict=__default):
    hue = option.get('hue', __default['hue'])
    saturation = option.get('saturation', __default['saturation'])
    brightness = option.get('brightness', __default['brightness'])
    palette = np.zeros((256, 3))
    for i in range(256):
        h = Easing.Calc(
            hue['easing'], i, 256,
            255 * hue['range'][0], 255 * hue['range'][1])
        s = Easing.Calc(
            saturation['easing'], i, 256,
            255 * saturation['range'][0], 255 * saturation['range'][1])
        b = Easing.Calc(
            brightness['easing'], i, 256,
            255 * brightness['range'][0], 255 * brightness['range'][1])
        palette[i] = (h, s, b)
    return palette.astype(np.uint8)


# ------------------------------------ #
# Image Generation                     #
# ------------------------------------ #


@guvectorize(
    ['(i8[:,:],i8[:,:],i8[:,:,:])'],
    '(n,m),(p,o)->(n,m,o)',
    target='parallel')
def __apply_palette(data, palette, output):
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            output[i, j] = palette[data[i, j]]


def create_image(data, palette):
    image = __apply_palette(data, palette)
    image = Image.fromarray(np.uint8(image), mode='HSV')
    return image.convert('RGB')


def image_of_palette(palette):
    data = np.zeros((1, 256, 3))
    data[0] = palette
    image = Image.fromarray(np.uint8(data), mode='HSV')
    return image.convert('RGB')


if __name__ == '__main__':
    _, _, data = julia_set(
        -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 4000, 1000
    )

    palette = create_palette()
    data = min_max_normalize(data, 0, 255).astype(np.uint8)
    image = create_image(data, palette)
    image.save('julia.png', 'PNG')
