import sys
from PyQt5.QtGui import QPixmap 
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMainWindow,
    QPushButton,
    QDesktopWidget,
    QGridLayout
)

class MainScreen(QWidget):
    def __init__(self, width=1024, height=600):
        super().__init__()
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width, self.height = sizeObject.width() - 500, sizeObject.height() - 300
        self.loadUi()
        self.show()

    def loadUi(self):
        self.setWindowTitle("YTDownloader")
        self.resize(self.width, self.height)
        self.label = QLabel(self)
        self.label.setText("This is the movement")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.center()

    def center(self):
        """ Automatically center the window """
        qRectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        qRectangle.moveCenter(center)
        self.move(qRectangle.topLeft())