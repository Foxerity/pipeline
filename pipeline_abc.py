import importlib
from abc import ABC, abstractmethod
from typing import List

import yaml


class Pipeline(ABC):

    def __init__(self, config_file=None):
        self.config = {}
        self.modules = []
        if config_file:
            self.from_configfile(config_file)

    @abstractmethod
    def setup(self, **kwargs):
        raise NotImplementedError

    def run(self, **kwargs):
        pass

    def from_configfile(self, config_file):
        with open(config_file, 'r') as file:
            loaded_config = yaml.safe_load(file)
        self.config = self._deserialize_config(loaded_config['config'])
        self.modules = [self._load_module_config(mod_config) for mod_config in loaded_config['modules']]

    def save_configfile(self, config_file):
        config_to_save = {
            'config': self._serialize_config(self.config),
            'modules': [self._get_module_config(module) for module in self.modules]
        }
        with open(config_file, 'w') as file:
            yaml.dump(config_to_save, file)

    def get_executable_modules(self) -> List[str]:
        return [module.__class__.__name__ for module in self.modules if hasattr(module, "__call__")]

    def _get_module_config(self, module):
        return {
            'module_path': module.__module__,
            'class': module.__class__.__name__,
            'config': self._serialize_config(module.config)
        }

    @staticmethod
    def _load_module_config(mod_config):
        module_path = mod_config['module_path']
        module_class = mod_config['class']
        module = importlib.import_module(module_path)
        module_class = getattr(module, module_class)
        module_instance = module_class()
        module_instance.config = mod_config['config']
        return module_instance

    @staticmethod
    def _serialize_config(config):
        serialized_config = {}
        for key, value in config.items():
            if isinstance(value, tuple):
                serialized_config[key] = {"__type__": 'tuple', "value": list(value)}
            else:
                serialized_config[key] = value
        return serialized_config

    @staticmethod
    def _deserialize_config(config):
        deserialized_config = {}
        for key, value in config.items():
            if isinstance(value, dict) and '__type__' in value and value['__type__'] == "tuple":
                deserialized_config[key] = tuple(value['value'])
            else:
                deserialized_config[key] = value
        return deserialized_config
