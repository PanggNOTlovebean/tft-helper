import sys

from task.base_task import BaseTask
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (
    SplitFluentWindow,
    FluentIcon,
    FluentTranslator,
    Theme,
    setTheme,
)
from gui.interfaces import TaskInterface
from task.augument_task import AugumentTask


class MainWindow(SplitFluentWindow):
    def __init__(self, task_list: list[BaseTask] = []):
        super().__init__()
        self.init_window()
        self.taskInterface = TaskInterface(task_list)
        self.init_navigation()

    def init_navigation(self):
        self.addSubInterface(self.taskInterface, icon=FluentIcon.HOME, text="任务")

    def init_window(self):
        self.resize(960, 780)
        self.setMinimumWidth(760)
        self.setWindowIcon(QIcon("data/icon/icon.png"))
        self.setWindowTitle("云顶之弈助手")

        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)


# 在主程序中使用
if __name__ == "__main__":
    setTheme(Theme.DARK)
    app = QApplication(sys.argv)

    translator = FluentTranslator()
    app.installTranslator(translator)
    task_list = [AugumentTask() for _ in range(3)]
      
    window = MainWindow(task_list)
    window.show()
    sys.exit(app.exec())
