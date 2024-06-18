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
        self.txt_queue = None
        self.txt_tral_queue = None
        self.txt_socket_queue = None

        self.img_queue = None

        self.vid_obj_queue = None
        self.rece_vid_queue = None
        self.socket_queue = None

        self.skeleton_queue = None
        self.generation_queue = None

    def setup(self, queue_dict, **kwargs):
        self.config = {
            # 'host': '192.168.2.137',
            'host': '127.0.0.1',
            'port': 60000,
        }
        self.modules = [
            ReceiveSocketProcess(),
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]

        self.txt_queue = queue_dict['txt_queue']
        self.txt_tral_queue = queue_dict['txt_tral_queue']
        self.txt_socket_queue = queue_dict['txt_socket_queue']

        self.img_queue = queue_dict['img_queue']

        self.vid_obj_queue = queue_dict['vid_obj_queue']
        self.rece_vid_queue = queue_dict['receive_queue']
        self.socket_queue = queue_dict['static_socket_queue']

        self.skeleton_queue = queue_dict['skeleton_queue']
        self.generation_queue = queue_dict['generation_queue']

        self.modules[0].setup(self.config['host'], self.config['port'], queue_dict)
        self.modules[1].setup(self.txt_socket_queue, self.txt_queue, self.txt_tral_queue)
        # self.modules[2].setup(self.vid_obj_queue)
        # self.modules[3].setup(self.vid_obj_queue, self.rece_vid_queue, self.socket_queue)
        # self.modules[4].setup(self.skeleton_queue, self.generation_queue)

    def run(self, **kwargs):
        print("creating subprocesses.")
        txt_process = multiprocessing.Process(target=self.modules[0].run)
        txt_process.start()

        img_process = multiprocessing.Process(target=self.modules[1].run)
        img_process.start()
        #
        # static_vid_process = multiprocessing.Process(target=self.modules[2].run)
        # static_vid_process.start()
        #
        # stream_vid_process = multiprocessing.Process(target=self.modules[3].run)
        # stream_vid_process.start()


