import os
import urllib

from pipeline_abc import Pipeline


class DataLoader(Pipeline):
    def setup(self):
        self.config = {
            'source': 'online',  # online or local
            'path': 'data/dataset.zip'
        }

    def __call__(self, **kwargs):
        self.get_data()

    def get_data(self):
        if self.config['source'] == 'online':
            self.download_data(self.config['path'])
        elif self.config['source'] == 'local':
            self.load_local_data(self.config['path'])

    def download_data(self, url):
        local_filename = url.split('/')[-1]
        print(f"Downloading data from {url} to {local_filename}")
        urllib.request.urlretrieve(url, local_filename)
        print("Data downloaded and processed")

    def load_local_data(self, path):
        if os.path.exists(path):
            print(f"Loading data from local path {path}")
        else:
            raise FileNotFoundError(f"Data file not found at {path}")


class DataCleaner(Pipeline):
    def setup(self):
        self.config = {
            'cleaning_params': {}
        }

    def __call__(self, **kwargs):
        self.clean_data()

    def clean_data(self):
        print("Cleaning data with parameters", self.config['cleaning_params'])


class DataPreprocessor(Pipeline):
    def setup(self):
        self.config = {
            'resize': (256, 256),
            'augmentation': True
        }

    def __call__(self, **kwargs):
        self.preprocess_data()

    def preprocess_data(self):
        print(f"Preprocessing data with resize {self.config['resize']} and augmentation {self.config['augmentation']}")
