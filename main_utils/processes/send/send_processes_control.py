from pipeline_abc import Pipeline
from main_utils.processes.send.send_txt_process import TxtProcess
from main_utils.processes.send.send_img_process import ImgProcess
from main_utils.processes.send.send_static_vid_process import StaticVidProcess
from main_utils.processes.send.send_stream_vid_process import StreamVidProcess


class ProcessesControl(Pipeline):
    def setup(self, **kwargs):
        self.config = {
            'name': "Object Detection"
        }
        self.modules = [
            TxtProcess(),
            ImgProcess(),
            StaticVidProcess(),
            StreamVidProcess(),
        ]

        for module in self.modules:
            module.setup()

    def run(self, **kwargs):
        pass
