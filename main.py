import sys
import json
import random
from PyQt5.QtGui import QPixmap 
from typing import List, Union, Dict
from utils.convertbytes import convert
from utils.download import resolutions, video_description, download_video, download_playlist
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QVBoxLayout,
    QDialogButtonBox,
    QWidget,
    QLabel,
    QComboBox,
    QMainWindow,
    QPushButton,
    QDesktopWidget,
    QAction,
    QTableWidget,
    QHeaderView,
    QDialog,
    QTableWidgetItem,
    QToolBar,
    QProgressBar,
    QFormLayout,
    QLineEdit
)

progressBars = []
savedDownloads = []
class MainScreen(QMainWindow):
    def __init__(self, width: int =1024, height: int=600, parent=None):
        super(MainScreen, self).__init__(parent)
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width, self.height = sizeObject.width() - 500, sizeObject.height() - 300
        self._selectedRows= set()
        self.settings = QtCore.QSettings('Main', 'settings')
        self.loadUi()
        self.show()

    def loadUi(self):
        self.setWindowTitle("YTDownloader")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('./images/youtube.svg')))
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
        self.action_download = QAction("Download",self, triggered=lambda : self.download())
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

        self.action_pause.setEnabled(False)
        self.action_delete.setEnabled(False)

        self.actions_toolbar.addAction(self.action_download)
        self.actions_toolbar.addAction(self.action_pause)
        self.actions_toolbar.addAction(self.action_delete)
        self.actions_toolbar.addAction(self.action_options)
        self.actions_toolbar.addAction(self.action_schedule)

        self.table = DownloadsTable(self)
        self.table.cellClicked.connect(lambda row : self.updateSelectedRow(row))
        
        self.setCentralWidget(self.table)

        self.center()

    # Events and Signals 
    def pause(self):
        print("[PAUSED]")

    def download(self):
        dlg = self.table.dialog
        dlg.exec()

    def deleteDownload(self):
        self.table._deleteRow(2)
        self.action_pause.setEnabled(False)
        self.action_delete.setEnabled(False)

    def updateSelectedRow(self, row):
        self._selectedRows.add(row)
        self.action_pause.setEnabled(True)
        self.action_delete.setEnabled(True)

    def center(self):
        """ Automatically center the window """
        qRectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        qRectangle.moveCenter(center)
        self.move(qRectangle.topLeft())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        global savedDownloads
        self.settings.setValue("savedDownloads", json.dumps(savedDownloads))
        print("Closed")
        


        return super().closeEvent(a0)

class DownloadsTable(QTableWidget):
    def __init__(self, parent=None):
        super(DownloadsTable, self).__init__(0,5, parent)
        self.setHorizontalHeaderLabels(['File','Title','Size','Status','Description'])
        self.horizontalHeader().setDefaultSectionSize(150)
        self.horizontalHeader().setStretchLastSection(True)
        #self.setSelectionMode(QAbstractItemView.MultiSelection)
        self.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        self.restoreSavedDownloads()
        self.current = 0

        self.dialog = QDialog(self)
        self.url = {}
        self.mode = ""
        self.selectedMode = 0
        self.selectedResolution = 720
        self.modes = ["Download Youtube Video", "Download Youtube Playlist"]

        self.dialog.setMinimumWidth(400)
        self.dialog.setWindowTitle("Enter Youtube Video URL")
        self.dialog.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('./images/youtube.svg')))
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(lambda : self.submit())
        self.buttonBox.rejected.connect(lambda : self.dialog.close())
        self.buttonBox.setStyleSheet(
            'background-color: rgb(85, 85, 127);'+
            'color: #fff;'
        )

        self.selectMode = QComboBox()
        self.selectMode.addItems(self.modes)
        self.downloadForm = QFormLayout()
        self.downloadForm.addRow(self.selectMode)
        self.urlField = QLineEdit()
        self.downloadForm.addRow('Enter URL: ', self.urlField)
        # self.urlField.textEdited.connect(lambda x: self.url.append(x))
        self.selectResolution = QComboBox()
        self.selectResolution.addItems(list(map(lambda x: f"{str(x)}p", list(resolutions))))
        self.selectResolution.setCurrentIndex(4)
        self.selectResolution.activated.connect(lambda x: self._setSelectedResolution(x))
        self.selectMode.activated.connect(lambda x: self._setSelectedMode(x))
        
        self.downloadForm.addRow('Enter Resolution: ', self.selectResolution)
        self.dialog.layout = QVBoxLayout()
        self.dialog.layout.addLayout(self.downloadForm)
        self.dialog.layout.addWidget(self.buttonBox)
        self.dialog.setLayout(self.dialog.layout)
        
    def restoreSavedDownloads(self):
        global savedDownloads, progressBars
        settings = QtCore.QSettings('Main', 'settings')
        try:
            savedDownloads = list(json.loads(settings.value('savedDownloads', None)))
            for idx, d in enumerate(savedDownloads):
                print(idx, d)
                self.insertRow(idx)
                progressBar = QProgressBar(self)
                progressBar.setAlignment(QtCore.Qt.AlignCenter)
                progressBars.append(progressBar)
                self.setItem(idx , 0, QTableWidgetItem(d['file']))
                self.setItem(idx, 1, QTableWidgetItem(d['title']))
                self.setItem(idx, 2, QTableWidgetItem(d['filesize']))
                self.setItem(idx, 4, QTableWidgetItem(d['description']))
                progressBar.setValue(d['progress'])
                self.setCellWidget(idx,3, progressBar)
        except TypeError or ValueError:
            pass

    def _addRow(self, data: Dict, **kwargs):
        global progressBars
        global savedDownloads
        print(f'[PROCESS]: Adding a new row.')
        progressBar = QProgressBar(self)
        progressBar.setAlignment(QtCore.Qt.AlignCenter)
        rowCount = self.rowCount()
        print(rowCount)
        self.current = rowCount
        self.insertRow(rowCount)

        d = list(data.values())
        self.setItem(rowCount , 0, QTableWidgetItem(d[0]))
        self.setItem(rowCount, 1, QTableWidgetItem(d[1]))
        self.setItem(rowCount, 2, QTableWidgetItem(d[2]))
        self.setItem(rowCount, 4, QTableWidgetItem(d[4]))
        progressBar.setValue(0)
        self.setCellWidget(rowCount,3, progressBar)
        progressBars.append({
            'widget':progressBar,
            'progress':0
        })
        savedDownloads.append({
            'progress':0,
            'file':d[0],
            'title': d[1],
            'filesize': d[2],
            'description': d[4]
        })

    def _deleteRow(self, index):
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        self.removeRow(1)

    def _setSelectedMode(self, x):
        print(f'[SELECTED MODE]: {x}')
        self.selectedMode = int(x)

    def _setSelectedResolution(self, x):
        print(f'[SELECTED RESOLUTION]: {list(resolutions)[x]}p')
        self.selectedResolution = list(resolutions)[x]

    def submit(self):
        self.thread = QtCore.QThread()
        print(str(self.urlField.text()))
        print(self.selectedResolution)
        print(self.selectedMode)
        video_obj = video_description(self.urlField.text(), self.onDownloadProgress, self.onDownloadComplete)
        video = video_obj["streams"].filter(file_extension="mp4", resolution=f"{str(self.selectedResolution)}p")
        print(video[0].filesize)
        rowData = {
            'File': video_obj['title']+'.mp4',
            'Title': video_obj['title'],
            'Size': convert(video[0].filesize, metric=True),
            'Status': random.randint(0,100),
            'Description': video_obj['description']
        }
        # self.close()
        self._addRow(rowData)
        self.dialog.close()

        # Run the Download Thread
        self.downloadWorker = DownloadWorker(video_obj, resolution=self.selectedResolution)
        self.downloadWorker.moveToThread(self.thread)
        self.thread.started.connect(self.downloadWorker.run)
        self.downloadWorker.finished.connect(self.thread.quit)
        self.downloadWorker.finished.connect(self.downloadWorker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()


    # Download Callbacks 
    # @staticmethod
    def onDownloadProgress(self,stream, chunk, bytes_remaining):
        global progressBars
        print(self.current)
        total_size = stream.filesize 
        bytes_downloaded = total_size - bytes_remaining 
        percentage_of_completion = (bytes_downloaded / total_size) * 100
        print(f"[PERCENTAGE OF COMPLETION]: {round(percentage_of_completion)}")
        progressBars[self.current]['widget'].setValue(percentage_of_completion)
        savedDownloads[self.current]['progress'] = percentage_of_completion

    # @staticmethod 
    def onDownloadComplete(self,stream, filepath):
        print(f'[COMPLETED]: Saved in {filepath}')

class DownloadWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    def __init__(self, video_obj, resolution: int, parent=None):
        super(QtCore.QObject, self).__init__()
        self.video_obj = video_obj 
        self.resolution = resolution
    def run(self):
        download_video(self.video_obj, self.resolution)
        self.finished.emit()
