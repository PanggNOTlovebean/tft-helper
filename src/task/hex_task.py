from PySide6.QtCore import QTimer

from task.base_task import BaseTask
from common.ocr import ocr
from common.logger import log
from common.game_info import game_stage
from common.signal import signal_bus
import time
import pythoncom
from common.ocr import RelatetiveBoxPosition, RelativePosition
from gui.overlay_window import HtmlItem


# 识别海克斯
class HexTask(BaseTask):
    name = "海克斯任务"
    description = "识别海克斯"

    def __init__(self):
        super().__init__()
        self.timer = QTimer()
        self.timer.timeout.connect(self.run)
        signal_bus.game_task_signal.connect(self.on_game_stage_change)
        
    def on_game_stage_change(self):
        if game_stage in ("2-1", "3-2", "4-2"):
            if not self.timer.isActive():
                self.timer.start(1000)  # 每秒检查一次
        else:
            self.timer.stop()

    def run(self):
        try:
            # 检查海克斯是否存在 游戏上方出现 选择一件 标识
            CHECK_HEX_POSITION = RelatetiveBoxPosition(0.454, 0.183, 0.547, 0.231)
            ocr_result = self.ocr(CHECK_HEX_POSITION)
            
            if "择" not in ocr_result:
                self.timer.stop()
                self.clear_html_items()
                log.info('海克斯选择结束')
                return

            log.info("选择海克斯")
            HEX_NAME_POSITION_TUPLE = (
                (0.213, 0.494, 0.368, 0.536),
                (0.440, 0.492, 0.581, 0.540),
                (0.647, 0.492, 0.790, 0.539),
            )
            
            HEX_TIER_POSITION_TUPLE = (
                (0.213, 0.494),
                (0.440, 0.492),
                (0.647, 0.492),
            )
            for ocr_position, tier_position in zip(HEX_NAME_POSITION_TUPLE, HEX_TIER_POSITION_TUPLE):
                ocr_result = self.ocr(RelatetiveBoxPosition(*ocr_position))
                log.info(f"海克斯天赋: {ocr_result}")
                html_tag = create_html_tag(("强度", "T1"), ("平均排名", "4.23"), ("2-1平均排名", "3.23"))
                self.add_html_item(HtmlItem(position=RelativePosition(*tier_position), html=html_tag, duration=3))

        except Exception as e:
            log.exception(e)



def create_html_tag(*pairs):
    """
    创建包含多个键值对的HTML标签
    pairs: 元组列表，每个元组包含(key, value)
    """
    spans = ''
    for key, value in pairs:
        spans += f'''
        <span style="background: #555; color: white; padding: 3px 6px; border-radius: 3px 0 0 3px;">
            {key}
        </span>
        <span style="background: #44cc11; color: white; padding: 3px 6px; border-radius: 0 3px 3px 0;">
            {value}
        </span>
        '''
    
    html = f'''
    <div style="display: inline-block; font-family: Verdana, Geneva, DejaVu Sans, sans-serif; 
                background: #555; border-radius: 3px; padding: 2px 0;">
        {spans}
    </div>
    '''
    return html


if __name__ == "__main__":
    task = HexTask()
