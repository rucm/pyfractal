from PyQt5.QtCore import (
    Qt,
    QTimer,
    QTimeLine,
    pyqtSlot
)
from PyQt5.QtWidgets import (
    QWidget,
    QMainWindow,
    QGraphicsView,
    QGraphicsScene
)
from PyQt5 import uic

from models import JuliaData


class View(QGraphicsView):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.scheduled_scalings = 0
        self.translate_scalings = 1.0
        self.can_move_scene = False
        self.old_pos = None

    def zoom(self, delta):
        degrees = int(delta / 8)
        steps = int(degrees / 15)
        self.scheduled_scalings += steps
        if self.scheduled_scalings * steps < 0:
            self.scheduled_scalings = steps
        anim = QTimeLine(350, self)
        anim.setUpdateInterval(20)
        anim.valueChanged.connect(self.scalingTime)
        anim.finished.connect(self.animFinished)
        anim.start()

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            self.zoom(event.angleDelta().y())
        elif event.modifiers() & Qt.ShiftModifier:
            v = self.horizontalScrollBar().value() - event.angleDelta().y()
            self.horizontalScrollBar().setValue(v)
        else:
            super().wheelEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.old_pos = event.localPos()
            self.can_move_scene = True
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.can_move_scene:
            delta = (event.localPos() - self.old_pos) / self.translate_scalings
            self.old_pos = event.localPos()
            self.translate(delta.x(), delta.y())

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        self.can_move_scene = False

    @pyqtSlot('qreal')
    def scalingTime(self, t):
        factor = 1.0 + self.scheduled_scalings / 300.0
        self.translate_scalings *= 1.0 + self.scheduled_scalings / 300.0
        old_pos = self.mapToScene(self.geometry().center())
        self.scale(factor, factor)
        new_pos = self.mapToScene(self.geometry().center())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())

    @pyqtSlot()
    def animFinished(self):
        if self.scheduled_scalings > 0:
            self.scheduled_scalings -= 1
        else:
            self.scheduled_scalings += 1
        self.sender().deleteLater()


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        Ui = uic.loadUiType('form.ui')[0]
        self.ui = Ui()
        self.ui.setupUi(self)
        self.scene = QGraphicsScene(self)
        self.ui.view.setScene(self.scene)

        self.julia_data = JuliaData()
        self.ui.run.clicked.connect(self.run)
        self.run()

    @pyqtSlot()
    def run(self):
        if self.julia_data.graph.scene() is not None:
            self.scene.removeItem(self.julia_data.graph)
        size = self.ui.size.value()
        x = self.ui.x.value()
        y = self.ui.y.value()
        scale = self.ui.scale.value()
        cx = self.ui.cx.value()
        cy = self.ui.cy.value()
        loop = self.ui.loop.value()
        h = None if self.ui.use_h.isChecked() else self.ui.h.value()
        s = None if self.ui.use_s.isChecked() else self.ui.s.value()
        v = None if self.ui.use_v.isChecked() else self.ui.v.value()
        self.julia_data.init_data(size, x, y, scale, cx, cy, loop)
        t = self.julia_data.calculate(h, s, v)
        self.scene.addItem(self.julia_data.graph)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.ui.processing_time.setText('{:.5f}s'.format(t))
