import cv2
from PySide6.QtCore import QTimer

from common.exception import NoFrameException
from common.game_info import game_stage
from common.logger import log
from common.ocr import RelatetiveBoxPosition, RelativePosition
from common.signal import signal_bus
from gui.overlay_window import RankFlagItem
from task.base_task import BaseTask
import json

from enum import Enum
import numpy as np

# 强化符文图标所在位置
AUGMENT_ICON_POSITION_TUPLE = (
    (0.2488, 0.3104, 0.3324, 0.4514),
    (0.4590, 0.3132, 0.5465, 0.4514),
    (0.6684, 0.3174, 0.7598, 0.4389)
)

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


# 强化符文等级
class AugmentLevel(Enum):
    PRISMATIC = ("棱彩", 3)
    SILVER = ("白银", 2)
    GOLD = ("黄金", 1)

    def get_level_num(self):
        return self.value[1]


class AugumentTask(BaseTask):
    name = "强化符文"
    description = "提示强化符文等级"

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.load_augment_data()
        signal_bus.game_task_signal.connect(self.on_game_stage_change)
        self.level = None

    def load_augment_data(self):
        """加载强化符文数据"""
        with open('data/stat/augments.json', 'r', encoding='utf-8') as f:
            self.augment_rank_map = json.load(f)
            log.info(f"读取强化符文数据 共计{len(self.augment_rank_map)}个")

    def on_game_stage_change(self):
        """处理游戏阶段变化信号"""
        if game_stage in ("2-1", "3-2", "4-2"):
            self.start()
        else:
            self.stop()

    def start(self):
        """启动定时器，每秒检查一次"""
        if not self.timer.isActive():
            self.timer.start(1000)

    def stop(self):
        """停止定时器并重置等级"""
        self.timer.stop()
        self.level = None

    def run(self):
        """主运行逻辑，获取帧并处理强化符文"""
        try:
            frame = self.capturer.do_get_frame()
            if not self.check_label_presence(frame):
                return

            log.info("选择强化符文")
            if self.level is None:
                self.level = self.determine_augment_level(frame)

            self.process_augment_names()

        except NoFrameException as e:
            log.error(e)
        except Exception as e:
            log.exception(e)

    def check_label_presence(self, frame):
        """检查标签是否存在，最多尝试3次"""
        no_label_count = 0
        while no_label_count <= 3:
            CHECK_HEX_POSITION = RelatetiveBoxPosition(0.454, 0.183, 0.547, 0.231)
            ocr_result = self.ocr(CHECK_HEX_POSITION)

            if "择" not in ocr_result:
                no_label_count += 1
                if no_label_count >= 3:
                    self.timer.stop()
                    self.clear_rank_items()
                    log.info('强化符文选择结束')
                    return False
            else:
                break
        return True

    def determine_augment_level(self, frame):
        """确定强化符文的等级"""
        icon_position = AUGMENT_ICON_POSITION_TUPLE[0]
        cropped_frame = RelatetiveBoxPosition(*icon_position).get_cropped_frame(frame)
        hsv_frame = cv2.cvtColor(cropped_frame, cv2.COLOR_BGR2HSV)

        if self.is_prismatic(hsv_frame):
            log.info("识别为棱彩阶符文")
            return AugmentLevel.PRISMATIC
        elif self.is_gold(hsv_frame):
            log.info("识别为黄金阶符文")
            return AugmentLevel.GOLD
        else:
            log.info("识别为白银阶符文")
            return AugmentLevel.SILVER

    def is_prismatic(self, hsv_frame):
        """检查是否为棱彩阶符文"""
        return self.is_color_above_threshold(hsv_frame[:, :, 2], 240, 0.15)

    def is_gold(self, hsv_frame):
        """检查是否为黄金阶符文"""
        return self.is_color_below_threshold(hsv_frame[:, :, 0], 50, 0.1)

    def is_color_above_threshold(self, channel, threshold, ratio):
        """检查颜色通道是否超过阈值"""
        count = np.sum(channel > threshold)
        return (count / channel.size) > ratio

    def is_color_below_threshold(self, channel, threshold, ratio):
        """检查颜色通道是否低于阈值"""
        count = np.sum(channel < threshold)
        return (count / channel.size) > ratio

    def process_augment_names(self):
        """处理强化符文名称并记录等级"""
        for ocr_position, tier_position in zip(AUGMENT_NAME_POSITION_TUPLE, AUGMENT_RANK_POSTION_TUPLE):
            ocr_result = self.ocr(RelatetiveBoxPosition(*ocr_position))
            aug_name = self.post_process_ocr_result(ocr_result)
            rank = self.augment_rank_map.get(aug_name, '?')
            log.info(f"强化符文: {aug_name}, rank:{rank}")
            self.add_rank_item(RankFlagItem(position=RelativePosition(*tier_position), rank=rank, duration=3))

    def post_process_ocr_result(self, ocr_result):
        """后处理OCR结果，清理不必要的字符,增加额外后缀"""
        aug_name = ''.join(char for char in ocr_result if ('\u4e00' <= char <= '\u9fff' or char in '+CD') and char != '川')
        if aug_name not in self.augment_rank_map:
            aug_name = self.append_level_suffix(aug_name)
        return aug_name

    def append_level_suffix(self, aug_name):
        """根据当前等级为强化符文名称添加后缀"""
        level_suffix_map = {
            AugmentLevel.PRISMATIC: 'III',
            AugmentLevel.GOLD: 'II',
            AugmentLevel.SILVER: 'I'
        }
        suffix = level_suffix_map.get(self.level)
        if suffix:
            aug_name += suffix
            if aug_name not in self.augment_rank_map:
                aug_name = aug_name[:-1]
        return aug_name


if __name__ == "__main__":
    task = AugumentTask()
