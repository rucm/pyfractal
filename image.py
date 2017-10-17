from PIL import Image
import numpy as np
from numba import jit, guvectorize, i4, c16
from fractal import julia_set, min_max


@guvectorize(
    ['(i4[:,:,:], i4[:,:],i4[:,:,:])'],
    '(n,m,p),(n,m)->(n,m,p)',
    target='parallel'
    )
def image_v(image, v, output):
    for i in range(v.shape[0]):
        for j in range(v.shape[1]):
            color = image[i, j]
            color[0], color[2] = v[i, j], v[i, j]
            output[i, j] = color


if __name__ == '__main__':
    from itertools import product
    import time

    size = 800
    _, _, n = julia_set(
        -1.5, 1.5, -1.5, 1.5, -0.3, -0.63, size, size, 1024
    )

    n = min_max(n) * 255
    n = n.astype(np.uint8)

    start = time.time()
    img = Image.new('RGB', (size, size), (128, 255, 255))
    img_tmp = np.asarray(img.convert('HSV'))
    img_tmp = image_v(img_tmp, n)
    img_tmp = Image.fromarray(np.uint8(img_tmp), mode='HSV')
    img = img_tmp.convert('RGB')
    t = time.time() - start
    print('time: {:0.3f}'.format(t))
    img.save('julia.png', 'PNG')
