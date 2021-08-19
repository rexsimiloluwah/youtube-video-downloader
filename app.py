import sys
from PyQt5.QtGui import QPixmap, QColor 
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QMainWindow,
    QPushButton,
    QDesktopWidget,
    QGridLayout,
    QGraphicsDropShadowEffect
)
from splashscreen import SplashScreen
from main import MainScreen

# Global Variables 
counter = 0

class YtDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.splashscreen = SplashScreen()
        self.splashscreen.setupUi(self)

        ## Remove title bar 
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        ## Set Dropdown shadow effect
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(20)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 60))
        self.splashscreen.dropOutShadowFrame.setGraphicsEffect(self.shadow)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.progress)
        # Create a 20ms timer
        self.timer.start(20)

        # Dynamic modification of text 
        QtCore.QTimer.singleShot(1000, lambda: self.splashscreen.loading.setText("<strong>Welcome to YTDownloader</strong>"))
        QtCore.QTimer.singleShot(1500, lambda: self.splashscreen.loading.setText("Loading your downloads..."))

        self.show()

    def progress(self):
        global counter

        # set counter value to progress bar 
        self.splashscreen.progressBar.setValue(counter)
        if counter > 100:
            self.timer.stop()
            self.main = MainScreen()
            self.main.show()

            # close the splash screen
            self.close()

        counter += 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = YtDownloader()
    sys.exit(app.exec_())