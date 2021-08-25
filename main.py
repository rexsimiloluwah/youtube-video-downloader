# @author [Similoluwa Okunowo]
# @email [rexsimiloluwa@gmail.com]
# @create date 2021-08-25 20:30:50
# @modify date 2021-08-25 20:30:50
# @desc [Main app UI and logic for the Youtube Downloader GUI]


import json
import random
from typing import List, Dict
from utils.convertbytes import convert
from PyQt5 import QtWidgets, QtGui, QtCore
from utils.download import resolutions, video_description, download_video, download_playlist

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialogButtonBox,
    QLabel,
    QComboBox,
    QMainWindow,
    QDesktopWidget,
    QAction,
    QTableWidget,
    QDialog,
    QTableWidgetItem,
    QToolBar,
    QProgressBar,
    QFormLayout,
    QLineEdit
)

## Global Variables 
progress_bars = []
saved_downloads = []

## MainWindow 
class MainScreen(QMainWindow):
    def __init__(self, width: int =1024, height: int=600, parent=None):
        super(MainScreen, self).__init__(parent)
        sizeObject = QtWidgets.QDesktopWidget().screenGeometry(-1)
        self.width, self.height = sizeObject.width() - 500, sizeObject.height() - 300
        self.selected_rows= set()
        self.settings = QtCore.QSettings('Main', 'settings')
        self.load_ui()
        self.show()

    def load_ui(self):
        """ Loads the Main UI """
        self.setWindowTitle("YTDownloader")
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('./images/youtube.svg')))
        self.resize(self.width, self.height)
        self.label = QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet('background-color:  rgb(229, 228, 240);')

        # Add Menubars and menu actions
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

        # Toolbar actions (with Icons)
        download_icon = QtGui.QIcon(QtGui.QPixmap('./images/folder.svg'))
        self.action_download = QAction("Download",self, triggered=lambda : self.download())
        self.action_download.setIcon(download_icon)
        self.action_download.setIconText("Download")

        pause_icon = QtGui.QIcon(QtGui.QPixmap('./images/pause.svg'))
        self.action_pause = QAction(self)
        self.action_pause.setIcon(pause_icon)
        self.action_pause.setIconText("Pause")

        delete_icon = QtGui.QIcon(QtGui.QPixmap('./images/delete.svg'))
        self.action_delete = QAction("Delete Download", self, triggered=self.delete_download)
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

        # Update selected row on cell click event
        self.table = DownloadsTable(self)
        self.table.cellClicked.connect(lambda row : self.update_selected_row(row))
        
        self.setCentralWidget(self.table)

        self.center()

    # Events and Signals 
    def pause(self):
        print("[PAUSED]")
        pass

    def download(self):
        """ Opens the Download form dialog """
        dlg = self.table.dialog
        dlg.exec()

    def delete_download(self):
        """ Delete a selected download """
        self.table.delete_row(2)
        self.action_pause.setEnabled(False)
        self.action_delete.setEnabled(False)

    def update_selected_row(self, row):
        """ Update selected row """
        self.selected_rows.add(row)
        self.action_pause.setEnabled(True)
        self.action_delete.setEnabled(True)

    def center(self):
        """ Automatically center the window """
        qRectangle = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        qRectangle.moveCenter(center)
        self.move(qRectangle.topLeft())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """ Event when the GUI is closed """
        global saved_downloads
        self.settings.setValue("savedDownloads", json.dumps(saved_downloads))
        print("Closed")
        return super().closeEvent(a0)

## Widget for displaying downloads and download progress
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

        self.restore_saved_downloads()
        self.current = 0
        self.dialog = QDialog(self)
        self.url = {}
        self.mode = ""
        self.selected_mode = 0  #default mode
        self.selected_resolution = 720 #default resolution
        self.modes = ["Download Youtube Video", "Download Youtube Playlist"]
        self.dialog.setMinimumWidth(400)
        self.dialog.setWindowTitle("Enter Youtube Video URL")
        self.dialog.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('./images/youtube.svg')))
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(lambda : self.submit())
        self.button_box.rejected.connect(lambda : self.dialog.close())
        self.button_box.setStyleSheet(
            'background-color: rgb(85, 85, 127);'+
            'color: #fff;'
        )

        ## Select mode ComboBox Widget
        self.select_mode = QComboBox()
        self.select_mode.addItems(self.modes)

        ## Download form
        self.download_form = QFormLayout()
        self.download_form.addRow(self.select_mode)
        self.url_field = QLineEdit()
        self.download_form.addRow('Enter URL: ', self.url_field)
        # self.url_field.textEdited.connect(lambda x: self.url.append(x))

        ## Select resolution ComboBox Widget
        self.select_resolution = QComboBox()
        self.select_resolution.addItems(list(map(lambda x: f"{str(x)}p", list(resolutions))))
        self.select_resolution.setCurrentIndex(4)
        self.select_resolution.activated.connect(lambda x: self.set_selected_resolution(x))
        self.select_mode.activated.connect(lambda x: self.set_selected_mode(x))

        self.download_form.addRow('Enter Resolution: ', self.select_resolution)

        ## Widget layout
        self.dialog.layout = QVBoxLayout()
        self.dialog.layout.addLayout(self.download_form)
        self.dialog.layout.addWidget(self.button_box)
        self.dialog.setLayout(self.dialog.layout)
        
    def restore_saved_downloads(self):
        """ Restore saved downloads from the settings scope """
        global saved_downloads, progress_bars
        settings = QtCore.QSettings('Main', 'settings')
        try:
            saved_downloads = list(json.loads(settings.value('savedDownloads', None)))
            for idx, d in enumerate(saved_downloads):
                print(idx, d)
                self.insertRow(idx)
                progress_bar = QProgressBar(self)
                progress_bar.setAlignment(QtCore.Qt.AlignCenter)
                progress_bars.append(progress_bar)
                self.setItem(idx , 0, QTableWidgetItem(d['file']))
                self.setItem(idx, 1, QTableWidgetItem(d['title']))
                self.setItem(idx, 2, QTableWidgetItem(d['filesize']))
                self.setItem(idx, 4, QTableWidgetItem(d['description']))
                progress_bar.setValue(d['progress'])
                self.setCellWidget(idx,3, progress_bar)
        except TypeError or ValueError:
            pass

    def add_row(self, data: Dict, **kwargs):
        """ Add a new row """
        global progress_bars
        global saved_downloads
        print(f'[PROCESS]: Adding a new row.')
        progress_bar = QProgressBar(self)
        progress_bar.setAlignment(QtCore.Qt.AlignCenter)
        row_count = self.rowCount()
        print(row_count)
        self.current = row_count
        self.insertRow(row_count)

        d = list(data.values())
        self.setItem(row_count , 0, QTableWidgetItem(d[0]))
        self.setItem(row_count, 1, QTableWidgetItem(d[1]))
        self.setItem(row_count, 2, QTableWidgetItem(d[2]))
        self.setItem(row_count, 4, QTableWidgetItem(d[4]))
        progress_bar.setValue(0)
        self.setCellWidget(row_count,3, progress_bar)
        progress_bars.append({
            'widget':progress_bar,
            'progress':0
        })
        saved_downloads.append({
            'progress':0,
            'file':d[0],
            'title': d[1],
            'filesize': d[2],
            'description': d[4]
        })

    def delete_row(self, index:int):
        """ Delete an existing row from the table """
        rows = set()
        for index in self.selectedIndexes():
            rows.add(index.row())
        self.removeRow(1)

    def set_selected_mode(self, x):
        """ Set the selected mode from the ComboBox """
        print(f'[SELECTED MODE]: {x}')
        self.selected_mode = int(x)

    def set_selected_resolution(self, x):
        """ Set the selected resolution from the ComboBox """
        print(f'[SELECTED RESOLUTION]: {list(resolutions)[x]}p')
        self.selected_resolution = list(resolutions)[x]

    def submit(self):
        """ onSubmit event for the Download dialog/form """
        self.thread = QtCore.QThread()
        print(str(self.url_field.text()))
        print(self.selected_resolution)
        print(self.selected_mode)
        video_obj = video_description(self.url_field.text(), self.on_download_progress, self.on_download_complete)
        video = video_obj["streams"].filter(file_extension="mp4", resolution=f"{str(self.selected_resolution)}p")
        print(video[0].filesize)
        rowData = {
            'File': video_obj['title']+'.mp4',
            'Title': video_obj['title'],
            'Size': convert(video[0].filesize, metric=True),
            'Status': random.randint(0,100),
            'Description': video_obj['description']
        }
        # self.close()
        self.add_row(rowData)
        self.dialog.close()

        # Run the Download Thread
        self.download_worker = DownloadWorker(video_obj, resolution=self.selected_resolution)
        self.download_worker.moveToThread(self.thread)
        self.thread.started.connect(self.download_worker.run)
        self.download_worker.finished.connect(self.thread.quit)
        self.download_worker.finished.connect(self.download_worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        # Start the thread
        self.thread.start()


    # Download Callbacks 
    def on_download_progress(self,stream, chunk, bytes_remaining):
        global progress_bars
        print(self.current)
        total_size = stream.filesize 
        bytes_downloaded = total_size - bytes_remaining 
        percentage_of_completion = (bytes_downloaded / total_size) * 100
        print(f"[PERCENTAGE OF COMPLETION]: {round(percentage_of_completion)}")
        progress_bars[self.current]['widget'].setValue(percentage_of_completion)
        saved_downloads[self.current]['progress'] = percentage_of_completion

    def on_download_complete(self,stream, filepath):
        print(f'[COMPLETED]: Saved in {filepath}')

## Worker for downloading a single video
class DownloadWorker(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    def __init__(self, video_obj, resolution: int, parent=None):
        super(QtCore.QObject, self).__init__()
        self.video_obj = video_obj 
        self.resolution = resolution
    def run(self):
        download_video(self.video_obj, self.resolution)
        self.finished.emit()
