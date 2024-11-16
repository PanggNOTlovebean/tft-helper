from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QPoint, QRect, QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QFont, QImage
import time
from dataclasses import dataclass
from typing import Any, Optional
from dataclasses import dataclass, field
import numpy as np
import cv2
import sys
from common.meta_class import SingletonMeta
from common.ocr import RelatetiveBoxPosition, RelativePosition
from PySide6.QtGui import QTextDocument

@dataclass
class DrawItem:
    """绘制项基类"""
    duration: Optional[float] = None  # 持续时间（秒），None表示永久
    create_time: float = field(default_factory=time.time)  # 创建时间
    @property
    def is_expired(self) -> bool:
        """判断是否已过期"""
        if self.duration is None:
            return False
        return time.time() - self.create_time > self.duration

@dataclass
class BoxTextItem(DrawItem):
    """矩形框和文字"""
    position: RelatetiveBoxPosition = field(default_factory=RelatetiveBoxPosition)
    text: str = field(default="")
    color: QColor = field(default_factory=lambda: QColor(255, 0, 0))

@dataclass
class ImageItem(DrawItem):
    """图片项"""
    x: int = field(default=0)
    y: int = field(default=0)
    image: Any = field(default=None)  # numpy.ndarray, QImage, or str
    scale: float = field(default=1.0)
    _qimage: Optional[QImage] = None
    
    def __post_init__(self):
        # 转换图片格式
        if isinstance(self.image, np.ndarray):
            if len(self.image.shape) == 3 and self.image.shape[2] == 3:
                self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            height, width = self.image.shape[:2]
            bytes_per_line = 3 * width
            self._qimage = QImage(self.image.data, width, height, 
                                bytes_per_line, QImage.Format_RGB888)
        elif isinstance(self.image, QImage):
            self._qimage = self.image
        elif isinstance(self.image, str):
            self._qimage = QImage(self.image)
        else:
            raise ValueError("Unsupported image type")

@dataclass
class HtmlItem(DrawItem):
    """HTML渲染项"""
    position: RelativePosition = field(default_factory=RelativePosition)  # 替换x,y为RelativePosition
    html: str = field(default="")
    width: Optional[int] = field(default=None)
    background_color: Optional[QColor] = field(default=None)
    _document: Optional['QTextDocument'] = None

    def __post_init__(self):
        self._document = QTextDocument()
        self._document.setDefaultFont(QFont("Arial", 10))
        if self.width:
            self._document.setTextWidth(self.width)
        self._document.setHtml(self.html)

class OverlayWindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        screen = QApplication.primaryScreen().availableGeometry()
        self.setGeometry(screen)
        
        # 使用坐标作为key
        self.box_items : dict[RelatetiveBoxPosition, BoxTextItem] = {}  # key: (x1,y1,x2,y2), value: BoxTextItem
        self.image_items = {} # key: (x,y), value: ImageItem
        self.html_items = {}  # key: RelativePosition, value: HtmlItem
        
        self.font = QFont()
        self.font.setPointSize(10)
        
        # 创建定时器用于清理过期项
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self.cleanup_expired_items)
        self.cleanup_timer.start(100)  # 每100ms检查一次
    
    def cleanup_expired_items(self):
        """清理所有过期的绘制项"""
        need_update = False
        
        # 清理box_items
        for pos in list(self.box_items.keys()):
            if self.box_items[pos].is_expired:
                del self.box_items[pos]
                need_update = True
        
        # 清理image_items
        for pos in list(self.image_items.keys()):
            if self.image_items[pos].is_expired:
                del self.image_items[pos]
                need_update = True
        
        if need_update:
            self.update()
    
    def add_box_item(self, item: BoxTextItem):
        """添加单个绘制项"""
        self.box_items[item.position] = item
        self.update()
    def remove_box_item(self, position: RelatetiveBoxPosition):
        """移除指定绘制项"""
        if position in self.box_items:
            del self.box_items[position]
            self.update()

    def add_image_item(self, item: ImageItem):
        """添加图片项"""
        self.image_items[item.position] = item
        self.update()

    def add_html_item(self, item: HtmlItem):
        """添加HTML渲染项"""
        self.html_items[item.position] = item
        self.update()

    def clear_html_items(self):
        """清空所有HTML渲染项"""
        self.html_items.clear()
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(self.font)
        
        # 绘制所有box_items
        for pos, item in self.box_items.items():
            pen = QPen(item.color)
            pen.setWidth(3)
            painter.setPen(pen)
            x1, y1, x2, y2 = item.position.get_screen_position()
            painter.drawRect(x1, y1, x2-x1, y2-y1)
            
            text_rect = painter.fontMetrics().boundingRect(item.text)
            text_rect.moveTopLeft(QPoint(x2, y2+20))
            text_rect.adjust(-10, -5, 10, 5)
            
            painter.fillRect(text_rect, QColor(0, 0, 0, 180))
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, item.text)
        
        # 绘制所有image_items
        for pos, item in self.image_items.items():
            if item.scale != 1.0:
                scaled_width = int(item._qimage.width() * item.scale)
                scaled_height = int(item._qimage.height() * item.scale)
                scaled_image = item._qimage.scaled(
                    scaled_width, scaled_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            else:
                scaled_image = item._qimage
            
            painter.drawImage(QPoint(item.x, item.y), scaled_image)
        
        # 绘制所有html_items
        for pos, item in self.html_items.items():
            painter.save()
            
            # 使用RelativePosition获取实际屏幕坐标
            x, y = item.position.get_screen_position()
            painter.translate(x, y)
            
            if item.background_color:
                rect = QRect(0, 0, 
                            item._document.size().width(), 
                            item._document.size().height())
                painter.fillRect(rect, item.background_color)
            
            item._document.drawContents(painter)
            
            painter.restore()