'''
回放测试    
'''

import cv2
import time

from ..capture.ReplayerCaptureMethod import ReplayerCaptureMethod

import cv2
from datetime import datetime
from time import sleep, time
from common.logger import log
from ..capture.hwnd_window import HwndWindow



hwnd = HwndWindow('League of Legends (TM) Client')
capture = ReplayerCaptureMethod(hwnd)
while True:
    sleep(1)
    mat = capture.do_get_frame()
    if mat is not None:
        # 获取时间戳 ms格式
        timestamp = int(time())
        cv2.imwrite(f'record/record_{timestamp}.png', mat)