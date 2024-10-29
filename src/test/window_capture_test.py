import cv2
from datetime import datetime
from time import sleep, time
from common.logger import log
from capture.hwnd_window import HwndWindow
from capture.WindowsGraphicsCaptureMethod import WindowsGraphicsCaptureMethod


if __name__ == '__main__':
    hwnd = HwndWindow('League of Legends (TM) Client')
    capture = WindowsGraphicsCaptureMethod(hwnd)
    while True:
        mat = capture.do_get_frame()
        if mat is not None:
            # 获取时间戳 ms格式
            timestamp = int(time())
            cv2.imwrite(f'record/record_{timestamp}.png', mat)
            log.info(mat.shape)
        sleep(1)
        