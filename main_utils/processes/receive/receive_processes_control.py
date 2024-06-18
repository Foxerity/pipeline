import multiprocessing

from pipeline_abc import Pipeline
from main_utils.processes.receive.receive_txt_process import TxtProcess
from main_utils.processes.receive.receive_img_process import ImgProcess
from main_utils.processes.receive.receive_static_vid_process import StaticVidProcess
from main_utils.processes.receive.receive_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def __init__(self):
        super().__init__()
        self.txt_queue = None
        self.txt_tral_queue = None

        self.img_queue = None

        self.vid_obj_queue = None
        self.rece_vid_queue = None

        self.skeleton_queue = None
        self.generation_queue = None

    def setup(self, txt_queue, txt_tral_queue, img_queue, skeleton_queue, generation_queue, vid_obj_queue, rece_vid_queue, **kwargs):
        self.modules = [
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]
        self.txt_queue = txt_queue
        self.txt_tral_queue = txt_tral_queue

        self.img_queue = img_queue

        self.vid_obj_queue = vid_obj_queue
        self.rece_vid_queue = rece_vid_queue

        self.skeleton_queue = skeleton_queue
        self.generation_queue = generation_queue

        self.modules[0].setup(self.txt_queue, self.txt_tral_queue)
        # self.modules[1].setup(self.vid_obj_queue)
        # self.modules[2].setup(self.vid_obj_queue, self.rece_vid_queue)
        # self.modules[3].setup(self.skeleton_queue, self.generation_queue)

    def run(self, **kwargs):
        txt_process = multiprocessing.Process(target=self.modules[0].run)
        txt_process.start()

        # img_process = multiprocessing.Process(target=self.modules[1].run, args=(kwargs,))
        # img_process.start()
        #
        # static_vid_process = multiprocessing.Process(target=self.modules[2].run)
        # static_vid_process.start()
        #
        # stream_vid_process = multiprocessing.Process(target=self.modules[3].run)
        # stream_vid_process.start()


