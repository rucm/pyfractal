import os
import sys
import logging

from PyQt5.QtWidgets import QApplication
from widgets import MainWindow


logging.basicConfig(
    filename='output.log',
    filemode='w',
    level=logging.DEBUG,
    format='%(asctime)s:%(filename)s:%(lineno)d:%(message)s'
)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
