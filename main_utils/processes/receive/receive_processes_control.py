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
        self.queue_dict = None

    def setup(self, queue_dict, **kwargs):
        self.queue_dict = queue_dict
        self.config = {
            # 'host': '192.168.2.137',
            'host': '127.0.0.1',
            'port': 60009,
        }
        self.modules = [
            ReceiveSocketProcess(),
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]
        self.initialize_modules()

        self.modules[0].setup(self.config['host'], self.config['port'], queue_dict)
        self.modules[1].setup(queue_dict['txt_socket_queue'], queue_dict['txt_queue'], queue_dict['txt_trad_queue'])
        self.modules[2].setup(queue_dict['img_queue'], queue_dict["img_tra_queue"], queue_dict['img_socket_queue'])
        self.modules[3].setup(queue_dict['vid_obj_queue'], queue_dict['rec_queue'], queue_dict['static_socket_queue'])
        # self.modules[4].setup(queue_dict['skeleton_queue'], queue_dict['generation_queue'])

    def run(self, **kwargs):
        print("creating subprocesses.")
        socket_process = multiprocessing.Process(target=self.modules[0].run)
        socket_process.start()

        txt_process = multiprocessing.Process(target=self.modules[1].run)
        txt_process.start()

        img_process = multiprocessing.Process(target=self.modules[2].run)
        img_process.start()

        static_vid_process = multiprocessing.Process(target=self.modules[3].run)
        static_vid_process.start()

        # stream_vid_process = multiprocessing.Process(target=self.modules[4].run)
        # stream_vid_process.start()


