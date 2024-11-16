import cv2
import numpy as np
import time
from typing import Tuple, Optional
from common.ocr import RelatetiveBoxPosition

def find_image(template: np.ndarray, 
               frame: np.ndarray,
               threshold: float = 0.8,
               timeout: int = 30,
               check_interval: float = 0.5) -> Optional[Tuple[int, int]]:
    """
    在游戏画面中查找指定图像
    
    Args:
        template: 要查找的模板图片(numpy数组)
        frame: 要搜索的图片帧(numpy数组)
        threshold: 匹配阈值，越高要求越严格
        timeout: 最大等待时间(秒)
        check_interval: 检查间隔时间(秒)
    
    Returns:
        成功则返回匹配位置的坐标元组(x, y)，失败返回None
    """
    if template is None:
        raise ValueError("模板图片不能为空")
    
    template_height, template_width = template.shape[:2]
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if frame is None:
            continue
            
        result = cv2.matchTemplate(frame, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= threshold:
            x = max_loc[0] + template_width // 2
            y = max_loc[1] + template_height // 2
            end_time = time.time()
            print(f"查找耗时: {end_time - start_time:.3f}秒")
            return (x, y)
            
        time.sleep(check_interval)
    
    end_time = time.time()
    print(f"查找超时，总耗时: {end_time - start_time:.3f}秒")
    return None

# 读取图片并进行测试
hero_template = cv2.imread("D:/VSCodeProjects/tft-helper/src/test/is_look_unit.bmp")
frame_template = cv2.imread("D:/VSCodeProjects/tft-helper/src/test/frame.png")
position = RelatetiveBoxPosition(0.925, 0.683, 0.954, 0.711)
croped_frame = position.get_cropped_frame(frame_template)
if hero_template is None or frame_template is None:
    raise ValueError("英雄.bmp或frame.png图片读取失败")


# 查找图片
hero_result = find_image(
    template=hero_template,
    frame=croped_frame,
    threshold=0.8,
    timeout=30,
    check_interval=0.5
)

if hero_result:
    x, y = hero_result
    print(f"找到英雄图片，位置: ({x}, {y})")
else:
    print("未找到英雄图片")