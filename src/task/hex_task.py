from PySide6.QtCore import QTimer

from task.base_task import BaseTask
from common.ocr import ocr
from common.logger import log
from common.game_info import game_stage
from common.signal import signal_bus
import time
import pythoncom
from common.ocr import RelatetiveBoxPosition


# 识别海克斯
class HexTask(BaseTask):
    name = "海克斯任务"
    description = "识别海克斯"

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_hex)
        signal_bus.game_task_signal.connect(self.on_game_stage_change)
        
    def on_game_stage_change(self):
        if game_stage in ("2-1", "3-2", "4-2"):
            if not self.timer.isActive():
                self.timer.start(1000)  # 每秒检查一次
        else:
            self.timer.stop()

    def check_hex(self):
        try:
            # 检查海克斯是否存在 游戏上方出现 选择一件 标识
            CHECK_HEX_POSITION = RelatetiveBoxPosition(0.454, 0.183, 0.547, 0.231)
            ocr_result = self.ocr(CHECK_HEX_POSITION)
            
            if "择" not in ocr_result:
                self.timer.stop()
                log.info('海克斯选择结束')
                return

            log.info("选择海克斯")
            HEX_NAME_POSITION_TUPLE = (
                (0.213, 0.494, 0.368, 0.536),
                (0.440, 0.492, 0.581, 0.540),
                (0.647, 0.492, 0.790, 0.539),
            )
            
            for position in HEX_NAME_POSITION_TUPLE:
                ocr_result = self.ocr(RelatetiveBoxPosition(*position))
                log.info(f"海克斯天赋: {ocr_result}")
                
        except Exception as e:
            log.exception(e)


if __name__ == "__main__":
    task = HexTask()
