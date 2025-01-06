import sys

from PySide6.QtWidgets import QApplication

from gui.tft_table import TFTTable
from task.base_task import BaseTask

import cv2

from common.logger import log
from common.ocr import RelatetiveBoxPosition
from task.base_task import BaseTask
from PySide6.QtCore import QTimer
from time import sleep


# 装备提示
class ItemTask(BaseTask):
    name = "装备提示任务"
    description = ""

    def __init__(self):
        super().__init__()
        self.open_status = False
        self.template = cv2.imread("data/template/is_look_unit.bmp")
        # TODO 延迟启动 这里不知道为什么 不延迟的话 会读不了帧
        sleep(1)

        # 初始化 QApplication 和 TFTTable
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.table = TFTTable()

        # 使用 QTimer 替代线程
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(100)  # 20ms 相当于之前的 sleep_time = 0.02

        # 添加测试数据
        self.init_test_data()
    def init_test_data(self):
        test_data = [
            (["data/item/TFT_Item_Bloodthirster.jpg"] * 3, 2.34, -1.92, 0.5),
            (["data/item/TFT_Item_Bloodthirster.jpg"] * 3, 2.34, -1.92, 0.5),
            (["data/item/TFT_Item_Bloodthirster.jpg"] * 3, 2.34, -1.92, 0.5),
            (["data/item/TFT_Item_Bloodthirster.jpg"] * 3, 2.34, -1.92, 0.5),
            (["data/item/TFT_Item_Bloodthirster.jpg"] * 3, 2.34, -1.92, 0.5),
        ]

        for row, (icons, avg_place, change, rate) in enumerate(test_data):
            self.table.set_item_data(row, icons, avg_place, change, rate)
            self.table.set_single_item_data(row, icons[0], avg_place, change, rate)

    def run(self):
        """主运行逻辑"""
        try:
            frame = self.capturer.get_frame()
            if frame is None:
                raise Exception('获取不到画面')

            position = RelatetiveBoxPosition(0.925, 0.683, 0.954, 0.711)
            new_status = self.find_image(self.template, frame, position)

            self.update_ui_status(new_status)

        except Exception as e:
            log.exception(e)

    def update_ui_status(self, new_status):
        """更新UI显示状态"""
        if new_status and not self.open_status:
            self.open_status = True
            log.info('打开英雄详情')
            self.table.show()
        elif not new_status and self.open_status:
            self.open_status = False
            log.info('关闭英雄详情')
            self.table.hide()

    def start(self):
        """启动定时器"""
        if not self.timer.isActive():
            self.timer.start(20)

    def stop(self):
        """停止定时器"""
        self.timer.stop()
        self.table.hide()
        self.open_status = False
