import time
from pathlib import Path
from datetime import datetime
APP_NAME = '云顶之弈助手'
APP_VERSION = '1.0.0'
LOL_PROCESS_NAME = 'League of Legends (TM) Client'
# 是否开启DEBUG
# DEBUG模式会在屏幕显示OCR结果
DEBUG_MODE = True

# 是否开启回放
REPLAY_MODE = True
REPLAY_BASE_TIME = '2024-12-22 22-31-21'
# 回放时间偏移量 单位秒
REPALY_BASE_TIME_OFFSET = 280
# 启动时间
APP_START_TIME = time.time()
APP_START_DATE = datetime.fromtimestamp(APP_START_TIME)

# 是否保存游戏过程中截图
ENABLE_SAVE_SCREENSHOT = True
# 截图存储路径
SCREENSHOT_BASE_DIR = Path('screenshot') / APP_START_DATE.strftime('%Y-%m-%d %H-%M-%S')
if ENABLE_SAVE_SCREENSHOT and not REPLAY_MODE:
    # 初始化截图存储文件夹
    SCREENSHOT_BASE_DIR.mkdir(parents=True, exist_ok=True)
