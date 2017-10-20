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
    QGraphicsScene,
    QFileDialog
)
from PyQt5 import uic

from models import FractalData


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
            self.set_rect.emit(self.graph.rect())
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

        self.ui.fractal_type.addItem('mandelbrot')
        self.ui.fractal_type.addItem('julia')

        self.fractal_data = FractalData()
        self.ui.run.clicked.connect(self.run)
        self.ui.reset.clicked.connect(self.reset)
        self.ui.save.clicked.connect(self.save)
        self.run()

    @pyqtSlot()
    def run(self):
        if self.fractal_data.item.scene() is not None:
            self.scene.removeItem(self.fractal_data.item)
        self.fractal_data.set_param(
            self.ui.x.value(), self.ui.y.value(),
            self.ui.scale.value(),
            self.ui.cx.value(), self.ui.cy.value(),
            self.ui.repeat_cnt.value()
        )
        self.fractal_data.set_image_param(
            self.ui.size.value(),
            self.ui.h.value(), self.ui.s.value(), self.ui.v.value()
        )
        self.fractal_data.select_data(
            self.ui.use_h.checkedButton().text(),
            self.ui.use_s.checkedButton().text(),
            self.ui.use_v.checkedButton().text()
        )
        t = self.fractal_data.calculate(self.ui.fractal_type.currentText())
        self.scene.addItem(self.fractal_data.item)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.ui.processing_time.setText('{:.5f}s'.format(t))

    @pyqtSlot()
    def reset(self):
        self.ui.fractal_type.setCurrentIndex(0)
        self.ui.x.setValue(0.0)
        self.ui.y.setValue(0.0)
        self.ui.scale.setValue(1.0)
        self.ui.cx.setValue(-0.8)
        self.ui.cy.setValue(0.16)
        self.ui.repeat_cnt.setValue(256)
        self.ui.size.setValue(800)
        self.ui.h.setValue(127)
        self.ui.s.setValue(255)
        self.ui.v.setValue(255)
        self.ui.h_default.setChecked(True)
        self.ui.s_default.setChecked(True)
        self.ui.v_divergence.setChecked(True)

    @pyqtSlot()
    def save(self):
        filename = QFileDialog.getSaveFileName(
            self,
            'Save',
            '',
            'png (*.png)'
        )[0]
        if filename != '':
            self.fractal_data.save(filename)

    @pyqtSlot('QRectF')
    def set_rect(self, rect):
        if rect.width() == 0.0:
            return
        origin = self.fractal_data.item.boundingRect()
        rect = self.fractal_data.item.mapRectFromScene(rect)
        scale = origin.width() / rect.width()
        dif = self.fractal_data.xmax - self.fractal_data.xmin
        center = rect.center() / origin.width() * dif
        self.ui.scale.setValue(self.fractal_data.scale * scale)
        self.ui.x.setValue(center.x() + self.fractal_data.xmin)
        self.ui.y.setValue(center.y() + self.fractal_data.ymin)
