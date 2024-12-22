import re
import sys
import threading
import time

import pythoncom
from PySide6.QtWidgets import QApplication

from common.exception import NoFrameException
from common.game_info import game_stage
from common.logger import log
from common.ocr import RelatetiveBoxPosition
from task.base_task import BaseTask


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
        sleep_time = 1
        while True:
            try:
                # 阶段位置
                frame = self.capturer.do_get_frame()
                position = RelatetiveBoxPosition(0.38, 0, 0.45, 0.04)
                ocr_result = self.ocr(position, frame)
                # 后处理 只接受数字和字符
                ocr_result = re.sub(r'[^0-9-]', '', ocr_result)
                game_stage.update(ocr_result)
                #TODO 通过cv识别进度条优化睡眠时间

                # 时间位置
                # position = RelatetiveBoxPosition(0.5195, 0.0000, 0.6258, 0.0389)
                # ocr_result = self.ocr(position, frame)
                # 后处理 只接受数字
                # ocr_result = re.sub(r'[^0-9]', '', ocr_result)
                # if ocr_result.isdigit() and int(ocr_result) > 2:
                #     sleep_time = int(ocr_result) - 1
                #     log.info(f'更新睡眠时间 {sleep_time}')
            except NoFrameException as e:
                log.error(e)
            except Exception as e:
                log.exception(e)
            time.sleep(sleep_time)
            sleep_time = 1


if __name__ == "__main__":
    # 调试时启动pyside application
    app = QApplication(sys.argv)
    game_stage_task = GameStageTask()
    # 等待主动结束
    sys.exit(app.exec())
