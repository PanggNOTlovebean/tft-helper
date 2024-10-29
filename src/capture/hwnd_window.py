import threading
import time

from win32 import win32gui
from common.logger import log
from common.meta_class import SingletonMeta
class HwndWindow(metaclass=SingletonMeta):
    def __init__(self, title):
        self.hwnd = None
        self.title = title
        self.thread = threading.Thread(target=self.update_hwnd, daemon=True)
        self.thread.start()

    def update_hwnd(self):
        while True:
            log.debug("定时更新游戏窗口")
            hwnd = win32gui.FindWindow(None, self.title)
            self.hwnd = None if hwnd == 0 else hwnd
            if self.hwnd is None:
                log.warning(f"游戏窗口不存在")
            else:
                log.debug(f"游戏窗口获取成功 hwnd:{self.hwnd}")
            time.sleep(1)

    @property
    def is_open(self) -> bool:
        return (
            self.hwnd is not None
            and win32gui.IsWindowVisible(self.hwnd)
            and win32gui.GetForegroundWindow() == self.hwnd
        )

    @property
    def exists(self):
        return self.hwnd is not None
    
