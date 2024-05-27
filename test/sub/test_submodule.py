from pipeline_abc import Pipeline


class SubModule(Pipeline):
    def setup(self, **kwargs):
        print("SubModule.setup...")
        self.config = {
            "name": "SubModule",
            "description": "SubModule",
            "parameters": {}
        }

    def run(self, **kwargs):
        print("SubModule.run...")
