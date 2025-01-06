import sys
from PySide6.QtWidgets import QApplication
from task.game_stage_task import GameStageTask
from task.augument_task import AugumentTask
from task.item_task import ItemTask

if __name__ == '__main__':
    # 调试时启动pyside application
    app = QApplication(sys.argv)
    game_stage_task = GameStageTask()
    augument_task = AugumentTask()   
    item_task = ItemTask()
    # 等待主动结束
    sys.exit(app.exec())