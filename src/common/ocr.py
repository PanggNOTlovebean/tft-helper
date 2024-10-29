from rapidocr_paddle import RapidOCR
import numpy as np

ocr = RapidOCR(det_use_cuda=True, cls_use_cuda=True, rec_use_cuda=True, min_height = 100)


class RelatetivePosition:
    def __init__(self, left_top_x: int, left_top_y: int, right_bottom_x: int, right_bottom_y: int):
        self._left_top_x = left_top_x
        self._left_top_y = left_top_y
        self._right_bottom_x = right_bottom_x
        self._right_bottom_y = right_bottom_y

    def get_cropped_frame(self, frame: np.ndarray) -> np.ndarray:
        h, w, _ = frame.shape
        left_top_x, left_top_y = (int(self._left_top_x * w), int(self._left_top_y * h))
        right_bottom_x, right_bottom_y = (int(self._right_bottom_x * w), int(self._right_bottom_y * h))
        return frame[left_top_y:right_bottom_y, left_top_x:right_bottom_x]
