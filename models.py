from PyQt5.QtCore import (
    Qt,
    QObject
)
from PyQt5.QtWidgets import (
    QGraphicsPixmapItem
)


class JuliaData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.graph = QGraphicsPixmapItem()

    def init_data(self, size, x, y, scale, cx, cy, loop):
        self.size = size
        self.x, self.y = x, y
        self.cx, self.cy = cx, cy
        self.loop = loop
        self.lower = -1.5 / scale
        self.upper = 1.5 / scale

    def calculate(self, h=None, s=None, v=None):
        from fractal import julia_set, min_max
        from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor
        import time
        from itertools import product

        start = time.time()
        _, _, n = julia_set(
            self.lower + self.x, self.upper + self.x,
            self.lower + self.y, self.upper + self.y,
            self.cx, self.cy,
            self.size, self.size,
            self.loop
        )

        n = min_max(n)

        image = QImage(self.size, self.size, QImage.Format_ARGB32)
        color = QColor()
        for i, j in product(range(self.size), range(self.size)):
            _h = n[i, j] if h is None else h
            _s = n[i, j] if s is None else s
            _v = n[i, j] if v is None else v
            color.setHsvF(_h, _s, _v)
            image.setPixelColor(i, j, color)
        self.graph.setPixmap(QPixmap.fromImage(image))
        return time.time() - start
