from capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from task.base_task import BaseTask
from common.logger import log
from common.game_info import game_stage
from common.ocr import RelatetiveBoxPosition
import threading
import time
import pythoncom
import cv2
from gui.overlay_window import DrawItem
from PySide6.QtWidgets import QApplication
import sys
import re
from gui.overlay_window import BoxTextItem
# 装备提示
class ItemTask(BaseTask):
    name = "装备提示任务"
    description = ""
    def __init__(self):
        super().__init__()
        self.open_status = False
        self.template = cv2.imread("../data/template/is_look_unit.bmp")
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()
    
    def run(self):
        pythoncom.CoInitialize()
        sleep_time = 0.02
        while True:
            try:
                # 判断是否打开英雄详情
                frame = self.capturer.get_frame()
                if frame is None:
                    raise Exception('获取不到画面')
                position = RelatetiveBoxPosition(0.925, 0.683, 0.954, 0.711)
                new_status = self.find_image(self.template, frame, position)
                if new_status and not self.open_status:
                    self.open_status = True
                    log.info('打开英雄详情')
                elif not new_status and self.open_status:
                    self.open_status = False
                    log.info('关闭英雄详情')
            except Exception as e:
                log.exception(e)
            time.sleep(sleep_time)
