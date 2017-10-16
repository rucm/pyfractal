import numpy as np
from numba import jit, guvectorize, i8, c16


@jit(i8(c16, c16, i8), nopython=True)
def julia(z, c, loop):
    real, imag, nreal = z.real, z.imag, 0.0
    for n in range(loop):
        nreal = real * real - imag * imag + c.real
        imag = 2 * real * imag + c.imag
        real = nreal
        if real * real + imag * imag > 4.0:
            return n
    return 0


@guvectorize(
    [(c16[:], c16[:], i8[:], i8[:])],
    '(n),(),()->(n)',
    target='parallel')
def julia_numpy(z, c, loops, output):
    loop = loops[0]
    _c = c[0]
    for i in range(z.shape[0]):
        output[i] = julia(z[i], _c, loop)


def julia_set(xmin, xmax, ymin, ymax, cx, cy, width, height, loop):
    r1 = np.linspace(xmin, xmax, width, dtype='f8')
    r2 = np.linspace(ymin, ymax, height, dtype='f8')
    z = r1 + r2[:, None] * 1j
    n3 = julia_numpy(z, cx + cy * 1j, loop)

    return r1, r2, n3.T


def min_max(n, axis=None):
    min = n.min(axis=axis, keepdims=True)
    max = n.max(axis=axis, keepdims=True)
    return (n - min) / (max - min)

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
