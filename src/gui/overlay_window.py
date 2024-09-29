import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))
sys.path.append(str(Path(__file__).parent.parent))
print(str(Path(__file__)))
print(str(Path(__file__).parent))

from loguru import logger as log
import win32api
from PySide6.QtCore import Qt, QPoint, QTimer, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont, QGuiApplication, QPixmap
from PySide6.QtWidgets import QWidget
from capture.HwndWindow import HwndWindow
from PySide6.QtWidgets import QApplication



class FrameWidget(QWidget):
    def __init__(self):
        super(FrameWidget, self).__init__()
        self._mouse_position = QPoint(0, 0)
        self.setMouseTracking(True)
        # Start a timer to update mouse position using Windows API
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_mouse_position)
        self.timer.start(1000)  # Update every 50 milliseconds
        self.mouse_font = QFont()
        self.mouse_font.setPointSize(10)  # Adjust the size as needed
        screen = QGuiApplication.primaryScreen()
        self.scaling = screen.devicePixelRatio()

        self.images = [
            QPixmap("data/item/TFT_Item_Bloodthirster.jpg"),
            QPixmap("data/item/TFT_Item_GargoyleStoneplate.jpg"),
            QPixmap("data/item/TFT_Item_GuinsoosRageblade.jpg"),
        ]

    def update_mouse_position(self):
        try:
            if not self.isVisible():
                return
            x, y = win32api.GetCursorPos()
            relative = self.mapFromGlobal(QPoint(x / self.scaling, y / self.scaling))
            if self._mouse_position != relative and relative.x() > 0 and relative.y() > 0:
                self._mouse_position = relative
            self.update()
        except Exception as e:
            log.warning(f'GetCursorPos exception {e}')

    def frame_ratio(self):
        # if ok.gui.device_manager.width == 0:
        #     return 1
        # return self.width() / ok.gui.device_manager.width
        return 1

    def paintEvent(self, event):
        if not self.isVisible():
            return
        painter = QPainter(self)
        self.paint_border(painter)
        self.paint_boxes(painter)
        self.paint_mouse_position(painter)
        self.paint_images(painter)

    def paint_boxes(self, painter):
        pen = QPen()  # Set the brush to red color
        pen.setWidth(2)  # Set the width of the pen (border thickness)
        painter.setPen(pen)  # Apply the pen to the painter
        painter.setBrush(Qt.NoBrush)  # Ensure no fill

        frame_ratio = self.frame_ratio()
        # for key, value in ok.gui.ok.screenshot.ui_dict.items():
        #     boxes = value[0]
        #     pen.setColor(value[2])
        #     painter.setPen(pen)
        #     for box in boxes:
        #         width = box.width * frame_ratio
        #         height = box.height * frame_ratio
        #         x = box.x * frame_ratio
        #         y = box.y * frame_ratio
        #         painter.drawRect(x, y, width, height)
        #         painter.drawText(x, y + height + 12, f"{box.name or key}_{round(box.confidence * 100)}")

    def paint_border(self, painter):
        pen = QPen(QColor(255, 0, 0, 255))  # Solid red color for the border
        pen.setWidth(1)  # Set the border width
        painter.setPen(pen)
        # Draw the border around the widget
        painter.drawRect(0, 0, self.width() - 1, self.height() - 1)

    def paint_mouse_position(self, painter):
        x_percent = self._mouse_position.x() / self.width()
        y_percent = self._mouse_position.y() / self.height()
        x, y = self._mouse_position.x() * 2, self._mouse_position.y() * 2
        text = f"({x}, {y}, {x_percent:.2f}, {y_percent:.2f})"
        painter.setFont(self.mouse_font)

        painter.setPen(QPen(QColor(255, 0, 0, 255), 1))
        painter.drawText(20, 20, text)
        #
        # # Draw the black text
        # painter.setPen(QPen(QColor(0, 0, 0), 2))
        # painter.drawText(10, 10, text)
    
    def paint_images(self, painter):
        width = self.width() // 3  # 将宽度平均分成三份
        height = self.height() // 2  # 高度设为窗口高度的一半

        for i, image in enumerate(self.images):
            x = i * width
            y = self.height() // 4  # 将图片垂直居中

            # 缩放图片以适应分配的空间
            scaled_image = image.scaled(width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # 计算图片在分配空间内的居中位置
            image_rect = scaled_image.rect()
            target_rect = QRect(x + (width - image_rect.width()) // 2,
                                y + (height - image_rect.height()) // 2,
                                image_rect.width(),
                                image_rect.height())

            painter.drawPixmap(target_rect, scaled_image)

class OverlayWindow(FrameWidget):
    def __init__(self):
        super().__init__()
        # 设置透明背景，使得窗口的背景不会被绘制，从而可以显示下面的内容或窗口
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 确保窗口能够正确接收鼠标事件，因为透明窗口可能会导致鼠标事件无法被正确处理
        self.setAttribute(Qt.WA_OpaquePaintEvent)

        # 设置窗口：
        # Qt.FramelessWindowHint：去掉窗口的边框和标题栏，使其看起来更像一个浮动的工具窗口
        # Qt.WindowStaysOnTopHint：使窗口始终保持在其他窗口之上
        # Qt.Tool：将窗口标记为工具窗口，通常用于辅助工具
        # Qt.WindowTransparentForInput：使窗口对输入事件透明，允许鼠标事件穿透窗口，直接传递给下面的窗口
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)

    def update_overlay(self, visible, x, y, window_width, window_height, width, height, scaling):
        if visible:
            self.setGeometry(x / scaling, y / scaling, width / scaling, height / scaling)
        if visible and not self.isVisible():
            self.show()
            return
        if not visible and self.isVisible():
            self.hide()

if __name__ == '__main__':
    # 测试
    app = QApplication(sys.argv)
    window = OverlayWindow()
    window.show()
    sys.exit(app.exec())