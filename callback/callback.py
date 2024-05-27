from abc import ABC, abstractmethod


class Callback(ABC):
    @abstractmethod
    def init_run(self):
        raise NotImplementedError

    def before_run(self):
        pass

    def after_run(self):
        pass
