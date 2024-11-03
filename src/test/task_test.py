import sys
from PySide6.QtWidgets import QApplication
from task.game_stage_task import GameStageTask
from task.hex_task import HexTask

if __name__ == '__main__':
    # 调试时启动pyside application
    app = QApplication(sys.argv)
    game_stage_task = GameStageTask()
    hex_task = HexTask()   
    # 等待主动结束
    sys.exit(app.exec())