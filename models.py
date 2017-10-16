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
        self.init_data(800, -0.8, 0.156, 256)

    def init_data(self, size, cx, cy, loop):
        self.size = size
        self.cx, self.cy = cx, cy
        self.loop = loop
        self.lower = -1.5
        self.upper = 1.5
        self.graph = QGraphicsPixmapItem()

    def calcurate(self):
        from fractal import julia_set, min_max
        from PyQt5.QtGui import QImage, QPixmap, QPainter, QColor

        _, _, n = julia_set(
            self.lower, self.upper,
            self.lower, self.upper,
            self.cx, self.cy,
            self.size, self.size,
            self.loop
        )

        n = min_max(n)

        image = QImage(self.size, self.size, QImage.Format_ARGB32)
        from itertools import product
        for i, j in product(range(self.size), range(self.size)):
            color = QColor()
            color.setHsvF(0.5, 1.0, n[i, j])
            image.setPixelColor(i, j, color)
        image.save('fractal.png')
        self.graph.setPixmap(QPixmap.fromImage(image))
