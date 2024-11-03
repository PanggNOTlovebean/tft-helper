from abc import ABC, abstractmethod
from qfluentwidgets import QConfig, ConfigItem, BoolValidator
import numpy as np
from __version__ import DEBUG_MODE, LOL_PROCESS_NAME, REPLAY_MODE
from typing import Protocol
from rapidocr_paddle import RapidOCR
from common.ocr import ocr
from common.exception import NoFrameException
from common.task_config import TaskConfig
from capture.hwnd_window import HwndWindow
from capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod
from capture.ReplayerCaptureMethod import ReplayerCaptureMethod
from capture.BaseCaptureMethod import BaseCaptureMethod 
from common.logger import log
from common.ocr import RelatetiveBoxPosition
from gui.overlay_window import DrawItem, OverlayWindow, BoxTextItem

class BaseTask(ABC):
    name = ''
    description = ''
    hwnd: HwndWindow = HwndWindow(LOL_PROCESS_NAME)
    capturer: BaseCaptureMethod = (
        WindowsGraphicsCaptureMethod(hwnd)
        if not REPLAY_MODE
        else ReplayerCaptureMethod(hwnd)
    )
    ocr_line_model: RapidOCR = ocr
    _overlay_window = None  # 添加类级别的静态变量
    def __init__(self, config: TaskConfig = TaskConfig()):
        self.config = config
        if BaseTask._overlay_window is None:
            BaseTask._overlay_window = OverlayWindow()
            BaseTask._overlay_window.show()
        self.overlay_window = BaseTask._overlay_window

    def run(self): ...

    def is_executable(self) -> bool:
        return self.hwnd.is_open
    
    def ocr(self, position: RelatetiveBoxPosition, frame: np.ndarray = None, ocr_line = True) -> str:
        if frame is None:
            frame = self.capturer.do_get_frame()
        cropped_frame = position.get_cropped_frame(frame)
        ocr_result = self.ocr_line(cropped_frame)
        if DEBUG_MODE:
            box_text_item = BoxTextItem(position=position, text=ocr_result, duration=2)
            self.overlay_window.add_box_item(box_text_item)
        return ocr_result
    
    def ocr_line(self, frame: np.ndarray) -> str:
        '''
        识别单行文本
        '''
        ocr_result = self.ocr_line_model(frame)
        try:
            parsed_result = ocr_result[0][0][1]
        except Exception as e:
            log.warning('ocr 识别失败 返回空字符串')
            return ''
        return parsed_result
    
    def enable(self):
        self.config.set(self.config.enabled, True)

    def disable(self):
        self.config.set(self.config.enabled, False)

    def is_enabled(self):
        return self.config.get(self.config.enabled)

    def add_overlay_box_item(self, item: BoxTextItem):
        self.overlay_window.add_box_item(item)
