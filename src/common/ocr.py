from rapidocr_paddle import RapidOCR
import numpy as np
from common.constant import MONITOR_W, MONITOR_H
ocr = RapidOCR(det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True, min_height = 100)


class RelatetiveBoxPosition:
    '''相对盒子坐标 包括左上角和右下角坐标'''
    def __init__(self, left_top_x: int, left_top_y: int, right_bottom_x: int, right_bottom_y: int):
        self._left_top_x = left_top_x
        self._left_top_y = left_top_y
        self._right_bottom_x = right_bottom_x
        self._right_bottom_y = right_bottom_y
        
    def get_cropped_frame(self, frame: np.ndarray) -> np.ndarray:
        '''根据相对坐标裁剪图片'''
        h, w, _ = frame.shape
        left_top_x, left_top_y = (int(self._left_top_x * w), int(self._left_top_y * h))
        right_bottom_x, right_bottom_y = (int(self._right_bottom_x * w), int(self._right_bottom_y * h))
        return frame[left_top_y:right_bottom_y, left_top_x:right_bottom_x]

    def get_screen_position(self) -> tuple[int, int, int, int]:
        '''根据相对坐标获取屏幕绝对坐标'''
        left_top_x, left_top_y = (int(self._left_top_x * MONITOR_W), int(self._left_top_y * MONITOR_H))
        right_bottom_x, right_bottom_y = (int(self._right_bottom_x * MONITOR_W), int(self._right_bottom_y * MONITOR_H))
        return left_top_x, left_top_y, right_bottom_x, right_bottom_y

    def __hash__(self) -> int:
        return hash((self._left_top_x, self._left_top_y, self._right_bottom_x, self._right_bottom_y))
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelatetiveBoxPosition):
            return self._left_top_x == other._left_top_x and self._left_top_y == other._left_top_y and self._right_bottom_x == other._right_bottom_x and self._right_bottom_y == other._right_bottom_y
        return False


class RelativePosition:
    '''相对位置坐标'''
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
    
    @property
    def x(self) -> float:
        '''获取x坐标'''
        return self._x
    
    @property
    def y(self) -> float:
        '''获取y坐标'''
        return self._y
    
    def get_screen_position(self) -> tuple[int, int]:
        '''获取屏幕绝对坐标'''
        return (int(self._x * MONITOR_W), int(self._y * MONITOR_H))
    
    def __hash__(self) -> int:
        return hash((self._x, self._y))
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, RelativePosition):
            return self._x == other._x and self._y == other._y
        return False