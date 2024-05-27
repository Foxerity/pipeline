import importlib
from abc import ABC, abstractmethod
from callback.callback import Callback
from typing import List, Dict, Any

import yaml


class Pipeline(ABC):
    """
    基类：
        __init__:可以被重写，选择手动创建Pipeline还是从文件中构建
        setup   :必须被重写，初始化项目的必须方法
        run     :可以被重写，默认链式执行全部的核心子模块（带__call__。不带默认为工具类或非Pipeline主链路上的模块）
        from_configfile:可以被重写，从文件构建出Pipeline的方法
        save_configfile:可以被重写，从Pipeline保存为文件的方法
        get_executable_modules:可以被重写，获取Pipeline上的主要模块（带__call__）
    """
    def __init__(self, config_file=None):
        """
        :param config_file: 配置文件
        """
        self.config = {}
        self.modules = []
        if config_file:
            self.from_configfile(config_file)

    @abstractmethod
    def setup(self, **kwargs):
        raise NotImplementedError

    def run(self, callbacks=None, **kwargs):
        """
        :param callbacks:   需要被挂载的Callback列表
        :param kwargs:      参数适配
        :return:            None
        """
        for module in self.modules:
            for callback in callbacks or []:
                callback.before_run()
            if hasattr(module, '__call__'):
                module(**kwargs)
            for callback in callbacks or []:
                callback.after_run()

    def from_configfile(self, config_file):
        """
        :param config_file:     配置文件
        :return:                None
        """
        with open(config_file, 'r') as file:
            loaded_config = yaml.safe_load(file)
            loaded_config = self._deserialize_config(loaded_config)
        root_module = self._load_module_config(loaded_config)
        self.config = root_module.config
        self.modules = root_module.modules

    def save_configfile(self, config_file):
        """
        :param config_file:     配置文件
        :return:                None
        """
        config_to_save = self._get_module_config(self)
        with open(config_file, 'w') as file:
            yaml.dump(config_to_save, file)

    def get_executable_modules(self) -> List[str]:
        """
        :return:                获取Pipeline上的主要模块（带__call__）
        """
        return [module.__class__.__name__ for module in self.modules if hasattr(module, "__call__")]

    def _get_module_config(self, module) -> Dict[str, Any]:
        """
        :param module:          Pipeline上会被保存在配置文件中的模块
        :return:                配置文件dict
        """
        return {
            'module_path': module.__module__,
            'class': module.__class__.__name__,
            'config': self._serialize_config(module.config),
            'modules': [self._get_module_config(sub_module) for sub_module in getattr(module, 'modules', [])]
        }

    def _load_module_config(self, mod_config) -> "Pipeline":
        """
        :param mod_config:      从配置文件中读取到的模型配置
        :return:                从对应的配置中实例化出的模块对象
        """
        module_path = mod_config['module_path']
        module_class = mod_config['class']
        module = importlib.import_module(module_path)
        module_class = getattr(module, module_class)
        module_instance = module_class()
        module_instance.config = mod_config['config']
        module_instance.modules = [self._load_module_config(sub_module) for sub_module in mod_config.get('modules', [])]
        return module_instance

    @staticmethod
    def _serialize_config(config) -> Dict[str, Any]:
        """
        辅助yaml文件进行序列化，python中一些特殊的数据结构不能被直接序列化至文件，如tuple等。
        :param config:          配置文件格式的dict
        :return:                yaml化后的配置文件dict
        """
        serialized_config = {}
        for key, value in config.items():
            if isinstance(value, tuple):
                serialized_config[key] = {"__type__": 'tuple', "value": list(value)}
            else:
                serialized_config[key] = value
        return serialized_config

    @staticmethod
    def _deserialize_config(config) -> Dict[str, Any]:
        """
        将yaml文件中原先序列化失败的数据结构重新序列化为正确的格式。
        :param config:          配置文件格式的dict
        :return:                python化后的配置文件dict
        """
        deserialized_config = {}
        for key, value in config.items():
            if isinstance(value, dict) and '__type__' in value and value['__type__'] == "tuple":
                deserialized_config[key] = tuple(value['value'])
            else:
                deserialized_config[key] = value
        return deserialized_config
