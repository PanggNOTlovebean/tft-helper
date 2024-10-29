from capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from task.base_task import BaseTask
from common.logger import log
from common.game_info import game_stage
from common.ocr import RelatetivePosition
import threading
import time
import pythoncom
import cv2 

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
        while True:
            try:
                frame = self.capturer.get_frame()
                stage_position = RelatetivePosition(0.38, 0, 0.44, 0.04)
                cropped_frame = stage_position.get_cropped_frame(frame)
                ocr_result = self.ocr_line(cropped_frame)
                game_stage.update(ocr_result)
            except Exception as e:
                log.exception(e)
            time.sleep(1)


if __name__ == "__main__":
    game_stage_task = GameStageTask()
    # 等待主动结束
    while True:
        time.sleep(1)
