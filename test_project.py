from pipeline_abc import Pipeline
from test.test_dataloader import DataLoader, DataCleaner, DataPreprocessor
from test.test_detection import DetectionModule1, DetectionModule2
from test.test_analysis import AnalysisModule, VisualizationModule


class ObjectDetectionProject(Pipeline):
    def setup(self):
        self.config = {
            'name': "Object Detection Project",
        }
        # 添加各个模块
        self.modules = [
            DataLoader(),
            DataCleaner(),
            DataPreprocessor(),
            DetectionModule1(),
            DetectionModule2(),
            AnalysisModule(),
            VisualizationModule()
        ]
        # 逐个设置模块
        for module in self.modules:
            module.setup()

    def run(self, **kwargs):
        for module in self.modules:
            module.run()


if __name__ == '__main__':
    # 创建并设置项目
    project = ObjectDetectionProject()
    project.setup()
    project.save_configfile('object_detection_project.yaml')

    # 从配置文件加载项目
    new_project = ObjectDetectionProject(config_file='object_detection_project.yaml')
    new_project.run()

    # 获取需要被执行的模块名称
    print("Executable methods:", new_project.get_executable_modules())
