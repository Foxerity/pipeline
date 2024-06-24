import multiprocessing

from pipeline_abc import Pipeline
from main_utils.processes.send.send_socket_process import SendSocketProcess
from main_utils.processes.send.send_txt_process import TxtProcess
from main_utils.processes.send.send_img_process import ImgProcess
from main_utils.processes.send.send_static_vid_process import StaticVidProcess
from main_utils.processes.send.send_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def __init__(self):
        super().__init__()
        self.SendSocketProcess = None
        self.TxtProcess = None
        self.ImgProcess = None
        self.StaticVidProcess = None
        self.StreamVidProcess = None
        self.queue_dict = None

    def setup(self, queue_dict, **kwargs):
        self.config = {
            'name': "Object Detection",
            # 'host': '192.168.2.137',
            'host': '127.0.0.1',
            'port': 12343,
        }
        self.queue_dict = queue_dict

        self.modules = [
            SendSocketProcess(),
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]
        self.initialize_modules()

        parameters = {
            "SendSocketProcess": (
                self.config['host'],
                self.config['port'],
                queue_dict
            ),
            
            "TxtProcess": (
                queue_dict['txt_socket_queue'],
                queue_dict['txt_queue'],
            ),

            "ImgProcess": (
                queue_dict['img_queue'],
                queue_dict['img_socket_queue'],
            ),

            "StaticVidProcess": (
                queue_dict['static_vid_queue'],
                queue_dict['static_socket_queue'],
            ),
            
            "StreamVidProcess": (
                queue_dict['stream_vid_queue'],
            )
        }

        self.SendSocketProcess.setup(*parameters['SendSocketProcess'])
        self.TxtProcess.setup(*parameters['TxtProcess'])
        self.ImgProcess.setup(*parameters['ImgProcess'])
        # self.StaticVidProcess.setup(*parameters['StaticVidProcess'])
        # self.StreamVidProcess.setup(*parameters['StreamVidProcess'])

    def run(self, **kwargs):
        socket_process = multiprocessing.Process(target=self.SendSocketProcess.run)
        socket_process.start()

        txt_process = multiprocessing.Process(target=self.TxtProcess.run)
        txt_process.start()

        img_process = multiprocessing.Process(target=self.ImgProcess.run)
        img_process.start()

        # static_vid_process = multiprocessing.Process(target=self.StaticVidProcess.run)
        # static_vid_process.start()

        # stream_vid_process = multiprocessing.Process(target=self.StreamVidProcess.run)
        # stream_vid_process.start()


