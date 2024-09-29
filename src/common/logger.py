from loguru import logger
from common.signal import signal_bus
import sys

def setup_logger():
    logger.remove()
    def log_handler(message):
        # 解析消息 获取到日志级别
        level = message.split(" | ", 2)[1].strip()
        signal_bus.log.emit(level, message.strip())
    # 输出到控制台
    logger.add(sys.stdout)
    logger.add(log_handler)
    return logger

log = setup_logger()