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
        self.image = None
        self.div = None
        self.z_abs = None
        self.item = QGraphicsPixmapItem()

    def set_param(self, x, y, scale, cx, cy, steps):
        self.xmin = -1.5 / scale + x
        self.xmax = 1.5 / scale + x
        self.ymin = -1.5 / scale + y
        self.ymax = 1.5 / scale + y
        self.scale = scale
        self.cx, self.cy = cx, cy
        self.steps = int(steps)

    def set_image_param(self, size, h, s, v):
        self.size = size
        self.h, self.s, self.v = h, s, v

    def select_data(self, use_h, use_s, use_v):
        self.use_h, self.use_s, self.use_v = use_h, use_s, use_v

    def save(self, filename):
        import fractal
        fractal.save_image(self.image, filename, 'PNG')

    def calculate(self, fractal_type):
        import time
        import fractal
        start = time.time()
        if fractal_type == 'mandelbrot':
            _, _, self.divergence, self.z_abs = fractal.mandelbrot_set(
                self.xmin, self.xmax, self.ymin, self.ymax,
                self.size, self.size,
                self.steps
            )
        elif fractal_type == 'julia':
            _, _, self.divergence, self.z_abs = fractal.julia_set(
                self.xmin, self.xmax, self.ymin, self.ymax,
                self.cx, self.cy,
                self.size, self.size,
                self.steps
            )
        self.divergence = fractal.min_max(self.divergence, 255, 0)
        self.z_abs = fractal.min_max(self.z_abs, 255, 0)
        self.image = fractal.create_image(self.size, self.h, self.s, self.v)
        if self.use_h == 'divergence':
            self.image = fractal.change_hue(self.image, self.divergence)
        elif self.use_h == 'z_abs':
            self.image = fractal.change_hue(self.image, self.z_abs)
        if self.use_s == 'divergence':
            self.image = fractal.change_saturation(self.image, self.divergence)
        elif self.use_s == 'z_abs':
            self.image = fractal.change_saturation(self.image, self.z_abs)
        if self.use_v == 'divergence':
            self.image = fractal.change_value(self.image, self.divergence)
        elif self.use_v == 'z_abs':
            self.image = fractal.change_value(self.image, self.z_abs)
        pixmap = fractal.to_qpixmap(self.image)
        self.item.setPixmap(pixmap)
        return time.time() - start
