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


__default_option = {
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


def create_pallette(option: dict):
    hue = option.get('hue', __default_option['hue'])
    h_range = [255 * hue['range'][0], 255 * hue['range'][1]]
    h = cubic_bezier(
        np.asarray(hue['easing']['p1']),
        np.asarray(hue['easing']['p2']))
    h = min_max_normalize(h, h_range[0], h_range[1]).astype(np.uint8)

    saturation = option.get('saturation', __default_option['saturation'])
    s_range = [255 * saturation['range'][0], 255 * saturation['range'][1]]
    s = cubic_bezier(
        np.asarray(saturation['easing']['p1']),
        np.asarray(saturation['easing']['p2']))
    s = min_max_normalize(s, s_range[0], s_range[1]).astype(np.uint8)

    brightness = option.get('brightness', __default_option['brightness'])
    b_range = [255 * brightness['range'][0], 255 * brightness['range'][1]]
    b = cubic_bezier(
        np.asarray(brightness['easing']['p1']),
        np.asarray(brightness['easing']['p2']))
    b = min_max_normalize(b, b_range[0], b_range[1]).astype(np.uint8)


# ------------------------------------ #
# Image Generation                     #
# ------------------------------------ #


def create_image(size, h, s, v):
    image = Image.new('HSV', (size, size), (h, s, v))
    return image


def save_image(image, filename, filetype):
    img = image.convert('RGB')
    img.save(filename, filetype)


@guvectorize(
    ['(i4[:,:,:],i4[:,:],i4[:],i4[:,:,:])'],
    '(n,m,p),(n,m),()->(n,m,p)',
    target='parallel')
def __change_color(image, d, indices, output):
    index = indices[0]
    for i in range(d.shape[0]):
        for j in range(d.shape[1]):
            color = image[i, j]
            color[index] = d[i, j]
            output[i, j] = color


def change_hue(image, data):
    d = data.astype(np.uint8)
    image_array = np.asarray(image)
    image_array = __change_color(image_array, d, 0)
    img = Image.fromarray(np.uint8(image_array), mode='HSV')
    return img


def change_saturation(image, data):
    d = data.astype(np.uint8)
    image_array = np.asarray(image)
    image_array = __change_color(image_array, d, 1)
    img = Image.fromarray(np.uint8(image_array), mode='HSV')
    return img


def change_value(image, data):
    d = data.astype(np.uint8)
    image_array = np.asarray(image)
    image_array = __change_color(image_array, d, 2)
    img = Image.fromarray(np.uint8(image_array), mode='HSV')
    return img


def to_qpixmap(image):
    from PIL import ImageQt
    img = image.convert('RGB')
    return ImageQt.toqpixmap(img)


if __name__ == '__main__':
    _, _, n = julia_set(
        -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 400, 256
    )

    n = min_max_normalize(n, 255, 0)

    image = create_image(400, 128, 255, 255)
    image = change_value(image, n)
    save_image(image, 'test.png', 'PNG')

    p1 = np.asarray([1.0, 1.0])
    p2 = np.asarray([0.0, 1.0])
    bezier = cubic_bezier(p1, p2)
    bezier = min_max_normalize(bezier, 0.5 * 255, 1.0 * 255)
    for b in bezier:
        print('{}, {}'.format(b[0], b[1]))
