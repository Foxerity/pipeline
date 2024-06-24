from abc import ABC, abstractmethod
from colorama import Fore, Style, init

from pipeline_abc import Pipeline
init(autoreset=True)


class Callback(Pipeline):
    def __init__(self):
        super().__init__()
        self.BLACK = Fore.BLACK
        self.RED = Fore.RED
        self.GREEN = Fore.GREEN
        self.YELLOW = Fore.YELLOW
        self.BLUE = Fore.BLUE
        self.RESET = Fore.RESET
        self.color = {
            'r': self.RED,
            'g': self.GREEN,
            'b': self.BLUE,
            'y': self.YELLOW,
            0: self.RESET
        }

    @abstractmethod
    def init_run(self, **kwargs):
        raise NotImplementedError

    def before_run(self):
        pass

    def after_run(self):
        pass
