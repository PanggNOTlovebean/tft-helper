from PySide6.QtCore import QTimer

from task.base_task import BaseTask, capture
from common.ocr import ocr
from common.logger import log
from common.game_info import game_stage
# 识别海克斯
class HexTask(BaseTask):
    name = "海克斯任务"
    description = "识别海克斯"
    def __init__(self):
        super().__init__()
        # 使用QTimer 每隔1s 运行一次
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.run)
        self.timer.start(1000)

    def run(self):
        mat = capture.do_get_frame()
        log.info(f"Running {self.name}")

if __name__ == '__main__':
    task = HexTask()
    
