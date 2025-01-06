from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem, QApplication,
                             QWidget, QHBoxLayout, QLabel)
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtCore import Qt
from qfluentwidgets import TableWidget
import os

class TFTTable(TableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # 设置窗口标志，使其无边框并始终保持在最顶层
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        
        # 移除透明背景设置
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # 设置表格的行数和列数（扩充到8列）
        self.setRowCount(5)
        self.setColumnCount(8)

        # 设置列标题
        headers = ["装备组合", "平均名次", "名次变化", "使用率",
                   "单件装备", "平均名次", "名次变化", "使用率"]
        self.setHorizontalHeaderLabels(headers)

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

    def set_item_data(self, row, icons, avg_place, place_change, play_rate):
        """
        设置每一行的数据
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
        avg_place_item.setText(f"{avg_place:.2f}")
        avg_place_item.setTextAlignment(Qt.AlignCenter)  # 居中对齐
        avg_place_item.setForeground(Qt.white)  # 设置白色字体
        self.setItem(row, 1, avg_place_item)
        
        # 名次变化（带颜色）
        change_item = QTableWidgetItem()
        change_item.setText(f"{place_change:.2f}")
        change_item.setTextAlignment(Qt.AlignCenter)  # 居中对齐
        if place_change < 0:
            change_item.setForeground(Qt.green)
        else:
            change_item.setForeground(Qt.red)
        self.setItem(row, 2, change_item)
        
        # 使用率
        play_rate_item = QTableWidgetItem()
        play_rate_item.setText(f"{play_rate:.1f}%")
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
        avg_place_item.setText(f"{avg_place:.2f}")
        avg_place_item.setTextAlignment(Qt.AlignCenter)
        avg_place_item.setForeground(Qt.white)
        self.setItem(row, 5, avg_place_item)
        
        # 名次变化（带颜色）
        change_item = QTableWidgetItem()
        change_item.setText(f"{place_change:.2f}")
        change_item.setTextAlignment(Qt.AlignCenter)
        if place_change < 0:
            change_item.setForeground(Qt.green)
        else:
            change_item.setForeground(Qt.red)
        self.setItem(row, 6, change_item)
        
        # 使用率
        play_rate_item = QTableWidgetItem()
        play_rate_item.setText(f"{play_rate:.1f}%")
        play_rate_item.setTextAlignment(Qt.AlignCenter)
        play_rate_item.setForeground(Qt.white)
        self.setItem(row, 7, play_rate_item)

if __name__ == "__main__":
    import sys
    import os
    
    app = QApplication(sys.argv)
    
    # 获取当前文件所在目录
    # current_dir = os.path.dirname(os.path.abspath(__file__))
    # print(f"当前目录: {current_dir}")  # 调试信息
    
    # 创建主窗口
    table = TFTTable()
    # table.resize(400, 300)
    table.setWindowTitle('TFT装备数据')
    
    # 使用绝对路径构建测试数据
    test_data = [
        (["data/item/TFT_Item_Bloodthirster.jpg","data/item/TFT_Item_Bloodthirster.jpg","data/item/TFT_Item_Bloodthirster.jpg"], 2.34, -1.92, 0.5),
        (["data/item/TFT_Item_Bloodthirster.jpg","data/item/TFT_Item_Bloodthirster.jpg","data/item/TFT_Item_Bloodthirster.jpg"], 2.34, -1.92, 0.5),
        (["data/item/TFT_Item_Bloodthirster.jpg","data/item/TFT_Item_Bloodthirster.jpg","data/item/TFT_Item_Bloodthirster.jpg"], 2.34, -1.92, 0.5),
        (["data/item/TFT_Item_Bloodthirster.jpg", "data/item/TFT_Item_Bloodthirster.jpg",
          "data/item/TFT_Item_Bloodthirster.jpg"], 2.34, -1.92, 0.5),
        (["data/item/TFT_Item_Bloodthirster.jpg", "data/item/TFT_Item_Bloodthirster.jpg",
          "data/item/TFT_Item_Bloodthirster.jpg"], 2.34, -1.92, 0.5),
    ]
    
    for row, (icons, avg_place, change, rate) in enumerate(test_data):
        # 设置左侧多图标数据
        table.set_item_data(row, icons, avg_place, change, rate)
        # 设置右侧单图标数据（使用第一个图标）
        table.set_single_item_data(row, icons[0], avg_place, change, rate)
    table.show()
    sys.exit(app.exec())