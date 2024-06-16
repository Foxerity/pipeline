from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import Qt


class ImageTabWidget(QtWidgets.QWidget):
    def __init__(self, path):
        super(ImageTabWidget, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.show_frame = self.findChild(QtWidgets.QFrame, 'show_frame_2')
        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_2')
        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_2')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.browserButton.setFont(browser_font)
        self.sendButton.setFont(browser_font)
        self.browserButton.setText('浏览')
        self.sendButton.setText('发送')

    def pushButton_send_controlTimer(self):
        if not self.pushButton_send_timer.isActive():
            self.pushButton_send_timer.start()
            self.pushButton_send.setText(self.translate("MainWindow", "结束发送"))
        else:
            self.pushButton_send_timer.stop()
            self.send_thread.terminate()
            self.pushButton_send.setText(self.translate("MainWindow", "发送"))