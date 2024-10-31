from time import time
from common.logger import log

class GameStage:
    # 游戏阶段 1-1 2-1等
    first_num = 0
    second_num = 0

    # 长久不更新表示游戏已退出
    last_update_time = 0

    def update(self, stage: str) -> bool:
        first_num, second_num = map(int, stage.split('-'))
        if self.first_num != first_num or self.second_num != second_num:
            self.first_num = first_num
            self.second_num = second_num
            self.last_update_time = time()
            log.info(f'更新游戏阶段为 {self}')
            return True
        return False

    def clear(self):
        self.first_num = 0
        self.second_num = 0
        self.last_update_time = 0

    def is_valid(self):
        return self.last_update_time > 0

    def __str__(self):
        return f"{self.first_num}-{self.second_num}"

game_stage = GameStage()
