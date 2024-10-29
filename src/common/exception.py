class NoFrameException(Exception):  # 定义 NoFrameException
    def __init__(self, message="未获取到帧数据"):
        super().__init__(message)  # 调用父类构造函数