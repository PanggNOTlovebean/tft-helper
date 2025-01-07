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
        # sleep(1)

        # 加载装备数据
        self.unit_items = self.load_unit_items()

        # 初始化 QApplication 和 TFTTable
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.table = TFTTable()

        # 使用 QTimer 替代线程
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        self.timer.start(100)  # 20ms 相当于之前的 sleep_time = 0.02
        
        # 当前查看的英雄名称
        # 避免重复获取装备数据
        self.unit_name = None

    def run(self):
        """主运行逻辑"""
        if not self.is_executable():
            return
        try:
            frame = self.capturer.get_frame()
            if frame is None:
                raise Exception('获取不到画面')
            # 通过英雄详情页面 生命偷取图标来判断
            position = RelatetiveBoxPosition(0.925, 0.683, 0.954, 0.711)
            new_status = self.find_image(self.template, frame, position)

            self.update_ui_status(new_status, frame)

        except Exception as e:
            log.exception(e)

    def update_table_data(self, unit_name):
        """更新表格数据"""
        if unit_name and unit_name != self.unit_name:
            log.info(f'识别到英雄：{unit_name}')
            # 获取该英雄的装备数据
            items_data = self.get_unit_items(unit_name)
            if items_data:
                # 更新推荐装备数据
                for idx, build in enumerate(items_data["recommended_builds"]):
                    icons = [f"data/items/{item}.png" for item in build["items"]]
                    self.table.set_combined_items_data(
                        idx, 
                        icons,
                        build.get("avg_place",'?'),
                        build.get("place_change", '?'),
                        build.get("play_rate", '?')
                    )
                
                # 更新单件装备数据
                for idx, item in enumerate(items_data["top_items"]):
                    self.table.set_single_item_data(
                        idx,
                        f"data/items/{item.get('name')}.png",
                        item.get("avg_place", '?'),
                        item.get("place_change", '?'),
                        item.get("play_rate",'?')
                    )
            else:
                log.error(f'获取装备数据失败: {unit_name}')
            self.unit_name = unit_name

    def update_ui_status(self, new_status, frame=None):
        """更新UI显示状态"""
        if new_status and not self.open_status:
            self.open_status = True
            log.info('打开英雄详情')
            if frame is not None:
                position = RelatetiveBoxPosition(0.8863, 0.2944, 0.9512, 0.3187)
                unit_name = self.ocr(position, frame)
                self.update_table_data(unit_name)
                self.table.show_toggle_button()

        if new_status and self.open_status:
            
            if frame is not None:
                position = RelatetiveBoxPosition(0.8863, 0.2944, 0.9512, 0.3187)
                unit_name = self.ocr(position, frame)
                if unit_name != self.unit_name:
                    log.info('切换英雄')
                    self.update_table_data(unit_name)
            
        elif not new_status and self.open_status:
            self.open_status = False
            log.info('关闭英雄详情')
            self.table.hide_toggle_button()

    def start(self):
        """启动定时器"""
        if not self.timer.isActive():
            self.timer.start(20)

    def stop(self):
        """停止定时器"""
        self.timer.stop()
        self.table.hide()
        self.open_status = False

    def load_unit_items(self):
        """
        加载英雄装备数据
        返回格式: {
            "英雄名": {
                "recommended_builds": [
                    {
                        "items": [{"id": "装备ID"}, ...],
                        "avg_place": 平均名次,
                        "change": 变化值,
                        "win_rate": 胜率
                    },
                    ...
                ],
                "top_items": [
                    {
                        "id": "装备ID",
                        "avg_place": 平均名次,
                        "change": 变化值,
                        "win_rate": 胜率
                    },
                    ...
                ]
            }
        }
        """
        try:
            import json
            with open("data/stat/unit_items.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            log.error(f"加载英雄装备数据失败: {e}")
            return {}

    def get_unit_items(self, unit_name):
        """获取指定英雄的装备数据"""
        return self.unit_items.get(unit_name)
