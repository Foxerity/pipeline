import os
import sys
from PyQt5 import uic, QtWidgets, QtGui
from PyQt5.QtWidgets import QMainWindow, QApplication, QTabWidget, QFileDialog, QSizePolicy
from PyQt5.QtCore import Qt, QFileSystemWatcher, QTimer

from callback.callback import Callback
from pipeline_abc import Pipeline


class MainPage(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainPage, self).__init__()
        self.initUI()
        # 加载并添加各个标签页
        self.initTabs_txt("ui/recive/recive_txt_tab.ui")
        self.initTabs_img("ui/recive/recive_img_tab.ui")
        self.initTabs_static_vid("ui/recive/recive_static_vid_tab.ui")
        self.initTabs_stream_vid("ui/recive/recive_stream_vid_tab.ui")

    def initUI(self):
        # 设置窗口位置和大小（x, y, width, height）
        self.setGeometry(800, 800, 800, 800)
        self.setWindowTitle('Set Geometry Example')
        # 创建主窗口的 QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_widget)

    def initTabs_txt(self, path):
        self.add_tab(path, "指令")

    def initTabs_img(self, path):
        self.add_tab(path, "图片")

    def initTabs_static_vid(self, path):
        self.add_tab(path, "静态视频")

    def initTabs_stream_vid(self, path):
        self.add_tab(path, "流式视频")

        self.skeleton_frame = self.findChild(QtWidgets.QFrame, 'skeleton_frame')
        self.gener_frame = self.findChild(QtWidgets.QFrame, 'gener_frame')

        self.browserButton = self.findChild(QtWidgets.QPushButton, 'browserButton_3')

        self.sendButton = self.findChild(QtWidgets.QPushButton, 'sendButton_3')

        self.browserButton.clicked.connect(lambda: self.open_file_dialog('skeleton_frame'))
        self.sendButton.clicked.connect(lambda: self.open_file_dialog('gener_frame'))

    def add_tab(self, ui_file, tab_name):
        # 加载 .ui 文件并创建相应的 QWidget
        tab = uic.loadUi(ui_file)
        self.tab_widget.addTab(tab, tab_name)

    def open_file_dialog(self, show_frame=None):
        # 打开文件对话框选择目录
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, '选择目录')
        if show_frame == 'skeleton_frame':
            self.skeleton_directory = directory
        elif show_frame == 'gener_frame':
            self.gener_directory = directory
        else:
            raise ValueError
        if directory:
            print(f"监视目录：{directory}")
            self.check_for_new_image(directory, show_frame)

    def check_for_new_image(self, directory, show_frame=None):
        # 获取目录中的所有文件
        if show_frame == 'skeleton_frame':
            if not directory == self.skeleton_directory:
                return
            show_frames = self.skeleton_frame
        elif show_frame == 'gener_frame':
            if not directory == self.gener_directory:
                return
            show_frames = self.gener_frame
        else:
            raise ValueError

        files = os.listdir(directory)
        # 过滤图片文件
        image_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]

        if image_files:
            # 如果找到图片，显示第一张图片
            image_path = os.path.join(directory, image_files[0])
            self.display_image(image_path, show_frames)
            os.remove(image_path)
            QTimer.singleShot(1, lambda: self.check_for_new_image(directory, show_frame))
        else:
            # 如果没有图片，定时器每隔一段时间检查一次
            QTimer.singleShot(1000, lambda: self.check_for_new_image(directory, show_frame))

    def display_image(self, image_path, show_frame=None):
        # 创建 QPixmap 并从文件加载图片
        pixmap = QtGui.QPixmap(image_path)
        pixmap = pixmap.scaled(show_frame.size())
        # 创建 QPalette 并设置 QFrame 的背景
        palette = show_frame.palette()
        palette.setBrush(QtGui.QPalette.Background, QtGui.QBrush(pixmap))
        show_frame.setPalette(palette)
        show_frame.setAutoFillBackground(True)
        show_frame.repaint()


class MainWindow(Pipeline):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.main_page = MainPage()

    def setup(self, **kwargs):
        pass

    def run(self, callbacks: Callback = None, **kwargs):
        self.main_page.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = MainWindow()
    main.run()
    sys.exit(app.exec_())
