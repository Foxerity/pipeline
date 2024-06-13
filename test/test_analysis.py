from pipeline_abc import Pipeline


class AnalysisModule(Pipeline):
    def setup(self):
        self.config = {}

    def __call__(self, **kwargs):
        self.analyze_results()
        self.run()

    def analyze_results(self):
        print("Analyzing results")

    def run(self, **kwargs):
        print('run something')


class VisualizationModule(Pipeline):
    def setup(self):
        self.config = {}

    def __call__(self, **kwargs):
        self.visualize_results()

    def visualize_results(self):
        print("Visualizing results")
