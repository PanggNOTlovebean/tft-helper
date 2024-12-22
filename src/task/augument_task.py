from PySide6.QtCore import QTimer

from common.exception import NoFrameException
from common.game_info import game_stage
from common.logger import log
from common.ocr import RelatetiveBoxPosition, RelativePosition
from common.signal import signal_bus
from gui.overlay_window import RankFlagItem
from task.base_task import BaseTask
import json


# 强化符文名称所在位置
AUGMENT_NAME_POSITION_TUPLE = (
    (0.2230, 0.5028, 0.3594, 0.5354),
    (0.4344, 0.5028, 0.5723, 0.5326),
    (0.6457, 0.5028, 0.7836, 0.5354),
)

# 强化符文提示显示位置
AUGMENT_RANK_POSTION_TUPLE = (
    (0.2230, 0.5028),
    (0.4344, 0.5028),
    (0.6457, 0.5028),
)


class AugumentTask(BaseTask):
    name = "强化符文"
    description = "提示强化符文等级"

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        with open('data/stat/augments.json', 'r', encoding='utf-8') as f:
            self.augment_rank_map = json.load(f)
            log.info(f"读取强化符文数据 共计{len(self.augment_rank_map)}个")
  
        signal_bus.game_task_signal.connect(self.on_game_stage_change)

    def on_game_stage_change(self):
        if game_stage in ("2-1", "3-2", "4-2"):
            if not self.timer.isActive():
                self.timer.start(1000)  # 每秒检查一次
        else:
            self.timer.stop()

    def run(self):
        try:
            # 检查海克斯是否存在 游戏上方出现 选择一件 标识
            CHECK_HEX_POSITION = RelatetiveBoxPosition(0.454, 0.183, 0.547, 0.231)
            ocr_result = self.ocr(CHECK_HEX_POSITION)

            if "择" not in ocr_result:
                self.timer.stop()
                self.clear_rank_items()
                log.info('强化符文选择结束')
                return

            log.info("选择强化符文")
            for ocr_position, tier_position in zip(AUGMENT_NAME_POSITION_TUPLE, AUGMENT_RANK_POSTION_TUPLE):
                ocr_result = self.ocr(RelatetiveBoxPosition(*ocr_position))
                # 后处理 修复识别错误
                ocr_result = ocr_result.replace('I川', 'III').replace('ⅡI', 'II')
                log.info(f"强化符文: {ocr_result}")

                rank = self.augment_rank_map.get(ocr_result, '?')
                if rank == '?':
                    log.error(f"未获取到强化符文等级: {ocr_result}")

                self.add_rank_item(RankFlagItem(position=RelativePosition(*tier_position), rank=rank, duration=3))

        except NoFrameException as e:
            log.error(e)
        except Exception as e:
            log.exception(e)



if __name__ == "__main__":
    task = AugumentTask()
