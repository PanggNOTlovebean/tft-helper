from .base_task import BaseTask
from capture.hwnd_window import HwndWindow
from capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod

class TaskExectuor:
    def __init__(self, task_list: list[BaseTask]):
        self.task_list = task_list
        self.hwnd = HwndWindow('League of Legends (TM) Client')
        self.capture = WindowsGraphicsCaptureMethod(self.hwnd)
        
    def run(self):
        for task in self.task_list:
            if task.can_run():
                task.run()