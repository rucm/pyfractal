import numpy as np
from numba import jit


@jit('i8(f8,f8,f8,f8,i8)')
def julia(zx, zy, cx, cy, loop):
    x, y = zx, zy
    for n in range(loop):
        _zx = x * x
        _zy = y * y
        if _zx + _zy > 4:
            return n
        y = 2 * x * y + cy
        x = _zx - _zy + cx
    return 0


@jit('Tuple((f8[:],f8[:],f8[:,:]))(f8,f8,f8,f8,f8,f8,i8,i8,i8)', nopython=True)
def julia_set(xmin, xmax, ymin, ymax, cx, cy, width, height, loop):
    r1 = np.linspace(xmin, xmax, width)
    r2 = np.linspace(ymin, ymax, height)
    n3 = np.empty((width, height))
    for i in range(width):
        for j in range(height):
            n3[i, j] = julia(r1[i], r2[j], cx, cy, loop)

    return r1, r2, n3


def min_max(n, axis=None):
    min = n.min(axis=axis, keepdims=True)
    max = n.max(axis=axis, keepdims=True)
    return (n - min) / (max - min)

if __name__ == '__main__':
    from timeit import timeit
    preset = [
        '-2, 2, -2, 2, 0, 0, 400, 400, 256',
        '-2, 2, -2, 2, 0, 0, 400, 400, 2048',
        '-2, 2, -2, 2, 0, 0, 800, 800, 256',
        '-2, 2, -2, 2, 0, 0, 800, 800, 2048',
        '-1.5, 1.5, -1.5, 1.5, -0.3, -0.63, 2048, 2048, 256'
    ]
    for i, s in enumerate(preset):
        t = timeit('julia_set({})'.format(s), globals=globals(), number=1)
        print('preset {}: {:.3f}s'.format(i + 1, t))
