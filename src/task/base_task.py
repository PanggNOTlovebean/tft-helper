# 添加抽象类BaseTask
from abc import ABC, abstractmethod
from qfluentwidgets import QConfig, ConfigItem, BoolValidator

from common.task_config import TaskConfig

class BaseTask(ABC):
    name :str = "任务抽象基类"
    description :str = ""
    def __init__(self, config: TaskConfig = TaskConfig()):
        self.config = config
    
    @abstractmethod
    def run(self):
        pass

    def enable(self):
        self.config.set(self.config.enabled, True)

    def disable(self):
        self.config.set(self.config.enabled, False)

    def is_enabled(self):
        return self.config.get(self.config.enabled)
    


