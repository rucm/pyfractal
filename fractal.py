import numpy as np
from numba import jit, guvectorize


# ------------------------------------ #
# Mandelbrot Set                       #
# ------------------------------------ #


@jit('Tuple((i8,f8))(c16, i8)', nopython=True)
def mandelbrot(c, loop):
    real, imag, nreal, zabs = 0.0, 0.0, 0.0, 0.0
    for n in range(loop):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        zabs = real * real + imag * imag
        if zabs > 2.0:
            return n, zabs
    return 0, zabs


@guvectorize(
    ['(c16[:],i8[:],f8[:],f8[:])'],
    '(n),()->(n),(n)',
    target='parallel')
def mandelbrot_numpy(c, loops, out1, out2):
    loop = loops[0]
    for i in range(c.shape[0]):
        out1[i], out2[i] = mandelbrot(c[i], loop)


def mandelbrot_set(xmin, xmax, ymin, ymax, cx, cy, width, height, loop):
    r1 = np.linspace(xmin, xmax, width, dtype='f8')
    r2 = np.linspace(ymin, ymax, height, dtype='f8')
    c = r1 + r2[:, None] * 1j
    n3, n4 = mandelbrot_numpy(c, loop)
    return r1, r2, n3.T, n4.T


# ------------------------------------ #
# Julia Set                            #
# ------------------------------------ #


@jit('Tuple((i8,f8))(c16, c16, i8)', nopython=True)
def julia(z, c, loop):
    real, imag, nreal, zabs = z.real, z.imag, 0.0, 0.0
    for n in range(loop):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        zabs = real * real + imag * imag
        if zabs > 4.0:
            return n, zabs
    return 0, 0


@guvectorize(
    ['(c16[:],c16[:],i8[:],f8[:],f8[:])'],
    '(n),(),()->(n),(n)',
    target='parallel')
def julia_numpy(z, c, loops, out1, out2):
    loop = loops[0]
    _c = c[0]
    for i in range(z.shape[0]):
        out1[i], out2[i] = julia(z[i], _c, loop)


def julia_set(xmin, xmax, ymin, ymax, cx, cy, width, height, loop):
    r1 = np.linspace(xmin, xmax, width, dtype='f8')
    r2 = np.linspace(ymin, ymax, height, dtype='f8')
    z = r1 + r2[:, None] * 1j
    n3, n4 = julia_numpy(z, cx + cy * 1j, loop)
    return r1, r2, n3.T, n4.T


# Normalized with maximum value M and minimum value m
def min_max(data, M=1, m=0, axis=None):
    mn = data.min(axis=axis, keepdims=True)
    mx = data.max(axis=axis, keepdims=True)
    return (data - mn) / (mx - mn) * (M - m) + m


def create_image(data):
    pass


if __name__ == '__main__':
    from timeit import timeit
    preset = [
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 400, 400, 256',
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 400, 400, 2048',
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 800, 800, 256',
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 800, 800, 2048',
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 2048, 2048, 256',
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 2048, 2048, 2048'
    ]
    for i, s in enumerate(preset):
        t = timeit('julia_set({})'.format(s), globals=globals(), number=1)
        print('preset {}: {:.3f}s'.format(i + 1, t))
