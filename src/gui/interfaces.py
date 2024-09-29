from PySide6.QtWidgets import QWidget, QFrame
from task.base_task import BaseTask
from gui.cards import TaskCard
from qfluentwidgets import FlowLayout, ExpandLayout, ScrollArea
from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, SplitFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont)
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFrame, QHBoxLayout, QVBoxLayout

class TaskInterface(QFrame):
    def __init__(self, task_list: list[BaseTask] = [], parent: QWidget = None):
        super().__init__(parent=parent)
        self.vBoxLayout = QVBoxLayout(self)

        self.vBoxLayout.setSpacing(6)
        self.vBoxLayout.setContentsMargins(30, 60, 30, 30)
        self.vBoxLayout.setAlignment(Qt.AlignTop)

        self.task_list = task_list
        self.task_cards = []
        for task in self.task_list:
            self.task_cards.append(TaskCard(task, self))
        
        for card in self.task_cards:
            self.vBoxLayout.addWidget(card)
        
        self.setObjectName("TaskTab")