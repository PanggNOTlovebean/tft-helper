import win32api
import win32con
# 屏幕宽度
MONITOR_W: int = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
# 屏幕高度
MONITOR_H: int = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)