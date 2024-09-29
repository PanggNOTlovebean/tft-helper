from time import time

class GameStage:
    # 游戏阶段 1-1 2-1等
    first_num = 0
    second_num = 0

    # 长久不更新表示游戏已退出
    last_update_time = 0
    
    def update(self, first_num: int, second_num: int):
        self.first_num = first_num
        self.second_num = second_num
        self.last_update_time = time()

    def clear(self):
        self.first_num = 0
        self.second_num = 0
        self.last_update_time = 0

    def is_valid(self):
        return self.last_update_time > 0

game_stage = GameStage()
