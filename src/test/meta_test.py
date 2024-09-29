'''
元类测试
'''

from ..capture.hwnd_window import HwndWindow

hwnd_window1 = HwndWindow('League of Legends (TM) Client')
hwnd_window2 = HwndWindow('League of Legends (TM) Client')

print(hwnd_window1 is hwnd_window2)