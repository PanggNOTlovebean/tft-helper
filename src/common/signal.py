from PySide6.QtCore import Signal, QObject

class SignalBus(QObject):
    # 预定义的信号
    log = Signal(str, str)
    game_task_signal = Signal(str)

signal_bus = SignalBus()