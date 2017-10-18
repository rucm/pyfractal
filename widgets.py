from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QTimer,
    QTimeLine,
    pyqtSlot,
    pyqtSignal
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


class Scene(QGraphicsScene):

    set_rect = pyqtSignal('QRectF')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.center = None
        self.graph = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.center = event.scenePos()
            rect = QRectF()
            self.graph = self.addRect(
                QRectF(self.center, self.center),
                Qt.white)

    def mouseMoveEvent(self, event):
        if self.center is not None:
            p = event.scenePos() - self.center
            p = QPointF(p.x(), p.x())
            rect = QRectF(
                self.center - p,
                self.center + p
            )
            self.graph.setRect(rect)

    def mouseReleaseEvent(self, event):
        if self.center is not None:
            # self.set_rect.emit(self.graph.rect())
            self.removeItem(self.graph)
            self.center = None
            self.graph = None


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        Ui = uic.loadUiType('form.ui')[0]
        self.ui = Ui()
        self.ui.setupUi(self)
        self.scene = Scene(self)
        self.ui.view.setScene(self.scene)
        self.scene.set_rect.connect(self.set_rect)

        self.ui.use_h.setId(self.ui.hp, 0)
        self.ui.use_h.setId(self.ui.hd, 1)
        self.ui.use_h.setId(self.ui.hz, 2)
        self.ui.use_s.setId(self.ui.sp, 0)
        self.ui.use_s.setId(self.ui.sd, 1)
        self.ui.use_s.setId(self.ui.sz, 2)
        self.ui.use_v.setId(self.ui.vp, 0)
        self.ui.use_v.setId(self.ui.vd, 1)
        self.ui.use_v.setId(self.ui.vz, 2)

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
        h = None if self.ui.use_h.checkedId() == 1 else self.ui.h.value()
        s = None if self.ui.use_s.checkedId() == 1 else self.ui.s.value()
        v = None if self.ui.use_v.checkedId() == 1 else self.ui.v.value()
        self.julia_data.init_data(size, x, y, scale, cx, cy, loop)
        t = self.julia_data.calculate(h, s, v)
        self.scene.addItem(self.julia_data.graph)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.ui.processing_time.setText('{:.5f}s'.format(t))

    @pyqtSlot('QRectF')
    def set_rect(self, rect):
        origin = self.julia_data.graph.boundingRect()
        rect = self.julia_data.graph.mapRectFromScene(rect)
        c = (rect.center() - origin.center()) / origin.width() * 3.0
        self.ui.x.setValue(c.x())
        self.ui.y.setValue(c.y())
