from pipeline_abc import Pipeline
from test.sub.test_submodule import SubModule


class DetectionModule1(Pipeline):
    def setup(self):
        self.config = {
            'name': 'YOLOv5',
            'mode': 'train',  # train or inference
            'params': {}
        }
        self.modules = [
            SubModule()
        ]
        for module in self.modules:
            module.setup()

    def __call__(self, **kwargs):
        self.run()

    def run(self, **kwargs):
        print(f"Running {self.config['name']} in {self.config['mode']} mode with parameters {self.config['params']}")
        for module in self.modules:
            module.run()


class DetectionModule2(Pipeline):
    def setup(self):
        self.config = {
            'name': 'FasterRCNN',
            'mode': 'inference',  # train or inference
            'params': {}
        }

    def __call__(self, **kwargs):
        self.run_detection()

    def run_detection(self):
        print(f"Running {self.config['name']} in {self.config['mode']} mode with parameters {self.config['params']}")
