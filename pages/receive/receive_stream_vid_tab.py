import os

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtCore import QTimer, Qt


class StreamVidTab(QtWidgets.QWidget):
    def __init__(self, path, skeleton_queue, generation_queue):
        super(StreamVidTab, self).__init__(flags=Qt.WindowFlags())
        uic.loadUi(path, self)

        self.skeleton_frame = self.findChild(QtWidgets.QFrame, 'skeleton_frame')
        self.gener_frame = self.findChild(QtWidgets.QFrame, 'gener_frame')
        self.skeletionButton = self.findChild(QtWidgets.QPushButton, 'skeletionButton')
        self.generButton = self.findChild(QtWidgets.QPushButton, 'generButton')
        self.calculateButton = self.findChild(QtWidgets.QPushButton, 'calculateButton_3')
        self.receiveButton = self.findChild(QtWidgets.QPushButton, 'receiveButton_3')

        browser_font = QtGui.QFont()
        browser_font.setPointSize(14)
        self.receiveButton.setFont(browser_font)
        self.calculateButton.setFont(browser_font)
        self.skeletionButton.setFont(browser_font)
        self.generButton.setFont(browser_font)
        self.calculateButton.setText('计算')
        self.receiveButton.setText('接收')
        self.skeletionButton.setText('骨骼点')
        self.generButton.setText('生成')

        self.skeleton_queue = skeleton_queue
        self.generation_queue = generation_queue

        self.skeletionButton.clicked.connect(lambda: self.check_for_skeleton())
        self.generButton.clicked.connect(lambda: self.check_for_generation())

    def check_for_skeleton(self):
        if self.skeleton_queue and not self.skeleton_queue.empty():
            img = self.skeleton_queue.get()
            print('get img.')
            if img and isinstance(img, Image.Image):
                self.display_image(img, 'ske')
                QTimer().singleShot(80, lambda: self.check_for_skeleton())
            else:
                QTimer().singleShot(80, lambda: self.check_for_skeleton())
        else:
            QTimer().singleShot(80, lambda: self.check_for_skeleton())

    def check_for_generation(self):
        if self.generation_queue and not self.generation_queue.empty():
            img = self.generation_queue.get()
            print('get img.')
            if img and isinstance(img, Image.Image):
                self.display_image(img, 'gen')
                QTimer().singleShot(80, lambda: self.check_for_generation())
            else:
                QTimer().singleShot(80, lambda: self.check_for_generation())
        else:
            QTimer().singleShot(80, lambda: self.check_for_generation())

    def display_image(self, image_path, img_type):
        if isinstance(image_path, Image.Image):
            pixmap = ImageQt(image_path)
        else:
            pixmap = QtGui.QPixmap(image_path)
        if img_type == 'ske':
            pixmap = pixmap.scaled(self.skeleton_frame.size())
            palette = self.skeleton_frame.palette()
            palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
            self.skeleton_frame.setPalette(palette)
            self.skeleton_frame.setAutoFillBackground(True)
            self.skeleton_frame.repaint()
        elif img_type == 'gen':
            pixmap = pixmap.scaled(self.gener_frame.size())
            palette = self.gener_frame.palette()
            palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
            self.gener_frame.setPalette(palette)
            self.gener_frame.setAutoFillBackground(True)
            self.gener_frame.repaint()


