import multiprocessing

from pipeline_abc import Pipeline
from main_utils.processes.receive.receive_txt_process import TxtProcess
from main_utils.processes.receive.receive_img_process import ImgProcess
from main_utils.processes.receive.receive_static_vid_process import StaticVidProcess
from main_utils.processes.receive.receive_stream_vid_process import StreamVidProcess
from main_utils.processes.receive.receive_socket_process import ReceiveSocketProcess


class ProcessesControl(Pipeline):
    def __init__(self):
        super().__init__()
        self.StaticVidProcess = None
        self.ImgProcess = None
        self.TxtProcess = None
        self.ReceiveSocketProcess = None
        self.queue_dict = None

    def setup(self, queue_dict, **kwargs):
        self.queue_dict = queue_dict
        self.config = {
            # 'host': '192.168.2.137',
            'host': '127.0.0.1',
            'port': 12343,
        }
        self.modules = [
            ReceiveSocketProcess(),
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]
        self.initialize_modules()

        parameters = {
            "ReceiveSocketProcess": (
                    self.config['host'],
                    self.config['port'],
                    queue_dict
            ),

            "TxtProcess": (
                    queue_dict['txt_socket_queue'],
                    queue_dict['txt_queue'],
                    queue_dict['txt_trad_queue'],
                    queue_dict['txt_value_queue']
            ),

            "ImgProcess": (
                    queue_dict['img_queue'],
                    queue_dict["img_tra_queue"],
                    queue_dict['img_socket_queue'],
                    queue_dict['img_value_queue']
            ),

            "StaticVidProcess": (
                    queue_dict['vid_obj_queue'],
                    queue_dict['rec_queue'],
                    queue_dict['static_socket_queue'],
                    queue_dict['static_value_queue'],
            ),
            "StreamVidProcess": (
                    queue_dict['skeleton_queue'],
                    queue_dict['generation_queue']
            )
        }

        self.ReceiveSocketProcess.setup(*parameters['ReceiveSocketProcess'])
        self.TxtProcess.setup(*parameters['TxtProcess'])
        self.ImgProcess.setup(*parameters['ImgProcess'])
        self.StaticVidProcess.setup(*parameters['StaticVidProcess'])
        # self.StreamVidProcess.setup(*parameters['StreamVidProcess'])

    def run(self, **kwargs):
        print("creating subprocesses.")

        socket_process = multiprocessing.Process(target=self.ReceiveSocketProcess.run)
        socket_process.start()

        txt_process = multiprocessing.Process(target=self.TxtProcess.run)
        txt_process.start()

        img_process = multiprocessing.Process(target=self.ImgProcess.run)
        img_process.start()

        static_vid_process = multiprocessing.Process(target=self.StaticVidProcess.run)
        static_vid_process.start()

        # stream_vid_process = multiprocessing.Process(target=self.StreamVidProcess.run)
        # stream_vid_process.start()


