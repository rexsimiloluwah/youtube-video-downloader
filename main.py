import sys
import random
from PyQt5.QtGui import QPixmap 
from typing import List, Union, Dict
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QWidget,
    QLabel,
    QMainWindow,
    QPushButton,
    QDesktopWidget,
    QAction,
    QTableWidget,
    QHeaderView,
    QTableWidgetItem,
    QToolBar,
    QProgressBar
)

class MainScreen(QMainWindow):
    def __init__(self, width: int =1024, height: int=600, parent=None):
        super(MainScreen, self).__init__(parent)
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width, self.height = sizeObject.width() - 500, sizeObject.height() - 300
        self.loadUi()
        self.show()

    def loadUi(self):
        self.setWindowTitle("YTDownloader")
        self.resize(self.width, self.height)
        self.label = QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet('background-color:  rgb(229, 228, 240);')

        menu = self.menuBar()
        file_menu = menu.addMenu('File')
        downloads_menu = menu.addMenu('Downloads')
        settings_menu = menu.addMenu('Settings')
        about_menu = menu.addMenu('About')

        downloads_menu.addAction(
            'Pause All',
            self.pause,
            QtGui.QKeySequence('Ctrl+P')
        )

        downloads_menu.addAction(
            'Resume All',
            self.pause,
            QtGui.QKeySequence('Ctrl+R')
        )

        downloads_menu.addSeparator()
        downloads_menu.addAction(
            'View Downloads',
            self.pause,
        )

        downloads_menu.addAction(
            'Find',
            self.pause,
            QtGui.QKeySequence('Ctrl+F')
        )

        downloads_menu.addSeparator()
        downloads_menu.addAction(
            'Options',
            self.pause,
        )

        ## Toolbar 
        self.actions_toolbar = QToolBar('actions', self)
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.actions_toolbar)
        self.actions_toolbar.setIconSize(QtCore.QSize(48,48))
        self.actions_toolbar.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)

        download_icon = QtGui.QIcon(QtGui.QPixmap('./images/folder.svg'))
        self.action_download = QAction("Download",self, triggered=lambda : self.download({
            'File': 'Learn GO Programming For Absolute Beginners.mp4',
            'Title': 'Learn Go Programming for absolute beginners',
            'Size': 'Yes',
            'Status': random.randint(0,100),
            'Description': 'First Download'
        }))
        self.action_download.setIcon(download_icon)
        self.action_download.setIconText("Download")

        pause_icon = QtGui.QIcon(QtGui.QPixmap('./images/pause.svg'))
        self.action_pause = QAction(self)
        self.action_pause.setIcon(pause_icon)
        self.action_pause.setIconText("Pause")

        delete_icon = QtGui.QIcon(QtGui.QPixmap('./images/delete.svg'))
        self.action_delete = QAction("Delete Download", self, triggered=self.deleteDownload)
        self.action_delete.setIcon(delete_icon)
        self.action_delete.setIconText("Delete")

        options_icon = QtGui.QIcon(QtGui.QPixmap('./images/settings.svg'))
        self.action_options = QAction(self)
        self.action_options.setIcon(options_icon)
        self.action_options.setIconText("Options")

        schedule_icon = QtGui.QIcon(QtGui.QPixmap('./images/alarm-clock.svg'))
        self.action_schedule = QAction(self)
        self.action_schedule.setIcon(schedule_icon)
        self.action_schedule.setIconText("Schedule")

        self.actions_toolbar.addAction(self.action_download)
        self.actions_toolbar.addAction(self.action_pause)
        self.actions_toolbar.addAction(self.action_delete)
        self.actions_toolbar.addAction(self.action_options)
        self.actions_toolbar.addAction(self.action_schedule)
        
        self.table = DownloadsTable(self)
        self.setCentralWidget(self.table)

        self.center()

    # Events and Signals 
    def pause(self):
        print("[PAUSED]")

    def download(self, data):
        self.table._addRow(data)

    def deleteDownload(self):
        self.table._deleteRow(2)

    def center(self):
        """ Automatically center the window """
        qRectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        qRectangle.moveCenter(center)
        self.move(qRectangle.topLeft())

class DownloadsTable(QTableWidget):
    def __init__(self, parent=None):
        super(DownloadsTable, self).__init__(0,5, parent)
        self.setHorizontalHeaderLabels(['File','Title','Size','Status','Description'])
        self.horizontalHeader().setDefaultSectionSize(150)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

    def _addRow(self, data: Dict, **kwargs):
        progressBar = QProgressBar(self)
        progressBar.setAlignment(QtCore.Qt.AlignCenter)
        rowCount = self.rowCount()
        print(rowCount)
        self.insertRow(rowCount)

        d = list(data.values())
        self.setItem(rowCount , 0, QTableWidgetItem(d[0]))
        self.setItem(rowCount, 1, QTableWidgetItem(d[1]))
        self.setItem(rowCount, 2, QTableWidgetItem(d[2]))
        self.setItem(rowCount, 4, QTableWidgetItem(d[4]))
        progressBar.setValue(int(d[3]))
        self.setCellWidget(rowCount,3, progressBar)


    def _deleteRow(self, index):
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        self.removeRow(1)

    
