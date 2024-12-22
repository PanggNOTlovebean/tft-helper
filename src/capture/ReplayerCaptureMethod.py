from __version__ import REPLAY_BASE_TIME, APP_START_TIME, REPALY_BASE_TIME_OFFSET
from capture.BaseWindowsCaptureMethod import BaseWindowsCaptureMethod
from capture.hwnd_window import HwndWindow
from pathlib import Path
import cv2
import time
from common.logger import log
import sys

class ReplayerCaptureMethod(BaseWindowsCaptureMethod):
    name = "回放截图文件夹"
    description = "用于本地测试"
    
    def __init__(self, hwnd_window: HwndWindow):
        super().__init__(hwnd_window)
        # 把年月日时转成时间戳
        replay_base_time = time.mktime(time.strptime(REPLAY_BASE_TIME, "%Y-%m-%d %H-%M-%S"))
        self.last_frame = None
        self.next_frame = None
        
        self.last_frame_name = ""
        self.last_frame_time = replay_base_time

        self.next_frame_name = ""
        self.next_frame_time = replay_base_time

        # 获取截图路径
        self.screenshot_path = Path("screenshot") / REPLAY_BASE_TIME

        
        # 获取文件夹列表
        self.screenshot_list = self.screenshot_path.glob("*.png")
        try:
            self.next_frame_name = next(self.screenshot_list)
            self.next_frame_time = int(self.next_frame_name.stem)
        except StopIteration:
            log.error("录像文件不存在 终止进程")
            sys.exit()
            

    def do_get_frame(self):
        current_time = time.time()
        time_diff = current_time - APP_START_TIME + REPALY_BASE_TIME_OFFSET

        if time_diff < self.next_frame_time:
            return self.last_frame

        # 更新帧
        self.last_frame_name = self.next_frame_name
        self.last_frame_time = self.next_frame_time
        self.last_frame = cv2.imread(str(self.last_frame_name))

        try:
            while True:
                self.next_frame_name = next(self.screenshot_list)
                self.next_frame_time = int(self.next_frame_name.stem)
                if self.next_frame_time > time_diff:
                    break
        except StopIteration:
            self.next_frame_name = None
        log.info(f"更新帧 {self.next_frame_name}")
        return self.last_frame
