# Ramin Toosi

import os
import sys

from PyQt5 import QtGui
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

import design
import ydlAPI as ydl


class Demo(QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Explaining super is out of the scope of this article
        # So please google it if you're not familiar with it
        # Simple reason why we use it here is that it allows us to
        # access variables, methods etc in the design.py file
        super(Demo, self).__init__()
        self.ui = design.Ui_MainWindow
        self.setupUi(self)

        scriptDir = os.path.dirname(os.path.realpath(__file__))
        pixmap = QtGui.QPixmap(os.path.join(scriptDir,'materials/no_thumbnail.png'))
        self.label_thumbnail.setScaledContents(True)
        self.label_thumbnail.setPixmap(pixmap)
        self.label_thumbnail_2.setScaledContents(True)
        self.label_thumbnail_2.setPixmap(pixmap)
        qtRectangle = self.frameGeometry()
        centerPoint = QtWidgets.QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())
        self.setWindowIcon(QtGui.QIcon(os.path.join(scriptDir,'materials/logo.png')))


        # variables

        # self.push_next.clicked.connect(self.goToNext)
        self.push_url.clicked.connect(self.get_url_streams)
        self.check_best.clicked.connect(self.download_best_option)
        self.push_download.clicked.connect(self.download_video)
        self.push_browse.clicked.connect(self.browse_folder)
        self.line_url.textChanged.connect(self.url_changed)
        self.push_batch_select.clicked.connect(self.select_batch)
        self.push_batch_brows.clicked.connect(self.browse_batch_folder)
        self.push_download_batch.clicked.connect(self.download_batch)
        self.check_hfolder.clicked.connect(self.check_batch_output_format)

    def url_changed(self):
        self.push_download.setEnabled(False)
        self.push_download.setText('Download (Load URL First)')
        self.stream_tree.clear()
        self.label_thumbnail.clear()
        self.label_title.clear()
        pixmap = QtGui.QPixmap('materials/no_thumbnail.png')
        self.label_thumbnail.setScaledContents(True)
        self.label_thumbnail.setPixmap(pixmap)

    def get_url_streams(self):
        self.stream_tree.clear()
        self.label_thumbnail.clear()
        self.label_title.clear()
        pixmap = QtGui.QPixmap('materials/no_thumbnail.png')
        self.label_thumbnail.setScaledContents(True)
        self.label_thumbnail.setPixmap(pixmap)
        url = self.line_url.text()
        opt_dict = self.get_options()
        ret, formats = ydl.get_available_streams(url,opt_dict)
        if ret:
            self.push_download.setEnabled(True)
            self.push_download.setText('Download')
            QtWidgets.QApplication.processEvents()
            parvid = QtWidgets.QTreeWidgetItem(self.stream_tree)
            parvid.setText(0, "Video")
            parvid.setFlags(parvid.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            paraud = QtWidgets.QTreeWidgetItem(self.stream_tree)
            paraud.setText(0, "Audio")
            paraud.setText(0, "Audio")
            paraud.setFlags(paraud.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            for frm in formats:
                if frm[2] == 'audio':
                    child = QtWidgets.QTreeWidgetItem(paraud)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    s = ','
                    child.setText(0, s.join(frm))
                    child.setCheckState(0, Qt.Unchecked)
                else:
                    child = QtWidgets.QTreeWidgetItem(parvid)
                    child.setFlags(child.flags() | Qt.ItemIsUserCheckable)
                    s = ','
                    child.setText(0, s.join(frm))
                    child.setCheckState(0, Qt.Unchecked)
            self.stream_tree.show()
            QtWidgets.QApplication.processEvents()
            thumbnail = ydl.get_thumbnail(url,opt_dict)
            if thumbnail:
                pixmap = QtGui.QPixmap(thumbnail)
                self.label_thumbnail.setScaledContents(True)
                self.label_thumbnail.setPixmap(pixmap)
                if not self.check_thumbnail.isChecked():
                    os.remove(thumbnail)
            self.label_title.setText(ydl.get_title(url,opt_dict))
        else:
            self.showMessage('Invalid URL')



    def download_best_option(self):
        self.stream_tree.setEnabled(not self.check_best.isChecked())

    def get_options(self):
        opt_dict = {}
        proxy = self.line_proxy.text()
        if not proxy == '':
            opt_dict['proxy'] = proxy

        if self.line_dir.text() or self.line_filename.text():
            if self.line_filename.text():
                opt_dict['output_path'] = os.path.join(self.line_dir.text(),self.line_filename.text() + '.%(ext)s')
            else:
                opt_dict['output_path'] = os.path.join(self.line_dir.text(), '%(title)s.%(ext)s')

        return opt_dict

    def download_video(self):
        self.push_download.setText('Downloading ...')
        opt_dict = self.get_options()
        url = self.line_url.text()
        if self.check_best.isChecked():
            selected_frms = ['best']
        else:
            selected_frms = self.find_checked()
        if selected_frms == []:
            self.showMessage('No stream is selected.')
            return

        for ifrm, frm in enumerate(selected_frms):
            for progval, filesize, speed, eta in ydl.download_video(url,frm,opt_dict):
                self.progress_single.setValue(int(float(progval[:-1])*10))
                self.progress_total.setValue(int((ifrm*1000 + float(progval[:-1]) * 10) / len(selected_frms)))
                self.label_speed.setText(speed)
                self.label_eta.setText(eta)
                self.label_size.setText(filesize)
                QtWidgets.QApplication.processEvents()
        self.push_download.setText('Download')


    def find_checked(self):
        checked = []
        root = self.stream_tree.invisibleRootItem()
        signal_count = root.childCount()

        for i in range(signal_count):
            signal = root.child(i)
            num_children = signal.childCount()

            for n in range(num_children):
                child = signal.child(n)

                if child.checkState(0) == QtCore.Qt.Checked:
                    checked.append(child.text(0).split(',')[0])
        return checked

    def browse_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        if folder != '':
            self.line_dir.setText(folder)

    def select_batch(self):
        filename = QtWidgets.QFileDialog.getOpenFileName()[0]
        if filename != '':
            self.list_urls.clear()
            self.line_batchfile.setText(filename)
            urls = ydl.read_batchfile(filename)
            self.list_urls.addItems(urls)

    def browse_batch_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory()
        if folder != '':
            self.line_output_batch.setText(folder)

    def download_batch(self):
        opt_dict = self.get_options_batch()
        self.push_download_batch.setText('Downloading ...')
        urls = []
        for index in range(self.list_urls.count()):
            urls.append(self.list_urls.item(index).text())

        for ifrm, url in enumerate(urls):
            for progval, filesize, speed, eta in ydl.download_video_batch(url, opt_dict):
                self.progress_single_2.setValue(int(float(progval[:-1]) * 10))
                self.progress_total_2.setValue(int((ifrm * 1000 + float(progval[:-1]) * 10) / len(urls)))
                self.label_speed_2.setText(speed)
                self.label_eta_2.setText(eta)
                self.label_size_2.setText(filesize)
                QtWidgets.QApplication.processEvents()
        self.push_download.setText('Download')

    def check_batch_output_format(self):
        self.label_14.setEnabled(self.check_hfolder.isChecked())
        self.combo_folder_name.setEnabled(self.check_hfolder.isChecked())

    def get_options_batch(self):
        opt_dict = {}
        proxy = self.line_proxy.text()
        if not proxy == '':
            opt_dict['--proxy'] = proxy

        if self.radio_best.isChecked():
            opt_dict['-f'] = 'best'
        else:
            opt_dict['-f'] = 'worst'

        if self.check_hfolder.isChecked():
            indfoldername = self.combo_folder_name.currentIndex()
            if indfoldername == 0:
                foldername = '%(title)s'
            else:
                foldername = '%(id)s'
            str_out = foldername + '/' + '%(title)s.%(ext)s'
            opt_dict['-o'] = os.path.join(self.line_output_batch.text(),str_out)
        else:
            opt_dict['-o'] = os.path.join(self.line_output_batch.text(), '%(title)s.%(ext)s')

        return opt_dict


    def showMessage(self,text):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Information)
        msg.setText(text)
        msg.setWindowTitle("RTYDL")
        msg.exec()





def main():
    app = QtWidgets.QApplication(sys.argv)
    mainWin = Demo()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()