from PySide6.QtCore import Qt
from PySide6.QtWidgets import QHBoxLayout, QWidget
from qfluentwidgets import FluentIcon, PushButton, SwitchButton, ExpandSettingCard, SwitchSettingCard
from common.signal import signal_bus
from task.base_task import BaseTask


class TaskCard(SwitchSettingCard):
    def __init__(self, task: BaseTask, parent: QWidget):
        super().__init__(icon=FluentIcon.GAME, title=task.name, content=task.description, parent=parent)
        self.task = task
        self.config = task.config
        self.configItem = self.config.enabled
