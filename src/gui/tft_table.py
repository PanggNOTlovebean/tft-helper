from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QApplication,
                             QWidget, QHBoxLayout, QLabel, QPushButton)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from qfluentwidgets import TableWidget
import os

class TFTTable(TableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置窗口标志，使其无边框、保持在最顶层，并且透明于输入事件
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowTransparentForInput
        )


        # 设置表格的行数和列数（扩充到8列）
        self.setRowCount(5)
        self.setColumnCount(8)

        # 设置列标题
        headers = ["装备组合", "平均名次", "名次变化", "使用率",
                   "单件装备", "平均名次", "名次变化", "使用率"]
        self.setHorizontalHeaderLabels(headers)
        
        # 设置表头和行号的字体颜色为白色
        header_style = "QHeaderView::section { color: white; }"
        self.horizontalHeader().setStyleSheet(header_style)
        self.verticalHeader().setStyleSheet(header_style)

        # 设置列宽
        self.setColumnWidth(0, 120)  # 第一列宽一些，用于显示多个图标
        self.setColumnWidth(4, 60)  # 第五列窄一些，只显示单个图标
        for i in range(1, 4):
            self.setColumnWidth(i, 80)
        for i in range(5, 8):
            self.setColumnWidth(i, 80)

        # 设置行高
        for i in range(5):
            self.setRowHeight(i, 40)
            
        # 调整窗口大小以适应内容
        self.adjustSize()
        total_width = sum(self.columnWidth(i) for i in range(self.columnCount())) + 50
        total_height = sum(self.rowHeight(i) for i in range(self.rowCount())) + self.horizontalHeader().height()
        
        # 为边框和滚动条预留一些额外空间
        self.setFixedSize(total_width + 2, total_height + 2)

        # 移动窗口到英雄详情附近
        screen = QApplication.primaryScreen().geometry()
        # 确保窗口完全在屏幕内，通过减去窗口宽度和高度来调整
        x = int(screen.width() * 0.883) - self.width()
        y = int(screen.height() * 0.33) 
        self.move(x, y)

        # 初始时隐藏表格
        self.hide()
        
        # 创建显示/隐藏按钮
        self.toggle_button = QPushButton("装\n备\n推\n荐", parent)
        self.toggle_button.setFixedSize(32, 120)  # 调整按钮大小为竖向
        self.toggle_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(30, 30, 30, 200);
                border: 1px solid #666;
                color: white;
                font-size: 12px;
                padding: 8px 0;
            }
            QPushButton:hover {
                background-color: rgba(40, 40, 40, 200);
            }
        """)
        
        # 设置按钮窗口属性
        self.toggle_button.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 设置按钮位置（在表格右侧）
        button_x = int(screen.width() * 0.883) - self.toggle_button.width()
        button_y = int(screen.height() * 0.33) - self.toggle_button.height()
        self.toggle_button.move(button_x, button_y)
        
        # 连接按钮点击事件
        self.toggle_button.clicked.connect(self.toggle_visibility)
        self.toggle_button.hide()

    def show_toggle_button(self):
        self.toggle_button.setText("装\n备\n推\n荐")
        self.toggle_button.show()
        
    def hide_toggle_button(self):
        self.toggle_button.hide()
        self.hide()

    def set_combined_items_data(self, row, icons, avg_place, place_change, play_rate):
        """
        设置装备组合
        :param row: 行号
        :param icons: 图标路径列表 (最多3个)
        :param avg_place: 平均名次
        :param place_change: 名次变化
        :param play_rate: 使用率
        """
        # 创建水平布局容器
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)  # 设置边距
        layout.setSpacing(4)  # 设置图标间距
        
        # 添加多个图标
        for icon_path in icons:
            if os.path.exists(icon_path):
                label = QLabel()
                pixmap = QPixmap(icon_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    label.setPixmap(scaled_pixmap)
                layout.addWidget(label)
        
        # 将容器设置到表格单元格
        self.setCellWidget(row, 0, container)
        
        # 设置数字数据 - 平均名次
        avg_place_item = QTableWidgetItem()
        avg_place_item.setText(avg_place)
        avg_place_item.setTextAlignment(Qt.AlignCenter)  # 居中对齐
        avg_place_item.setForeground(Qt.white)  # 设置白色字体
        self.setItem(row, 1, avg_place_item)
        
        # 名次变化（带颜色）
        change_item = QTableWidgetItem()
        change_item.setText(place_change)
        change_item.setTextAlignment(Qt.AlignCenter)  # 居中对齐
        if float(place_change) < 0:
            change_item.setForeground(Qt.green)
        else:
            change_item.setForeground(Qt.red)
        self.setItem(row, 2, change_item)
        
        # 使用率
        play_rate_item = QTableWidgetItem()
        play_rate_item.setText(play_rate)
        play_rate_item.setTextAlignment(Qt.AlignCenter)  # 居中对齐
        play_rate_item.setForeground(Qt.white)  # 设置白色字体
        self.setItem(row, 3, play_rate_item)

    def set_single_item_data(self, row, icon, avg_place, place_change, play_rate):
        """
        设置单个装备的数据（后四列）
        """
        # 创建单个图标的容器
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        
        # 添加单个图标
        if os.path.exists(icon):
            label = QLabel()
            pixmap = QPixmap(icon)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(scaled_pixmap)
            layout.addWidget(label)
        
        # 将容器设置到表格单元格
        self.setCellWidget(row, 4, container)
        
        # 设置数字数据 - 平均名次
        avg_place_item = QTableWidgetItem()
        avg_place_item.setText(avg_place)
        avg_place_item.setTextAlignment(Qt.AlignCenter)
        avg_place_item.setForeground(Qt.white)
        self.setItem(row, 5, avg_place_item)
        
        # 名次变化（带颜色）
        change_item = QTableWidgetItem()
        change_item.setText(place_change)
        change_item.setTextAlignment(Qt.AlignCenter)
        if float(place_change) < 0:
            change_item.setForeground(Qt.green)
        else:
            change_item.setForeground(Qt.red)
        self.setItem(row, 6, change_item)
        
        # 使用率
        play_rate_item = QTableWidgetItem()
        play_rate_item.setText(play_rate)
        play_rate_item.setTextAlignment(Qt.AlignCenter)
        play_rate_item.setForeground(Qt.white)
        self.setItem(row, 7, play_rate_item)

    def toggle_visibility(self):
        """
        切换表格的显示/隐藏状态
        """
        if self.isVisible():
            self.hide()
            self.toggle_button.setText("装\n备\n推\n荐")
        else:
            self.show()
            self.toggle_button.setText("隐\n藏")

def test_tft_table():
    from PySide6.QtWidgets import QApplication
    import sys
    import os

    # 创建QApplication实例
    app = QApplication(sys.argv)
    
    # 创建TFTTable实例
    table = TFTTable()
    
    # 测试数据
    # 装备图标路径示例（请替换为实际的图标路径）
    item_icons = [
        "path/to/item1.png",
        "path/to/item2.png",
        "path/to/item3.png"
    ]
    
    # 测试组合装备数据
    table.set_combined_items_data(
        row=0,
        icons=item_icons[:3],
        avg_place="4.2",
        place_change="-0.5",
        play_rate="15.2%"
    )
    
    # 测试单件装备数据
    table.set_single_item_data(
        row=0,
        icon=item_icons[0],
        avg_place="4.5",
        place_change="+0.3",
        play_rate="12.8%"
    )
    
    # 显示按钮（表格初始隐藏）
    table.toggle_button.show()
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    test_tft_table()