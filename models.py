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

    def set_default_data(self):
        self.x, self.y = 0.0, 0.0
        self.cx, self.cy = 0.0, 0.0
        self.loop = 256
        self.scale = 1.0
        self.size = 800
        self.xmin, self.xmax = -1.5, 1.5
        self.ymin, self.ymax = -1.5, 1.5


class JuliaData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = QGraphicsPixmapItem()

    def init_data(self, size, x, y, scale, cx, cy, loop):
        self.size = size
        self.x, self.y = x, y
        self.cx, self.cy = cx, cy
        self.loop = loop
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
            self.cx, self.cy,
            self.size, self.size,
            self.loop
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
