import numpy as np


def bezier(p1, p2, p3, p4, t):
    _t = 1 - t
    b1 = _t * _t * _t * p1
    b2 = 3 * _t * _t * t * p2
    b3 = 3 * _t * t * t * p3
    b4 = t * t * t * p4
    return b1 + b2 + b3 + b4


if __name__ == '__main__':
    p1 = np.asarray([0, 0])
    p2 = np.asarray([0.5, 0])
    p3 = np.asarray([0.5, 1.0])
    p4 = np.asarray([1.0, 1.0])
    t = np.linspace(0, 1, 256, dtype='f8')
    for i in range(256):
        p = bezier(p1, p2, p3, p4, t[i])
        print('{}, {}, {}'.format(i, p[0], p[1]))
