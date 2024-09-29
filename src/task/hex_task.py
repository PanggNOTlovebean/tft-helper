import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(1, str(Path(__file__).parent.parent))

from task.base_task import BaseTask
from common.logger import log
from common.game_info import game_stage
# 识别海克斯
class HexTask(BaseTask):
    def __init__(self, name, description):
        super().__init__(name, description)
        
    def run(self):
        log.info(f"Running {self.name}")