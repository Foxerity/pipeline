import yaml
import importlib
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from callback.callback import Callback


class Pipeline(ABC):
    """
    1、在Pipeline中，项目所有的模块必须继承自Pipeline以便统一的管理。
    2、在项目流程图中承担项目主要功能的模块被称为主要模块。
    3、用于主要模块的一些工具类、Hook、测试模块等非核心功能模块被称为次要模块。
    4、Pipeline默认通过__call__方法来区分主次模块。主要模块必须实现__call__方法。
    5、所有的模块都有run方法，run方法承担具体的执行功能，而__call__代表暴露模块接口和逻辑，可以接受调用或者调用其他模块。
    6、主模块需要承担Pipeline的前后连接，所以必须暴露接口，但不是所有模块都希望将接口暴露给所有其他模块。（比如工具类），
       未实现__call__方法的模块会在初始化时被隐藏，只被其约定的模块私有调用。而所有__call__方法会被统一收集、链接、执行。
    基类：
        def __init__:可以被重写，选择手动创建Pipeline还是从文件中构建
        def setup   :必须被重写，初始化项目的必须方法
        def run     :可以被重写，默认顺序执行全部的核心模块（带__call__。不带默认为工具类或非Pipeline主链路上的模块）
        def from_configfile:可以被重写，从文件构建出Pipeline的方法
        def save_configfile:可以被重写，从Pipeline保存为文件的方法
        def get_executable_modules:可以被重写，获取Pipeline上的主要模块（带__call__）
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

    def run(self, callbacks: Callback = None, **kwargs):
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
            elif hasattr(module, 'run'):
                module.run(**kwargs)
            for callback in callbacks or []:
                callback.after_run()

    def from_configfile(self, config_file):
        """
        :param config_file:     配置文件
        :return:                None
        """
        if isinstance(config_file, list):
            loaded_config = self._merge_yaml_files(config_file)
        elif isinstance(config_file, str):
            with open(config_file, 'r') as file:
                loaded_config = yaml.safe_load(file)
                loaded_config = self._deserialize_config(loaded_config)
        else:
            raise TypeError('Config_file must be list or str')
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
            yaml.dump(config_to_save, file, indent=4, default_flow_style=False)

    def get_executable_modules(self) -> List[str]:
        """
        :return:                获取Pipeline上的主要模块（带__call__）
        """
        return [module.__class__.__name__ for module in self.modules if hasattr(module, "__call__")]

    def initialize_modules(self):
        for module in self.modules:
            # 获取类名
            class_name = module.__class__.__name__
            # 转换为小写的类名
            class_name_lower = class_name.lower()
            # 将模块实例赋值给self的属性
            setattr(self, class_name, module)
            setattr(self, class_name_lower, module)

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

    @staticmethod
    def _merge_yaml_files(input_files: List[str]) -> Dict[str, Any]:
        """
        合并多个子模块的 YAML 文件
        :param input_files:     子模块的 YAML 文件列表
        :return:                合并后的配置字典
        """
        assert input_files is not None, ValueError("The input_files list should not be empty.")
        with open(input_files[0], 'r') as f:
            merged_config = yaml.safe_load(f)

        for file in input_files[1:]:
            with open(file, 'r') as f:
                config = yaml.safe_load(f)
                merged_config['modules'].append(config)

        return merged_config
