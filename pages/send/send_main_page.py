from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from pipeline_abc import Pipeline
from pages.send.send_text_tab import TextTabWidget
from pages.send.send_img_tab import ImageTabWidget
from pages.send.send_static_vid_tab import StaticVidTab
from pages.send.send_stream_vid_tab import StreamVidTab


# 主界面
class MainPage(QtWidgets.QMainWindow, Pipeline):
    # 子界面的配置文件, 分别对应文本、图像、静态视频、流式视频Tab
    pages_path = [
        "ui/send/send_txt_tab.ui",
        "ui/send/send_img_tab.ui",
        "ui/send/send_static_vid_tab.ui",
        "ui/send/send_stream_vid_tab.ui",
    ]

    def __init__(self, queue_dict):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        Pipeline.__init__(self)
        self.queue_dict = queue_dict
        # 创建主窗口的 QTabWidget
        self.tab_widget = QtWidgets.QTabWidget()
        self.init_main_UI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0], queue_dict['txt_queue']), "指令")
        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1], queue_dict['img_queue']), "图像")
        self.tab_widget.addTab(StaticVidTab(self.pages_path[2], queue_dict['static_vid_queue']), "静态视频")
        self.tab_widget.addTab(StreamVidTab(self.pages_path[3], queue_dict['stream_vid_queue']), "流式视频")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        self.on_tab_changed(0)

    def init_main_UI(self):
        # 设置窗口位置和大小（x, y, width, height）
        self.setGeometry(800, 800, 1600, 1000)
        self.setWindowTitle('水下通信演示系统——发送端')

        self.setCentralWidget(self.tab_widget)
        self.tab_widget.setStyleSheet("""
                        QTabBar::tab {
                            font-size: 18px;      /* 设置字体大小为18px */
                            height: 40px;         /* 设置标签高度为40px */
                            width: 120px;         /* 设置标签宽度为120px */
                            min-width: 100px;     /* 设置标签最小宽度为100px */
                            min-height: 30px;     /* 设置标签最小高度为30px */
                            max-width: 150px;     /* 设置标签最大宽度为150px */
                            max-height: 50px;     /* 设置标签最大高度为50px */
                        }
                        """)

    def setup(self, **kwargs):
        pass

    def run(self, **kwargs):
        self.show()

    def on_tab_changed(self, index):
        print(f"Current tab index: {index}")
        current_widget = self.tab_widget.currentWidget()
        print(f"Current tab widget: {current_widget}")

        # 执行不同的操作，根据当前选中的标签页
        if index == 0:
            print("Text Tab is selected")
            queue_tuple = self.queue_dict['txt_socket_queue']
            self.queue_dict['control_queue'].put(queue_tuple)
            print("putting txt_socket_queue")
        elif index == 1:
            queue_tuple = self.queue_dict['img_socket_queue']
            self.queue_dict['control_queue'].put(queue_tuple)
            print("Image Tab is selected")
        elif index == 2:
            print("Static Video Tab is selected")
            queue_tuple = self.queue_dict['static_socket_queue']
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 3:
            print("Stream Video Tab is selected")

