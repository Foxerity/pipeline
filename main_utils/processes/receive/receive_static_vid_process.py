import multiprocessing
import time


from pipeline_abc import Pipeline
from main_utils.processes.receive.utils.SPADE.serial_demo_single import receive_class


class StaticVidProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.vid_obj_queue = None
        self.rece_vid_queue = None
        self.socket_queue = None
        self.static_value_queue = None
        self.model_name = None

    def setup(self, vid_obj_queue, rece_vid_queue, socket_queue, static_value_queue, **kwargs):
        self.vid_obj_queue = vid_obj_queue
        self.rece_vid_queue = rece_vid_queue
        self.socket_queue = socket_queue
        self.static_value_queue = static_value_queue

    def run(self, **kwargs):
        while True:
            if self.vid_obj_queue and not self.vid_obj_queue.empty():
                self.model_name = self.vid_obj_queue.get()
                dic = {
                    "model_name": self.model_name,
                    "dataset_mode": "pix2pix",
                    "label_nc": 0
                }

                receive = receive_class(self.rece_vid_queue, self.socket_queue, dic)
                process = multiprocessing.Process(target=receive.main)
                process.start()
            time.sleep(0.5)


if __name__ == '__main__':
    test_receive = StaticVidProcess()
    test_q1 = multiprocessing.Queue()
    test_model_name = "two_box"

    test_receive.setup(test_q1, test_model_name)
    test_receive.run()
