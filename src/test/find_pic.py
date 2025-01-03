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
# hero_template = cv2.imread("D:/VSCodeProjects/tft-helper/src/test/is_look_unit.bmp")
# frame_template = cv2.imread("D:/VSCodeProjects/tft-helper/src/test/frame.png")

aug_template = cv2.imread("D:/VSCodeProjects/tft-helper/src/test/pandora3.png")
frame = cv2.imread("D:/VSCodeProjects/tft-helper/src/test/img.png")
if aug_template is not None and aug_template.shape[2] == 4:
    aug_template = cv2.cvtColor(aug_template, cv2.COLOR_BGRA2BGR)

# position = RelatetiveBoxPosition(0.2016, 0.2590, 0.3887, 0.4972)
position = RelatetiveBoxPosition(0.4129, 0.2507, 0.6023, 0.5000)
# position = RelatetiveBoxPosition(0.6242, 0.2590, 0.8090, 0.4896)
frame = position.get_cropped_frame(frame)

if aug_template is not None:
    cv2.imshow("Aug Template", aug_template)
else:
    print("无法加载 aug_template")

if frame is not None:
    cv2.imshow("Frame Template", frame)
else:
    print("无法加载 frame_template")
# 等待用户按键关闭窗口
cv2.waitKey(0)
cv2.destroyAllWindows()
if aug_template is None or frame is None:
    raise ValueError("图片读取失败")


# 查找图片
hero_result = find_image(
    template=aug_template,
    frame=frame,
    threshold=0.8,
    timeout=30,
    check_interval=0.5
)

if hero_result:
    x, y = hero_result
    print(f"找到英雄图片，位置: ({x}, {y})")
else:
    print("未找到英雄图片")