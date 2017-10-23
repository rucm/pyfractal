import numpy as np
from numba import jit, guvectorize
from PIL import Image


# ------------------------------------ #
# Mandelbrot Set                       #
# ------------------------------------ #


@jit('Tuple((i8,f8))(c16, i8)', nopython=True)
def mandelbrot(c, steps):
    real, imag, nreal, z_abs = 0.0, 0.0, 0.0, 0.0
    for n in range(steps):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        z_abs = real * real + imag * imag
        if z_abs > 2.0:
            return n, z_abs
    return 0, z_abs


@guvectorize(
    ['(c16[:],i8[:],f8[:],f8[:])'],
    '(n),()->(n),(n)',
    target='parallel')
def mandelbrot_numpy(c, steps, out1, out2):
    _steps = steps[0]
    for i in range(c.shape[0]):
        out1[i], out2[i] = mandelbrot(c[i], _steps)


def mandelbrot_set(xmin, xmax, ymin, ymax, size, steps):
    r1 = np.linspace(xmin, xmax, size, dtype='f8')
    r2 = np.linspace(ymin, ymax, size, dtype='f8')
    c = r1 + r2[:, None] * 1j
    n3, n4 = mandelbrot_numpy(c, steps)
    return r1, r2, n3, n4


# ------------------------------------ #
# Julia Set                            #
# ------------------------------------ #


@jit('Tuple((i8,f8))(c16, c16, i8)', nopython=True)
def julia(z, c, steps):
    real, imag, nreal, z_abs = z.real, z.imag, 0.0, 0.0
    for n in range(steps):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        z_abs = real * real + imag * imag
        if z_abs > 4.0:
            return n, z_abs
    return 0, 0


@guvectorize(
    ['(c16[:],c16[:],i8[:],f8[:],f8[:])'],
    '(n),(),()->(n),(n)',
    target='parallel')
def julia_numpy(z, c, steps, out1, out2):
    steps = steps[0]
    _c = c[0]
    for i in range(z.shape[0]):
        out1[i], out2[i] = julia(z[i], _c, steps)


def julia_set(xmin, xmax, ymin, ymax, cx, cy, size, steps):
    r1 = np.linspace(xmin, xmax, size, dtype='f8')
    r2 = np.linspace(ymin, ymax, size, dtype='f8')
    z = r1 + r2[:, None] * 1j
    n3, n4 = julia_numpy(z, cx + cy * 1j, steps)
    return r1, r2, n3, n4


# ------------------------------------ #
# Image Generation                     #
# ------------------------------------ #


# Normalized with maximum value M and minimum value m
def min_max(data, M=1, m=0, axis=None):
    mn = data.min(axis=axis, keepdims=True)
    mx = data.max(axis=axis, keepdims=True)
    return (data - mn) / (mx - mn) * (M - m) + m


def create_image(size, h, s, v):
    image = Image.new('HSV', (size, size), (h, s, v))
    return image


def save_image(image, filename, filetype):
    img = image.convert('RGB')
    img.save(filename, filetype)


def cubic_bezier_curve(p1, p2, p3, p4, t):
    pass


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
    _, _, n, _ = julia_set(
        -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 400, 400, 256
    )

    n = min_max(n, 255, 0)

    image = create_image(400, 128, 255, 255)
    image = change_value(image, n)
    save_image(image, 'test.png', 'PNG')
