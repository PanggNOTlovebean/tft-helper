import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(1, str(Path(__file__).parent.parent))

from task.base_task import BaseTask
from common.logger import log
from common.game_info import game_stage
# 识别游戏阶段
class GameStageTask(BaseTask):
    name = "识别游戏阶段"
    description = ""
    def __init__(self):
        super().__init__()
        
    def run(self):
        log.info(f"Running {self.name}")

if __name__ == "__main__":
    game_stage_task = GameStageTask()
    game_stage_task.run()

