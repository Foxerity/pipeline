import os
import time
import sys

from PIL import Image

from callback.callback import Callback
from pipeline_abc import Pipeline

sys.path.append('/home/samaritan/Project/pipeline/main_utils/processes/send/')
from send_utils.main import parse_args, handle_video


class StaticVidProcess(Pipeline):
    def __init__(self):
        super().__init__()
        self.path = None
        self.video_queue = None

    def setup(self, video_queue, **kwargs):
        self.path = r'/home/samaritan/Project/pipeline/main_utils/processes/send/send_utils/'
        self.video_queue = video_queue

    def run(self, callbacks: Callback = None, **kwargs):
        while True:
            if not self.video_queue.empty():

                video_name = self.video_queue.get()
                print('put success.')

                os.chdir(self.path)

                send_filename = video_name
                send_type = 'video'
                is_dynamic = False

                if send_filename.find("海底黄色") >= 0 \
                        or send_filename.find("sea_yellowbox") >= 0:
                    first_frame = './vector_lib/first_frame/sea_yellowbox_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/sea_yellowbox_0.png'

                    use_first_frame = True
                    pass

                elif send_filename.find("海底渔船") >= 0 \
                        or send_filename.find("sea_ship") >= 0:
                    first_frame = './vector_lib/first_frame/sea_ship_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/sea_ship_0.png'
                    use_first_frame = True

                    pass

                elif send_filename.find("海底潜艇") >= 0 \
                        or send_filename.find("sea_submarine") >= 0:

                    first_frame = './vector_lib/first_frame/sea_submarine_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/sea_submarine_0.png'
                    use_first_frame = True

                elif send_filename.find("黄色") >= 0 \
                        or send_filename.find("yellow") >= 0:
                    first_frame = './vector_lib/first_frame/yellowbox_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/yellowbox_0.png'
                    pass

                elif send_filename.find("鱼雷") >= 0 \
                        or send_filename.find("torpedo") >= 0:
                    first_frame = './vector_lib/first_frame/torpedo_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/torpedo_0.png'
                    pass

                elif send_filename.find("潜艇") >= 0 \
                        or send_filename.find("submarine") >= 0:
                    first_frame = './vector_lib/first_frame/submarine_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/submarine_0.png'

                    pass
                elif send_filename.find("渔船") >= 0 \
                        or send_filename.find("fish_ship") >= 0:
                    first_frame = './vector_lib/first_frame/fish_ship_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/fish_ship_0.png'

                    use_first_frame = True

                    pass
                elif send_filename.find("水雷") >= 0 \
                        or send_filename.find("mine") >= 0:
                    first_frame = './vector_lib/first_frame/mine2_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/mine2_0.png'
                    use_first_frame = True
                    pass

                elif send_filename.find("双色") >= 0 \
                        or send_filename.find("two") >= 0:

                    first_frame = './vector_lib/first_frame/two_color_box_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/twocolorbox_0.png'
                    use_first_frame = True
                    pass

                elif send_filename.find("乌龟") >= 0 \
                        or send_filename.find("tortoise") >= 0:
                    first_frame = './vector_lib/first_frame/tortoise_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/tortoise_0.png'
                    use_first_frame = True
                    pass

                elif send_filename.find("动态鱼") >= 0 \
                        or (send_filename.find("fishes") >= 0):
                    first_frame = './vector_lib/first_frame/fish_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/fish_0.png'

                    is_dynamic = True
                    use_first_frame = True
                    pass
                elif send_filename.find("UUV") >= 0 \
                        or send_filename.find("UUV") >= 0:
                    first_frame = './vector_lib/first_frame/UUV_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/UUV_0.png'

                    use_first_frame = True
                    pass

                elif send_filename.find("潜航器") >= 0 \
                        or send_filename.find("vehicle") >= 0:
                    first_frame = './vector_lib/first_frame/white_vehicle_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/white_vehicle_0.png'
                    pass

                elif send_filename.find("鲨鱼") >= 0 \
                        or send_filename.find("shark") >= 0:
                    first_frame = './vector_lib/first_frame/shark_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/shark_0.png'
                    pass

                    """ in xi'an Province """

                elif send_filename.find("桥墩") >= 0 \
                        or send_filename.find("pier") >= 0:
                    first_frame = './vector_lib/first_frame/pier_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/pier_0.png'
                    pass

                elif send_filename.find("检测器") >= 0 \
                        or send_filename.find("detector") >= 0:
                    first_frame = './vector_lib/first_frame/detector_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/detector_0.png'
                    use_first_frame = True
                    pass

                elif send_filename.find("仿生鱼") >= 0 \
                        or send_filename.find("bionic") >= 0:
                    first_frame = './vector_lib/first_frame/bionic_fish_0.png'
                    first_frame_seg = 'vector_lib/first_frame_seg/bionic_fish_0.png'
                    use_first_frame = True
                    pass
                else:
                    raise RuntimeError("Not support filename {} for now.".format(send_filename))

                print('type {}, filename, {}, use_first_frame {}'.format(send_type, video_name, use_first_frame))

                command = ["python", 'main.py', '-t', send_type, '-f', send_filename]

                if is_dynamic:
                    command.append('--dynamic')

                if use_first_frame:
                    command.extend(['--use_first_frame', '--first', first_frame, first_frame_seg])

                args = parse_args(command[2:])
                handle_video(args)

            time.sleep(2)
