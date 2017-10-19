from PyQt5.QtCore import (
    Qt,
    QObject,
    QPointF
)
from PyQt5.QtWidgets import (
    QGraphicsPixmapItem
)


class FractalData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_default_data()
        self.image = None
        self.div = None
        self.z_abs = None
        self.item = QGraphicsPixmapItem()

    def set_default_data(self):
        self.use_h = 'default'
        self.use_s = 'default'
        self.use_v = 'div'
        self.h, self.s, self.v = 0.5, 1.0, 1.0
        self.cx, self.cy = 0.0, 0.0
        self.repeat_cnt = 256
        self.scale = 1.0
        self.size = 800
        self.xmin, self.xmax = -1.5, 1.5
        self.ymin, self.ymax = -1.5, 1.5

    def set_data(self, xmin, xmax, ymin, ymax):
        self.xmin, self.xmax = xmin, xmax
        self.ymin, self.ymax = ymin, ymax

    def set_size(self, size):
        self.size = size

    def set_scale(self, scale):
        self.scale = scale

    def set_repeat_cnt(self, repeat_cnt):
        self.repeat_cnt = repeat_cnt

    def set_constant(self, cx, cy):
        self.cx, self.cy = cx, cy

    def set_hsv(self, h, s, v):
        self.h, self.s, self.v = h, s, v

    # param list: default, div, z-abs
    def set_use_param(self, use_h='default', use_s='default', use_v='default'):
        self.use_h = use_h
        self.use_s = use_s
        self.use_v = use_v

    def calculate(self):
        import fractal
        _, _, self.div, self.z_abs = fractal.mandelbrot_set(
            self.xmin, self.xmax, self.ymin, self.ymax,
            self.size, self.size,
            self.repeat_cnt
        )
        self.div = fractal.min_max(self.div, 255, 0)
        self.z_abs = fractal.min_max(self.z_abs, 255, 0)
        self.image = fractal.create_image(self.size, self.h, self.s, self.v)
        if self.use_h == 'div':
            self.image = fractal.change_hue(self.image, self.div)
        elif self.use_h == 'z_abs':
            self.image = fractal.change_hue(self.image, self.z_abs)
        if self.use_s == 'div':
            self.image = fractal.change_saturation(self.image, self.div)
        elif self.use_s == 'z_abs':
            self.image = fractal.change_saturation(self.image, self.z_abs)
        if self.use_v == 'div':
            self.image = fractal.change_value(self.image, self.div)
        elif self.use_v == 'z_abs':
            self.image = fractal.change_value(self.image, self.z_abs)
        pixmap = fractal.to_qpixmap(self.image)
        self.item.setPixmap(pixmap)


class JuliaData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = QGraphicsPixmapItem()

    def init_data(self, size, x, y, scale, cx, cy, repeat_cnt):
        self.size = size
        self.x, self.y = x, y
        self.cx, self.cy = cx, cy
        self.repeat_cnt = repeat_cnt
        self.scale = scale
        self.lower = -1.5 / scale
        self.upper = 1.5 / scale

    def calculate(self, h=None, s=None, v=None):
        from fractal import julia_set, min_max, mandelbrot_set
        from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
        import time
        from itertools import product

        start = time.time()
        _, _, n, m = mandelbrot_set(
            self.lower + self.x, self.upper + self.x,
            self.lower + self.y, self.upper + self.y,
            self.size, self.size,
            self.repeat_cnt
        )

        n = min_max(n)
        m = min_max(m)

        image = QImage(self.size, self.size, QImage.Format_ARGB32)
        color = QColor()
        for i, j in product(range(self.size), range(self.size)):
            _h = m[i, j] if h is None else h
            _s = n[i, j] if s is None else s
            _v = n[i, j] if v is None else v
            color.setHsvF(_h, _s, _v)
            image.setPixelColor(i, j, color)
        self.graph.setPixmap(QPixmap.fromImage(image))
        return time.time() - start
