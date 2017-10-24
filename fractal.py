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
    return r1, r2, n


# ------------------------------------ #
# Utility                              #
# ------------------------------------ #


def min_max_normalize(data, m=0, M=1, axis=None):
    mn = data.min(axis=axis, keepdims=True)
    mx = data.max(axis=axis, keepdims=True)
    return (data - mn) / (mx - mn) * (M - m) + m


@guvectorize(
    ['(f8[:],f8[:],f8[:],f8[:],f8[:],f8[:,:])'],
    '(n),(n),(n),(n),(m)->(m,n)',
    target='parallel')
def __cubic_bezier_vec(p1, p2, p3, p4, rates, output):
    for i in range(rates.shape[0]):
        t = rates[i]
        _t = 1 - t
        b1 = _t * _t * _t * p1
        b2 = 3 * _t * _t * t * p2
        b3 = 3 * _t * t * t * p3
        b4 = t * t * t * p4
        output[i] = b1 + b2 + b3 + b4


def cubic_bezier(p1, p2):
    begin = np.asarray([0.0, 0.0])
    end = np.asarray([1.0, 1.0])
    rates = np.linspace(0, 1, 256, dtype='f8')
    return __cubic_bezier_vec(begin, p1, p2, end, rates)


__default = {
    'hue': {
        'range': [0.5, 0.5],
        'easing': {
            'p1': [0.5, 0.5],
            'p2': [0.5, 0.5]
        }
    },
    'saturation': {
        'range': [1.0, 1.0],
        'easing': {
            'p1': [0.5, 0.5],
            'p2': [0.5, 0.5]
        }
    },
    'brightness': {
        'range': [0.0, 1.0],
        'easing': {
            'p1': [0.5, 0.5],
            'p2': [0.5, 0.5]
        }
    }
}


def __palette_param(option: dict):
    palette_range = [option['range'][0] * 255, option['range'][1] * 255]
    palette = cubic_bezier(
        np.asarray(option['easing']['p1']),
        np.asarray(option['easing']['p2'])
    )
    palette = min_max_normalize(
        palette,
        palette_range[0],
        palette_range[1])
    print(type(palette))
    return palette.astype(np.uint8)


@jit('void(i8[:,:],i8[:],i8[:],i8[:])', nopython=True)
def __create_palette_vec(palette, h, s, b):
    for i in range(palette.shape[0]):
        palette[i] = (h[i], s[i], b[i])


def create_palette(option: dict=__default):
    h = __palette_param(option.get('hue', __default['hue']))
    s = __palette_param(option.get('saturation', __default['saturation']))
    b = __palette_param(option.get('brightness', __default['brightness']))
    palette = np.asarray(np.zeros((256, 3))).astype(np.uint8)
    print(type(palette))
    __create_palette_vec(palette, h, s, b)
    return palette


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


def to_qpixmap(image):
    from PIL import ImageQt
    img = image.convert('RGB')
    return ImageQt.toqpixmap(img)


if __name__ == '__main__':
    _, _, data = julia_set(
        -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 400, 256
    )

    palette = create_palette()
    data = min_max_normalize(data, 0, 255).astype(np.uint8)
    image = create_image(data, palette)
    image.save('test-julia.png', 'PNG')
