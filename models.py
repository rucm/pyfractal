from PyQt5.QtCore import (
    Qt,
    QObject
)
import numpy as np


class JuliaData(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_data(400, 1, 0, 0, 256)

    def init_data(self, size, cx, cy, loop):
        self.size = size
        self.cx, self.cy = cx, cy
        self.loop = loop
        self.lower = -2.0 / self.size
        self.upper = 2.0 / self.size

    def calcurate(self):
        pass
