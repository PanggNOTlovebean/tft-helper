from capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from task.base_task import BaseTask
from common.logger import log
from common.game_info import game_stage
from common.ocr import RelatetiveBoxPosition
import threading
import time
import pythoncom
import cv2
from gui.overlay_window import DrawItem
from PySide6.QtWidgets import QApplication
import sys
import re
from gui.overlay_window import BoxTextItem
# 识别游戏阶段
class GameStageTask(BaseTask):
    name = "识别游戏阶段"
    description = ""
    def __init__(self):
        super().__init__()
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    
    def run(self):
        pythoncom.CoInitialize()
        sleep_time = 0.5
        while True:
            try:
                # 阶段位置
                position = RelatetiveBoxPosition(0.38, 0, 0.45, 0.04)
                ocr_result = self.ocr(position)
                # 后处理 只接受数字和字符
                ocr_result = re.sub(r'[^0-9-]', '', ocr_result)
                game_stage.update(ocr_result)

                # 时间位置
                position = RelatetiveBoxPosition(0.567, 0.002, 0.617, 0.0395)
                ocr_result = self.ocr(position)
                # 后处理 只接受数字
                ocr_result = re.sub(r'[^0-9]', '', ocr_result)
                if int(ocr_result) > 2:
                    sleep_time = int(ocr_result) - 1
                    log.info(f'更新睡眠时间 {sleep_time}')
            except Exception as e:
                log.exception(e)
            time.sleep(sleep_time)
            sleep_time = 0.5


if __name__ == "__main__":
    # 调试时启动pyside application
    app = QApplication(sys.argv)
    game_stage_task = GameStageTask()
    # 等待主动结束
    sys.exit(app.exec())
