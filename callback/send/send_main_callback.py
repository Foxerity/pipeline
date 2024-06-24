from datetime import datetime

from callback.callback import Callback


class SendMainCallback(Callback):
    def __init__(self):
        super().__init__()
        self.class_name = None
        self.filename = None

    def setup(self, class_name, **kwargs):
        self.class_name = class_name
        date_str = datetime.now().strftime("%m%d")
        self.filename = rf"callback/log/{date_str}.txt"

    def init_run(self, modules, queue_dict, **kwargs):
        modules = [module.__class__.__name__ for module in modules]
        messages = (
                    f"Initialized modules {modules}.",
                    f"Initialized Queues dict {len(queue_dict.items())}."
                    )
        self.f_print(messages, self.color['g'])

    def before_run(self, module=None):
        module = module.__class__.__name__
        message = (
                    f"Starting modules {module}.",
                    )
        self.f_print(message, self.color['b'])

    def after_run(self, module=None):
        module = module.__class__.__name__
        messages = (
                    f"Started modules {module}.",
                    )
        self.f_print(messages, self.color['r'])

    def f_print(self, messages=(), color=None):
        color = color if color is not None else ''
        with open(self.filename, "a") as file:
            for message in messages:
                print(f"{color}[{self.class_name}]: {self.color[0]}{message}")
                timestamp = datetime.now().strftime("%H:%M:%S")

                file.write(f"[{timestamp}] [{self.class_name}]: {message}\n")

