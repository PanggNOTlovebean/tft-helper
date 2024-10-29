import time
from pathlib import Path
from datetime import datetime
APP_NAME = '云顶之弈助手'
APP_VERSION = '1.0.0'
LOL_PROCESS_NAME = 'League of Legends (TM) Client'
DEBUG_MODE = False
REPLAY_MODE = False
REPLAY_BASE_TIME = '2024-09-28 23-43-21'
# 启动时间
APP_START_TIME = time.time()
APP_START_DATE = datetime.fromtimestamp(APP_START_TIME)
# 是否保存游戏过程中截图
ENABLE_SAVE_SCREENSHOT = True
# 截图存储路径
SCREENSHOT_BASE_DIR = Path('screenshot') / APP_START_DATE.strftime('%Y-%m-%d %H-%M-%S')
if ENABLE_SAVE_SCREENSHOT:
    # 初始化截图存储文件夹
    SCREENSHOT_BASE_DIR.mkdir(parents=True, exist_ok=True)
