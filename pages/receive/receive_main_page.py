from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy

from pages.receive.receive_text_tab import TextTabWidget
from pages.receive.receive_img_tab import ImageTabWidget
from pages.receive.receive_static_vid_tab import StaticVidTab
from pages.receive.receive_stream_vid_tab import StreamVidTab


class MainPage(QtWidgets.QMainWindow):
    pages_path = [
        "ui/receive/receive_txt_tab.ui",
        "ui/receive/receive_img_tab.ui",
        "ui/receive/receive_static_vid_tab.ui",
        "ui/receive/receive_stream_vid_tab.ui",
    ]

    def __init__(self, queue_dict):
        super(MainPage, self).__init__(flags=Qt.WindowFlags())
        # 创建主窗口的 QTabWidget
        self.queue_dict = queue_dict
        self.tab_widget = QtWidgets.QTabWidget()
        self.initUI()
        # 加载并添加四个标签页, 分别对应文本、图像、静态视频、流式视频Tab
        self.tab_widget.addTab(TextTabWidget(self.pages_path[0],
                                             queue_dict['txt_queue'], queue_dict['txt_trad_queue'],
                                             queue_dict['txt_value_queue'], queue_dict['socket_value']),
                               "指令")

        self.tab_widget.addTab(ImageTabWidget(self.pages_path[1], queue_dict['img_queue'], queue_dict["img_tra_queue"],
                                              queue_dict["img_value_queue"], queue_dict["socket_value"]),
                               "图像")

        self.tab_widget.addTab(StaticVidTab(self.pages_path[2],
                                            queue_dict['vid_obj_queue'], queue_dict['rec_queue'],
                                            queue_dict["static_value_queue"], queue_dict["socket_value"]),
                               "静态视频")

        self.tab_widget.addTab(StreamVidTab(self.pages_path[3],
                                            queue_dict['skeleton_queue'], queue_dict['generation_queue']),
                               "流式视频")

        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
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

        self.on_tab_changed(0)

    def initUI(self):
        # 设置窗口位置和大小(x, y, width, height)
        self.setGeometry(800, 800, 1600, 1000)
        self.setWindowTitle('水下通信演示系统——接收端')

        self.setCentralWidget(self.tab_widget)

    def on_tab_changed(self, index):
        print(f"Current tab index: {index}")
        current_widget = self.tab_widget.currentWidget()
        print(f"Current tab widget: {current_widget}")

        # 执行不同的操作，根据当前选中的标签页
        if index == 0:
            print("Text Tab is selected")
            queue_tuple = (1047, self.queue_dict['txt_socket_queue'])
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 1:
            print("Image Tab is selected")
            queue_tuple = (1047, self.queue_dict['img_socket_queue'])
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 2:
            print("Static Video Tab is selected")
            queue_tuple = (1047, self.queue_dict['static_socket_queue'])
            self.queue_dict['control_queue'].put(queue_tuple)
        elif index == 3:
            print("Stream Video Tab is selected")
