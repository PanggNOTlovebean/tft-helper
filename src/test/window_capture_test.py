import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent.parent))

import cv2
from datetime import datetime
from time import sleep, time
from common.logger import log
from ..capture.hwnd_window import HwndWindow

from ..capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod


hwnd = HwndWindow('League of Legends (TM) Client')
capture = WindowsGraphicsCaptureMethod(hwnd)
while True:
    sleep(1)
    mat = capture.do_get_frame()
    if mat is not None:
        # 获取时间戳 ms格式
        timestamp = int(time())
        cv2.imwrite(f'record/record_{timestamp}.png', mat)
        log.info(mat.shape)