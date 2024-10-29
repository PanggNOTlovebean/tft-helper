from dataclasses import dataclass
import sys

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListView,
    QComboBox,
    QLineEdit,
    QPushButton,
    QLabel,
    QAbstractItemView,
    QApplication,
    QStyledItemDelegate,
)
from PySide6.QtCore import Qt, QAbstractListModel, QModelIndex
from PySide6.QtGui import QMouseEvent, QColor
from common.signal import signal_bus
from common.logger import log

level_severity = {
    "DEBUG": 10,
    "INFO": 20,
    "WARNING": 30,
    "ERROR": 40,
    "CRITICAL": 50,
    "ALL": 100,
}

color_codes = {
    "INFO": QColor(0, 0, 255),  # 蓝色
    "DEBUG": QColor(0, 128, 0),  # 绿色
    "WARNING": QColor(255, 165, 0),  # 橙色
    "ERROR": QColor(255, 0, 0),  # 红色
    "CRITICAL": QColor(128, 0, 128),  # 紫色
    "ALL": QColor(
        0,
        0,
        0,
    ),  # 黑色
}

@dataclass
class ColoredText:
    text: str
    format: QColor
    level: str

# 渲染
class ColorDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(ColorDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        # 获取文本颜色
        text_color = index.data(Qt.ForegroundRole)
        if text_color:
            painter.setPen(text_color)

        # 绘制文本
        text = index.data(Qt.DisplayRole)
        painter.drawText(option.rect, Qt.AlignVCenter | Qt.AlignLeft, text)


# 日志数据模型
class LogModel(QAbstractListModel):
    def __init__(self):
        super(LogModel, self).__init__()
        self.logs = []
        self.filtered_logs = []
        self.current_level = "ALL"
        self.current_keyword = ""

    def data(self, index, role):
        if 0 <= index.row() < len(self.filtered_logs):
            if role == Qt.DisplayRole:
                return self.filtered_logs[index.row()].text
            elif role == Qt.ForegroundRole:
                return self.filtered_logs[index.row()].format
            # elif role == Qt.BackgroundRole:
            # return self.filtered_logs[index.row()].format

    def rowCount(self, index=None):
        return len(self.filtered_logs)

    def add_log(self, level, message):
        # 创建基于级别的彩色文本
        color_format = self.get_color_format(level)
        colored_text = ColoredText(message, color_format, level)

        # 在列表开头添加新日志
        self.logs.append(colored_text)

        # 如果日志数量超过500，删除最旧的日志
        if len(self.logs) > 500:
            self.logs.pop()

        # 更新模型
        self.beginResetModel()
        self.filter_logs()
        self.endResetModel()

    def filter_logs(self):
        keyword = self.current_keyword.lower()

        # 获取当前日志级别
        current_level_severity = level_severity.get(self.current_level, 0)

        # 根据日志级别和关键词过滤日志
        if self.current_level == "ALL":
            self.filtered_logs = [
                log for log in self.logs if keyword in log.text.lower()
            ]
        else:
            self.filtered_logs = [
                log
                for log in self.logs
                if level_severity.get(log.level, 0) >= current_level_severity
                and keyword in log.text.lower()
            ]

    def update_log_filter_setting(self, level, keyword):
        # 更新当前的日志级别和关键词
        self.current_level = level
        self.current_keyword = keyword
        # 开始移除行，清除所有已过滤的日志
        self.beginRemoveRows(QModelIndex(), 0, self.rowCount() - 1)
        self.filtered_logs.clear()
        # 结束移除行
        self.endRemoveRows()
        # 根据新的日志级别和关键词重新过滤日志
        self.filter_logs()

    def get_color_format(self, level):
        return color_codes.get(level, QColor())


# 日志窗口
class LogWindow(QWidget):
    def __init__(
        self,
        x: int = 0,
        y: int = 0,
        width: int = 1000,
        height: int = 300,
        level: str = "ALL",
        keyword: str = "",
    ):
        super().__init__()
        self.setWindowTitle("日志查看器")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setGeometry(x, y, width, height)

        self.old_pos = None

        # Layouts
        self.layout = QVBoxLayout()
        self.filter_layout = QHBoxLayout()

        # Widgets
        self.log_list = QListView()
        self.log_list.setStyleSheet(
            """
            background-color: rgba(255, 255, 255, 1);
            color: white;
            font-size: 14px;
            border: 1px solid #444;
            border-radius: 5px;
        """
        )
        self.log_list.setSelectionMode(QAbstractItemView.NoSelection)
        self.log_list.setItemDelegate(ColorDelegate())

        self.level_filter = QComboBox()
        self.level_filter.addItems(
            ["ALL", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )
        self.level_filter.setCurrentText(level)
        self.level_filter.currentIndexChanged.connect(self.filter_logs)

        self.keyword_filter = QLineEdit()
        self.keyword_filter.setPlaceholderText("按关键词过滤")
        self.keyword_filter.setText(keyword)
        self.keyword_filter.textChanged.connect(self.filter_logs)

        self.drag_button = QLabel(self.tr("拖动"))
        self.drag_button.setStyleSheet("background:rgba(0,0,0,255)")

        self.close_button = QPushButton(self.tr("关闭"))
        self.close_button.clicked.connect(self.close)

        # Adding widgets to layouts
        self.filter_layout.addWidget(self.level_filter)
        self.filter_layout.addWidget(self.keyword_filter, stretch=1)
        self.filter_layout.addWidget(self.drag_button)
        self.filter_layout.addWidget(self.close_button)

        self.layout.addLayout(self.filter_layout)
        self.layout.addWidget(self.log_list)

        self.setLayout(self.layout)

        self.log_model = LogModel()
        self.log_list.setModel(self.log_model)

        signal_bus.log.connect(self.add_log)
        self.filter_logs()

    def close(self):
        super().close()

    def add_log(self, level: str, message: str):
        self.log_model.add_log(level, message)
        self.log_list.scrollToBottom()

    def filter_logs(self):
        level = self.level_filter.currentText()
        keyword = self.keyword_filter.text()
        self.log_model.update_log_filter_setting(level, keyword)

    # 实现窗口可拖拽
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            # self.config["x"] = self.x()
            # self.config["y"] = self.y()
            self.old_pos = None


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建日志窗口
    log_window = LogWindow()
    log_window.show()
    from PySide6.QtCore import QTimer
    import random

    # 创建一个定时器来模拟日志输入
    timer = QTimer()

    def add_random_log():
        levels = ["DEBUG", "INFO", "WARNING", "ERROR"]  # DEBUG, INFO, WARNING, ERROR
        messages = [
            "2024-09-22 20:14:13.790 | INFO     | __main__:add_random_log:254 - 内存使用率超过90%",
            "内存使用率超过90%",
        ]
        level = random.choice(levels)
        message = random.choice(messages)
        # signal_bus.log.emit(level, message)
        log.info(message)

    # 每500毫秒添加一条随机日志
    timer.timeout.connect(add_random_log)
    timer.start(500)

    sys.exit(app.exec())
