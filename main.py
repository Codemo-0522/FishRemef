#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
现代化企业级文件批量重命名软件
使用PySide6构建，支持多种重命名格式、可视化预览、进度条等功能
"""

import sys
import os
import re
import random
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import shutil

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QLabel, QPushButton, QLineEdit, QComboBox, QSpinBox,
    QTableWidget, QTableWidgetItem, QProgressBar, QTextEdit, QGroupBox,
    QFileDialog, QMessageBox, QSplitter, QFrame, QCheckBox, QSlider,
    QScrollArea, QTabWidget, QHeaderView
)
from PySide6.QtCore import (
    Qt, QThread, QTimer, Signal, QPropertyAnimation, QEasingCurve,
    QParallelAnimationGroup, QRect, QSize, QMimeData
)
from PySide6.QtGui import (
    QPalette, QColor, QFont, QIcon, QPainter, QPen, QBrush,
    QLinearGradient, QPixmap, QDragEnterEvent, QDropEvent
)


class ModernButton(QPushButton):
    """现代化按钮组件"""
    
    def __init__(self, text="", icon=None, primary=False):
        super().__init__(text)
        self.primary = primary
        self.setup_style()
        
    def setup_style(self):
        if self.primary:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4CAF50, stop:1 #45a049);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5CBF60, stop:1 #4CAF50);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #45a049, stop:1 #3d8b40);
                }
                QPushButton:disabled {
                    background: #cccccc;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #6c7b7f, stop:1 #566063);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 12px;
                    font-weight: normal;
                    text-align: center;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #7c8b8f, stop:1 #667073);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5c6b6f, stop:1 #465053);
                }
            """)


class VariableTag(QLabel):
    """变量标签组件"""
    
    def __init__(self, variable, description, color="#4CAF50"):
        super().__init__()
        self.variable = variable
        self.description = description
        self.setup_style(color)
        
    def setup_style(self, color):
        self.setText(f"{self.variable}")
        self.setToolTip(f"{self.variable} - {self.description}")
        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 4px 8px;
                border-radius: 12px;
                font-size: 11px;
                font-weight: bold;
                margin: 2px;
            }}
            QLabel:hover {{
                background-color: {self.adjust_color(color, 20)};
                transform: scale(1.05);
            }}
        """)
        self.setAlignment(Qt.AlignCenter)
        
    def adjust_color(self, color, amount):
        """调整颜色亮度"""
        if color == "#4CAF50":
            return "#66BB6A"
        elif color == "#2196F3":
            return "#42A5F5"
        elif color == "#FF9800":
            return "#FFB74D"
        elif color == "#9C27B0":
            return "#BA68C8"
        elif color == "#F44336":
            return "#EF5350"
        return color
        
    def mousePressEvent(self, event):
        """点击时复制变量到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(self.variable)
        # 简单的反馈效果
        original_style = self.styleSheet()
        self.setStyleSheet(original_style.replace("background-color:", "background-color: #FFEB3B; color: black; background-color:"))
        QTimer.singleShot(200, lambda: self.setStyleSheet(original_style))


class ModernProgressBar(QProgressBar):
    """现代化进度条组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_style()
        
    def setup_style(self):
        self.setStyleSheet("""
            QProgressBar {
                border: none;
                border-radius: 10px;
                background-color: #E0E0E0;
                text-align: center;
                font-size: 12px;
                color: white;
            }
            QProgressBar::chunk {
                border-radius: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:0.5 #8BC34A, stop:1 #CDDC39);
            }
        """)


class CollapsibleGroupBox(QGroupBox):
    """可折叠的组框"""
    
    def __init__(self, title="", collapsed=False):
        super().__init__()
        self.collapsed = collapsed
        self.setup_ui(title)
        
    def setup_ui(self, title):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 3, 8, 8)  # 减少边距
        self.main_layout.setSpacing(5)  # 减少间距
        
        # 标题栏
        self.title_frame = QFrame()
        self.title_layout = QHBoxLayout(self.title_frame)
        self.title_layout.setContentsMargins(5, 5, 5, 5)
        
        # 折叠按钮
        self.toggle_btn = QPushButton("▼" if not self.collapsed else "▶")
        self.toggle_btn.setMaximumSize(20, 20)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
                color: #4CAF50;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(76, 175, 80, 0.2);
                border-radius: 3px;
            }
        """)
        self.toggle_btn.clicked.connect(self.toggle_collapsed)
        
        # 标题标签
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #ffffff;
                font-size: 13px;
                margin-left: 5px;
            }
        """)
        
        self.title_layout.addWidget(self.toggle_btn)
        self.title_layout.addWidget(self.title_label)
        self.title_layout.addStretch()
        
        # 内容区域
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.main_layout.addWidget(self.title_frame)
        self.main_layout.addWidget(self.content_widget)
        
        # 设置初始状态
        if self.collapsed:
            self.content_widget.hide()
            
        # 设置整体样式
        self.setStyleSheet("""
            CollapsibleGroupBox {
                border: 1px solid #666666;
                border-radius: 8px;
                margin-top: 5px;
                background-color: #2d2d2d;
            }
        """)
        
    def toggle_collapsed(self):
        """切换折叠状态"""
        self.collapsed = not self.collapsed
        if self.collapsed:
            self.content_widget.hide()
            self.toggle_btn.setText("▶")
        else:
            self.content_widget.show()
            self.toggle_btn.setText("▼")
            
    def add_widget(self, widget):
        """添加子组件到内容区域"""
        self.content_layout.addWidget(widget)
        
    def add_layout(self, layout):
        """添加布局到内容区域"""
        self.content_layout.addLayout(layout)


class FileDropArea(QFrame):
    """支持拖拽的文件夹选择区域"""
    
    folder_dropped = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setup_ui()
        
    def setup_ui(self):
        self.setMinimumHeight(60)  # 减少高度
        self.setMaximumHeight(80)  # 限制最大高度
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #4CAF50;
                border-radius: 8px;
                background-color: rgba(76, 175, 80, 0.1);
            }
            QFrame:hover {
                background-color: rgba(76, 175, 80, 0.2);
                border-color: #66BB6A;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 水平布局
        h_layout = QHBoxLayout()
        
        # 图标和提示文字
        self.label = QLabel("📁 拖拽文件夹到此处")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                color: #4CAF50;
                font-size: 14px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
        """)
        
        self.select_btn = ModernButton("选择文件夹", primary=False)
        self.select_btn.setMaximumWidth(100)  # 限制按钮宽度
        self.select_btn.clicked.connect(self.select_folder)
        
        h_layout.addWidget(self.label)
        h_layout.addWidget(self.select_btn)
        
        layout.addLayout(h_layout)
        self.setLayout(layout)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 添加拖拽高亮效果
            self.setStyleSheet("""
                QFrame {
                    border: 3px solid #66BB6A;
                    border-radius: 10px;
                    background-color: rgba(76, 175, 80, 0.3);
                }
            """)
            self.label.setText("📁 松开鼠标以选择文件夹")
            
    def dragLeaveEvent(self, event):
        # 恢复原始样式
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: rgba(76, 175, 80, 0.1);
            }
            QFrame:hover {
                background-color: rgba(76, 175, 80, 0.2);
                border-color: #66BB6A;
            }
        """)
        if not hasattr(self, 'current_folder_name'):
            self.label.setText("📁 拖拽文件夹到此处或点击选择")
        
    def dropEvent(self, event: QDropEvent):
        urls = event.mimeData().urls()
        if urls:
            folder_path = urls[0].toLocalFile()
            if os.path.isdir(folder_path):
                self.folder_dropped.emit(folder_path)
                folder_name = os.path.basename(folder_path)
                self.label.setText(f"📁 已选择: {folder_name}")
                self.current_folder_name = folder_name
                
        # 恢复原始样式
        self.setStyleSheet("""
            QFrame {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: rgba(76, 175, 80, 0.1);
            }
            QFrame:hover {
                background-color: rgba(76, 175, 80, 0.2);
                border-color: #66BB6A;
            }
        """)
                
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_dropped.emit(folder)
            self.label.setText(f"📁 已选择: {os.path.basename(folder)}")


class RenameWorker(QThread):
    """后台重命名工作线程"""
    
    progress_updated = Signal(int, str)
    finished = Signal(bool, str)
    
    def __init__(self, file_list, new_names, target_folder, backup_enabled=False, overwrite_enabled=False):
        super().__init__()
        self.file_list = file_list
        self.new_names = new_names
        self.target_folder = target_folder
        self.backup_enabled = backup_enabled
        self.overwrite_enabled = overwrite_enabled
        
    def run(self):
        try:
            total_files = len(self.file_list)
            success_count = 0
            
            for i, (old_path, new_name) in enumerate(zip(self.file_list, self.new_names)):
                try:
                    old_file = Path(old_path)
                    new_path = Path(self.target_folder) / new_name
                    
                    # 备份原文件
                    if self.backup_enabled and old_file.exists():
                        backup_path = old_file.parent / f"{old_file.stem}_backup{old_file.suffix}"
                        counter = 1
                        while backup_path.exists():
                            backup_path = old_file.parent / f"{old_file.stem}_backup_{counter}{old_file.suffix}"
                            counter += 1
                        shutil.copy2(old_file, backup_path)
                    
                    # 处理文件名冲突
                    if not self.overwrite_enabled:
                        # 不覆盖模式：添加序号避免冲突
                        counter = 1
                        original_new_path = new_path
                        while new_path.exists() and new_path != old_file:
                            stem = original_new_path.stem
                            suffix = original_new_path.suffix
                            new_path = original_new_path.parent / f"{stem}_{counter}{suffix}"
                            counter += 1
                    else:
                        # 覆盖模式：如果目标文件存在且不是源文件本身，则删除目标文件
                        if new_path.exists() and new_path != old_file:
                            new_path.unlink()  # 删除现有文件以实现覆盖
                    
                    # 执行重命名
                    if old_file != new_path:
                        old_file.rename(new_path)
                        success_count += 1
                        
                    progress = int((i + 1) / total_files * 100)
                    self.progress_updated.emit(progress, f"正在重命名: {new_name}")
                    
                    # 模拟处理时间，让进度条更平滑
                    self.msleep(50)
                    
                except Exception as e:
                    print(f"重命名失败 {old_path}: {str(e)}")
                    
            self.finished.emit(True, f"重命名完成！成功处理 {success_count}/{total_files} 个文件")
            
        except Exception as e:
            self.finished.emit(False, f"重命名过程中出现错误: {str(e)}")


class BatchRenameApp(QMainWindow):
    """主应用程序窗口"""
    
    def __init__(self):
        super().__init__()
        self.current_folder = ""
        self.file_list = []
        self.filtered_files = []
        self.rename_worker = None
        
        # 创建延迟刷新定时器
        self.refresh_timer = QTimer()
        self.refresh_timer.setSingleShot(True)
        self.refresh_timer.timeout.connect(self.refresh_preview)
        
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("现代化批量文件重命名工具")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # 设置深色主题
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QWidget {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #666666;
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: #2d2d2d;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #ffffff;
                background-color: #2d2d2d;
            }
            QLineEdit, QComboBox, QSpinBox {
                border: 1px solid #555555;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                background-color: #3c3c3c;
                color: #ffffff;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border-color: #4CAF50;
                background-color: #404040;
            }
            QTableWidget {
                gridline-color: #444444;
                background-color: #2d2d2d;
                alternate-background-color: #333333;
                selection-background-color: #4CAF50;
                border: 1px solid #444444;
                border-radius: 6px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #444444;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 12px;
                border: 1px solid #555555;
                font-weight: bold;
                font-size: 13px;
            }
            QHeaderView::section:hover {
                background-color: #4d4d4d;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                spacing: 8px;
                color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #555555;
                border-radius: 3px;
                background-color: #3c3c3c;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #4CAF50;
                border-radius: 3px;
                background-color: #4CAF50;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAiIGhlaWdodD0iOCIgdmlld0JveD0iMCAwIDEwIDgiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik04LjUgMUwzLjUgNkwxLjUgNCIgc3Ryb2tlPSJ3aGl0ZSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtbGluZWNhcD0icm91bmQiIHN0cm9rZS1saW5lam9pbj0icm91bmQiLz4KPC9zdmc+);
            }
            QCheckBox::indicator:hover {
                border-color: #66BB6A;
            }
        """)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)  # 减少组件间距
        main_layout.setContentsMargins(15, 15, 15, 15)  # 减少边距
        

        
        # 文件夹选择区域
        self.drop_area = FileDropArea()
        main_layout.addWidget(self.drop_area)
        
        # 主要内容分割器
        splitter = QSplitter(Qt.Horizontal)
        splitter.setContentsMargins(0, 0, 0, 0)  # 减少分割器边距
        main_layout.addWidget(splitter, 1)  # 让分割器占用所有可用空间
        
        # 左侧：设置面板
        self.setup_settings_panel(splitter)
        
        # 右侧：预览面板
        self.setup_preview_panel(splitter)
        
        # 底部：操作按钮和进度条
        self.setup_bottom_panel(main_layout)
        
        # 设置分割器比例
        splitter.setSizes([400, 800])
        
    def setup_settings_panel(self, parent):
        """设置左侧设置面板"""
        settings_widget = QWidget()
        settings_layout = QVBoxLayout(settings_widget)
        settings_layout.setContentsMargins(5, 5, 5, 5)  # 减少边距
        settings_layout.setSpacing(8)  # 减少组件间距
        
        # 文件过滤设置
        filter_group = CollapsibleGroupBox("📂 文件过滤", collapsed=False)
        filter_layout = QGridLayout()
        
        filter_layout.addWidget(QLabel("文件扩展名:"), 0, 0)
        self.extension_filter = QLineEdit()
        self.extension_filter.setPlaceholderText("例: .jpg,.png,.txt (空白=所有文件)")
        filter_layout.addWidget(self.extension_filter, 0, 1)
        
        filter_layout.addWidget(QLabel("排序方式:"), 1, 0)
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "修改时间(新到旧)", "修改时间(旧到新)", 
            "创建时间(新到旧)", "创建时间(旧到新)",
            "文件名(A-Z)", "文件名(Z-A)", 
            "文件名(数字排序)", "文件名(自然排序)",
            "文件大小(大到小)", "文件大小(小到大)",
            "文件类型(A-Z)", "文件类型(Z-A)",
            "文件扩展名(A-Z)", "文件扩展名(Z-A)",
            "随机排序"
        ])
        filter_layout.addWidget(self.sort_combo, 1, 1)
        
        filter_group.add_layout(filter_layout)
        settings_layout.addWidget(filter_group)
        
        # 重命名设置
        rename_group = CollapsibleGroupBox("✏️ 智能重命名格式", collapsed=False)
        rename_layout = QVBoxLayout()
        
        # 自定义格式输入
        format_label = QLabel("重命名格式:")
        format_label.setStyleSheet("QLabel { font-weight: bold; margin-bottom: 5px; }")
        rename_layout.addWidget(format_label)
        
        self.custom_format = QLineEdit()
        self.custom_format.setPlaceholderText("例: {name}_{date}_{index} 或 Photo_{index}_by_Author")
        self.custom_format.setText("{name}")  # 默认格式
        self.custom_format.setStyleSheet("""
            QLineEdit {
                font-size: 14px;
                padding: 10px;
                border: 2px solid #4CAF50;
                border-radius: 8px;
                background-color: #3c3c3c;
            }
            QLineEdit:focus {
                border-color: #66BB6A;
                background-color: #404040;
            }
        """)
        rename_layout.addWidget(self.custom_format)
        
        # 序号设置
        number_layout = QHBoxLayout()
        number_layout.addWidget(QLabel("起始序号:"))
        self.start_number = QSpinBox()
        self.start_number.setRange(0, 9999)
        self.start_number.setValue(1)
        number_layout.addWidget(self.start_number)
        
        number_layout.addWidget(QLabel("序号位数:"))
        self.number_digits = QSpinBox()
        self.number_digits.setRange(1, 6)
        self.number_digits.setValue(3)
        number_layout.addWidget(self.number_digits)
        number_layout.addStretch()
        
        rename_layout.addLayout(number_layout)
        
        # 快速格式按钮
        quick_format_label = QLabel("🚀 快速格式:")
        quick_format_label.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; }")
        rename_layout.addWidget(quick_format_label)
        
        quick_buttons_layout = QHBoxLayout()
        
        formats = [
            ("序号", "{index}"),
            ("原名+序号", "{name}_{index}"),
            ("日期+序号", "{date}_{index}"),
            ("时间戳", "{datetime}_{name}"),
        ]
        
        for name, format_str in formats:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 5px 10px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                    border-color: #66BB6A;
                }
            """)
            btn.clicked.connect(lambda checked, f=format_str: self.custom_format.setText(f))
            quick_buttons_layout.addWidget(btn)
            
        quick_buttons_layout.addStretch()
        rename_layout.addLayout(quick_buttons_layout)
        
        # 变量标签区域
        variables_label = QLabel("💡 可用变量 (点击复制):")
        variables_label.setStyleSheet("QLabel { font-weight: bold; margin-top: 10px; color: #ffffff; }")
        rename_layout.addWidget(variables_label)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setMaximumHeight(120)
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #444444;
                border-radius: 6px;
                background-color: #2d2d2d;
            }
            QScrollBar:vertical {
                background-color: #3d3d3d;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #4CAF50;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #66BB6A;
            }
        """)
        
        # 变量容器
        variables_widget = QWidget()
        variables_layout = QVBoxLayout(variables_widget)
        variables_layout.setContentsMargins(10, 10, 10, 10)
        
        # 定义变量分组和颜色
        variable_groups = [
            ("基础变量", [
                ("{name}", "清理后文件名", "#4CAF50"),
                ("{original}", "原始文件名", "#4CAF50"),
                ("{index}", "序号", "#4CAF50"),
            ], "#4CAF50"),
            ("时间变量", [
                ("{date}", "日期(20241220)", "#2196F3"),
                ("{datetime}", "完整时间", "#2196F3"),
                ("{year}", "年份", "#2196F3"),
                ("{month}", "月份", "#2196F3"),
                ("{day}", "日期", "#2196F3"),
                ("{time}", "时间(143052)", "#2196F3"),
            ], "#2196F3"),
            ("文件信息", [
                ("{size}", "文件大小(字节)", "#FF9800"),
                ("{size_kb}", "文件大小(KB)", "#FF9800"),
                ("{size_mb}", "文件大小(MB)", "#FF9800"),
                ("{ext}", "扩展名", "#FF9800"),
                ("{parent}", "父文件夹名", "#FF9800"),
            ], "#FF9800"),
        ]
        
        for group_name, variables, group_color in variable_groups:
            # 分组标题
            group_label = QLabel(f"📂 {group_name}")
            group_label.setStyleSheet(f"""
                QLabel {{
                    font-weight: bold;
                    color: {group_color};
                    margin: 5px 0px 3px 0px;
                    font-size: 12px;
                }}
            """)
            variables_layout.addWidget(group_label)
            
            # 变量标签行
            tags_layout = QHBoxLayout()
            tags_layout.setSpacing(5)
            
            for variable, description, color in variables:
                tag = VariableTag(variable, description, color)
                tags_layout.addWidget(tag)
            
            tags_layout.addStretch()
            variables_layout.addLayout(tags_layout)
        
        scroll_area.setWidget(variables_widget)
        rename_layout.addWidget(scroll_area)
        
        # 简化的示例说明
        example_label = QLabel("📝 示例: {name}_{index} → 清理后文件名_001.jpg\n💡 启用智能清理可自动移除网站标识和垃圾信息")
        example_label.setStyleSheet("""
            QLabel { 
                font-size: 12px; 
                color: #CCCCCC; 
                background-color: #2d2d2d;
                padding: 8px;
                border-radius: 4px;
                border: 1px solid #444444;
                margin-top: 5px;
                font-style: italic;
            }
        """)
        example_label.setWordWrap(True)
        rename_layout.addWidget(example_label)
        
        rename_group.add_layout(rename_layout)
        settings_layout.addWidget(rename_group)
        
        # 智能文件名清理
        cleanup_group = CollapsibleGroupBox("🧹 智能文件名清理", collapsed=True)  # 默认折叠
        cleanup_layout = QVBoxLayout()
        
        # 启用清理功能
        self.enable_cleanup = QCheckBox("启用智能清理")
        self.enable_cleanup.setToolTip("自动识别并移除文件名中的网站标识、重复内容等垃圾信息")
        self.enable_cleanup.setChecked(False)
        cleanup_layout.addWidget(self.enable_cleanup)
        
        # 清理模式选择
        mode_layout = QHBoxLayout()
        mode_layout.addWidget(QLabel("清理模式:"))
        self.cleanup_mode = QComboBox()
        self.cleanup_mode.addItems([
            "智能识别", "自定义文本", "自定义正则"
        ])
        mode_layout.addWidget(self.cleanup_mode)
        mode_layout.addStretch()
        cleanup_layout.addLayout(mode_layout)
        
        # 自定义规则输入
        rules_layout = QVBoxLayout()
        rules_layout.addWidget(QLabel("自定义清理规则:"))
        
        # 添加规则说明
        rules_help = QLabel("💡 规则说明:\n• 智能识别: 使用预设规则自动清理\n• 自定义文本: 精确删除指定文字，如输入 (1) 只删除完整的 (1)\n• 自定义正则: 使用正则表达式，如 \\(\\d+\\) 匹配括号内任意数字")
        rules_help.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #CCCCCC;
                background-color: #2d2d2d;
                padding: 5px;
                border-radius: 4px;
                border: 1px solid #444444;
            }
        """)
        rules_help.setWordWrap(True)
        rules_layout.addWidget(rules_help)
        
        self.cleanup_rules = QTextEdit()
        self.cleanup_rules.setMaximumHeight(80)
        self.cleanup_rules.setPlaceholderText("每行一个规则，例如:\n(1)\n百度网盘\n\\(\\d+\\)\n下载")
        rules_layout.addWidget(self.cleanup_rules)
        cleanup_layout.addLayout(rules_layout)
        
        # 预设规则按钮
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("快速规则:"))
        
        presets = [
            ("文本示例", "下载\n副本\n(1)\n(2)\n百度网盘"),
            ("正则示例", "\\(\\d+\\)\n\\[.*?\\]\n下载.*\n副本\\d*"),
        ]
        
        for name, rules in presets:
            btn = QPushButton(name)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #404040;
                    border: 1px solid #666666;
                    border-radius: 4px;
                    padding: 4px 8px;
                    font-size: 11px;
                }
                QPushButton:hover {
                    background-color: #4CAF50;
                    border-color: #66BB6A;
                }
            """)
            btn.clicked.connect(lambda checked, r=rules: self.cleanup_rules.setText(r))
            preset_layout.addWidget(btn)
            
        preset_layout.addStretch()
        cleanup_layout.addLayout(preset_layout)
        
        cleanup_group.add_layout(cleanup_layout)
        settings_layout.addWidget(cleanup_group)
        
        # 高级选项
        advanced_group = CollapsibleGroupBox("⚙️ 高级选项", collapsed=True)  # 默认折叠
        advanced_layout = QGridLayout()
        
        self.keep_extension = QCheckBox("保持原文件扩展名")
        self.keep_extension.setChecked(True)
        self.keep_extension.setToolTip("勾选: photo.jpg → 新名称.jpg\n取消: photo.jpg → 新名称 (无扩展名)")
        advanced_layout.addWidget(self.keep_extension, 0, 0)
        
        self.backup_original = QCheckBox("备份原文件")
        self.backup_original.setToolTip("重命名前在同目录创建备份副本\n例如: photo.jpg → photo_backup.jpg")
        advanced_layout.addWidget(self.backup_original, 0, 1)
        
        self.case_sensitive = QCheckBox("区分大小写")
        self.case_sensitive.setToolTip("勾选: File.txt 和 file.txt 视为不同文件\n取消: 视为相同文件")
        advanced_layout.addWidget(self.case_sensitive, 1, 0)
        
        self.overwrite_existing = QCheckBox("覆盖同名文件")
        self.overwrite_existing.setToolTip("勾选: 直接覆盖同名文件 (危险!)\n取消: 自动添加序号避免冲突")
        advanced_layout.addWidget(self.overwrite_existing, 1, 1)
        
        advanced_group.add_layout(advanced_layout)
        settings_layout.addWidget(advanced_group)
        
        # 移除多余的拉伸空间，让组件紧凑排列
        parent.addWidget(settings_widget)
        
    def setup_preview_panel(self, parent):
        """设置右侧预览面板"""
        preview_widget = QWidget()
        preview_layout = QVBoxLayout(preview_widget)
        preview_layout.setContentsMargins(5, 5, 5, 5)  # 减少边距
        preview_layout.setSpacing(8)  # 减少组件间距
        
        # 预览标题
        preview_title = QLabel("👀 重命名预览")
        preview_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #4CAF50;
                padding: 10px;
            }
        """)
        preview_layout.addWidget(preview_title)
        
        # 统计信息
        stats_layout = QHBoxLayout()
        
        self.total_files_label = QLabel("总文件数: 0")
        self.selected_files_label = QLabel("将重命名: 0")
        self.conflicts_label = QLabel("冲突: 0")
        
        # 设置统计标签样式
        self.total_files_label.setStyleSheet("""
            QLabel {
                background-color: #404040;
                color: #ffffff;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #555555;
            }
        """)
        
        self.selected_files_label.setStyleSheet("""
            QLabel {
                background-color: #2196F3;
                color: #ffffff;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #1976D2;
            }
        """)
        
        self.conflicts_label.setStyleSheet("""
            QLabel {
                background-color: #4CAF50;
                color: #ffffff;
                padding: 8px 12px;
                border-radius: 6px;
                font-weight: bold;
                border: 1px solid #45a049;
            }
        """)
        
        # 将标签添加到布局
        stats_layout.addWidget(self.total_files_label)
        stats_layout.addWidget(self.selected_files_label)
        stats_layout.addWidget(self.conflicts_label)
        stats_layout.addStretch()
        
        # 添加全选/全不选按钮和执行按钮
        self.select_all_btn = ModernButton("全选", primary=False)
        self.select_none_btn = ModernButton("全不选", primary=False)
        self.execute_btn = ModernButton("🚀 执行重命名", primary=True)
        
        # 调整按钮宽度，确保文字显示完整
        self.select_all_btn.setMinimumWidth(50)
        self.select_none_btn.setMinimumWidth(60)
        self.execute_btn.setMinimumWidth(120)
        
        stats_layout.addWidget(self.select_all_btn)
        stats_layout.addWidget(self.select_none_btn)
        stats_layout.addWidget(self.execute_btn)
        preview_layout.addLayout(stats_layout)
        
        # 预览表格
        self.preview_table = QTableWidget()
        self.preview_table.setColumnCount(4)
        self.preview_table.setHorizontalHeaderLabels(["选择", "原文件名", "新文件名", "状态"])
        
        # 设置表格列宽 - 允许用户调整
        header = self.preview_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)  # 选择列固定宽度
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)  # 原文件名可调整
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Interactive)  # 新文件名可调整
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)  # 状态列自动拉伸
        
        self.preview_table.setColumnWidth(0, 80)  # 增加选择列宽度
        self.preview_table.setColumnWidth(1, 350)
        self.preview_table.setColumnWidth(2, 350)
        
        # 设置行号显示
        vertical_header = self.preview_table.verticalHeader()
        vertical_header.setVisible(True)
        vertical_header.setDefaultSectionSize(35)
        vertical_header.setFixedWidth(60)  # 设置固定宽度确保序号完整显示
        vertical_header.setStyleSheet("""
            QHeaderView::section {
                background-color: #3d3d3d;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #555555;
                font-weight: bold;
                font-size: 12px;
                text-align: center;
            }
            QHeaderView::section:hover {
                background-color: #4d4d4d;
            }
        """)
        
        # 启用排序
        self.preview_table.setSortingEnabled(True)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.setSelectionBehavior(QTableWidget.SelectRows)
        
        preview_layout.addWidget(self.preview_table)
        
        parent.addWidget(preview_widget)
        
    def setup_bottom_panel(self, parent_layout):
        """设置底部操作面板"""
        bottom_widget = QWidget()
        bottom_widget.setMaximumHeight(60)  # 限制底部区域高度
        bottom_layout = QVBoxLayout(bottom_widget)
        bottom_layout.setContentsMargins(0, 5, 0, 5)  # 减少边距
        bottom_layout.setSpacing(5)  # 减少间距
        
        # 进度条
        self.progress_bar = ModernProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)  # 减少进度条高度
        self.progress_bar.setMaximumHeight(25)
        bottom_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("QLabel { color: #4CAF50; font-weight: bold; font-size: 12px; }")
        self.progress_label.setVisible(False)
        self.progress_label.setMaximumHeight(20)  # 限制标签高度
        bottom_layout.addWidget(self.progress_label)
        
        # 底部现在只有进度条，不需要额外的按钮布局
        parent_layout.addWidget(bottom_widget)
        
    def setup_connections(self):
        """设置信号连接"""
        self.drop_area.folder_dropped.connect(self.load_folder)
        self.execute_btn.clicked.connect(self.execute_rename)
        self.select_all_btn.clicked.connect(self.select_all_files)
        self.select_none_btn.clicked.connect(self.select_no_files)
        
        # 设置变化时自动延迟刷新预览
        self.extension_filter.textChanged.connect(self.schedule_refresh)
        self.sort_combo.currentTextChanged.connect(self.schedule_refresh)
        self.start_number.valueChanged.connect(self.schedule_refresh)
        self.number_digits.valueChanged.connect(self.schedule_refresh)
        self.custom_format.textChanged.connect(self.schedule_refresh)
        
        # 复选框变化时也自动刷新
        self.keep_extension.toggled.connect(self.schedule_refresh)
        self.backup_original.toggled.connect(self.schedule_refresh)
        self.case_sensitive.toggled.connect(self.schedule_refresh)
        self.overwrite_existing.toggled.connect(self.schedule_refresh)
        
        # 清理功能变化时也自动刷新
        self.enable_cleanup.toggled.connect(self.schedule_refresh)
        self.cleanup_mode.currentTextChanged.connect(self.schedule_refresh)
        self.cleanup_rules.textChanged.connect(self.schedule_refresh)
        
    def schedule_refresh(self):
        """计划延迟刷新预览（避免频繁刷新）"""
        self.refresh_timer.stop()
        self.refresh_timer.start(300)  # 300ms延迟
        
    def refresh_preview_immediately(self):
        """立即刷新预览"""
        self.refresh_timer.stop()
        self.refresh_preview()
        
    def load_folder(self, folder_path):
        """加载文件夹中的文件"""
        self.current_folder = folder_path
        self.scan_files()
        self.refresh_preview_immediately()
        
    def scan_files(self):
        """扫描文件夹中的文件"""
        if not self.current_folder:
            return
            
        self.file_list = []
        try:
            folder_path = Path(self.current_folder)
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    self.file_list.append(str(file_path))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法读取文件夹: {str(e)}")
            
    def filter_and_sort_files(self):
        """过滤和排序文件"""
        if not self.file_list:
            self.filtered_files = []
            return
            
        # 扩展名过滤
        extension_filter = self.extension_filter.text().strip()
        if extension_filter:
            extensions = [ext.strip().lower() for ext in extension_filter.split(',')]
            extensions = [ext if ext.startswith('.') else f'.{ext}' for ext in extensions]
            filtered = [f for f in self.file_list 
                       if Path(f).suffix.lower() in extensions]
        else:
            filtered = self.file_list.copy()
            
        # 排序
        sort_option = self.sort_combo.currentText()
        
        if "修改时间" in sort_option:
            filtered.sort(key=lambda x: os.path.getmtime(x), 
                         reverse="新到旧" in sort_option)
        elif "创建时间" in sort_option:
            filtered.sort(key=lambda x: os.path.getctime(x), 
                         reverse="新到旧" in sort_option)
        elif "文件名(数字排序)" in sort_option:
            # 数字排序：提取文件名中的数字进行排序
            def extract_numbers(filename):
                numbers = re.findall(r'\d+', os.path.basename(filename))
                return [int(n) for n in numbers] if numbers else [0]
            filtered.sort(key=extract_numbers)
        elif "文件名(自然排序)" in sort_option:
            # 自然排序：将数字作为数字而不是字符串排序
            def natural_sort_key(filename):
                name = os.path.basename(filename).lower()
                return [int(text) if text.isdigit() else text for text in re.split(r'(\d+)', name)]
            filtered.sort(key=natural_sort_key)
        elif "文件名" in sort_option:
            filtered.sort(key=lambda x: os.path.basename(x).lower(),
                         reverse="Z-A" in sort_option)
        elif "文件大小" in sort_option:
            filtered.sort(key=lambda x: os.path.getsize(x),
                         reverse="大到小" in sort_option)
        elif "文件类型" in sort_option:
            filtered.sort(key=lambda x: os.path.splitext(os.path.basename(x))[1].lower(),
                         reverse="Z-A" in sort_option)
        elif "文件扩展名" in sort_option:
            filtered.sort(key=lambda x: Path(x).suffix.lower(),
                         reverse="Z-A" in sort_option)
        elif "随机排序" in sort_option:
            random.shuffle(filtered)
                         
        self.filtered_files = filtered
        
    def clean_filename(self, filename):
        """智能清理文件名"""
        if not self.enable_cleanup.isChecked():
            return filename
            
        original_name = filename
        cleaned_name = filename
        mode = self.cleanup_mode.currentText()
        
        # 根据模式处理清理规则
        if mode == "智能识别":
            # 预定义的智能清理规则
            patterns = [
                # 网站标识
                r'百度网盘.*?[-_]?',
                r'阿里云盘.*?[-_]?',
                r'腾讯微云.*?[-_]?',
                r'夸克网盘.*?[-_]?',
                r'蓝奏云.*?[-_]?',
                r'OneDrive.*?[-_]?',
                r'Google.*?Drive.*?[-_]?',
                r'Dropbox.*?[-_]?',
                r'iCloud.*?[-_]?',
                r'115网盘.*?[-_]?',
                r'天翼云盘.*?[-_]?',
                r'和彩云.*?[-_]?',
                # 下载标识
                r'[-_]?下载.*',
                r'[-_]?副本\d*',
                r'[-_]?拷贝\d*',
                r'[-_]?copy\d*',
                r'\(\d+\)$',
                r'[-_]\d+$',
                r'新建.*',
                r'untitled.*',
                # 括号内容（只清理明显的下载标识）
                r'\[.*?下载.*?\]',
                r'【.*?下载.*?】',
                # 重复词
                r'\b(\w+)\s+\1\b',  # 重复的单词
                r'(\w+)[-_]\1',     # 用分隔符重复的词
                # 特殊符号清理
                r'[-_]{2,}',  # 多个连续的横线或下划线
                r'^[-_]+|[-_]+$',  # 开头结尾的横线下划线
            ]
            
            # 执行智能清理（所有都是正则表达式）
            for pattern in patterns:
                try:
                    cleaned_name = re.sub(pattern, '', cleaned_name, flags=re.IGNORECASE)
                except re.error:
                    continue
                    
        elif mode == "自定义文本":
            # 自定义文本模式 - 严格按照用户输入的文字进行删除
            if self.cleanup_rules.toPlainText().strip():
                custom_rules = self.cleanup_rules.toPlainText().strip().split('\n')
                for rule in custom_rules:
                    rule = rule.strip()
                    if rule:
                        # 直接使用字符串替换，不使用正则表达式
                        cleaned_name = cleaned_name.replace(rule, '')
                        
        elif mode == "自定义正则":
            # 自定义正则表达式模式
            if self.cleanup_rules.toPlainText().strip():
                custom_rules = self.cleanup_rules.toPlainText().strip().split('\n')
                for rule in custom_rules:
                    rule = rule.strip()
                    if rule:
                        try:
                            # 直接作为正则表达式使用
                            cleaned_name = re.sub(rule, '', cleaned_name, flags=re.IGNORECASE)
                        except re.error:
                            # 正则表达式错误时跳过
                            continue
        
        # 后处理清理
        cleaned_name = self.post_process_cleanup(cleaned_name)
        
        # 确保清理后的名称不为空
        if not cleaned_name.strip() or len(cleaned_name.strip()) < 2:
            return original_name
            
        return cleaned_name.strip()
    
    def post_process_cleanup(self, filename):
        """后处理清理"""
        # 清理多余的空格和符号
        filename = re.sub(r'\s+', ' ', filename)  # 多个空格变一个
        filename = re.sub(r'[-_]{2,}', '_', filename)  # 多个连续符号
        filename = re.sub(r'^[-_\s]+|[-_\s]+$', '', filename)  # 清理首尾
        
        # 最终清理
        filename = re.sub(r'\s+', ' ', filename).strip()
        filename = re.sub(r'^[-_\s]+|[-_\s]+$', '', filename)
        
        return filename
        
    def generate_new_names(self):
        """生成新文件名"""
        if not self.filtered_files:
            return []
            
        new_names = []
        start_num = self.start_number.value()
        digits = self.number_digits.value()
        custom_format = self.custom_format.text().strip()
        
        # 如果没有自定义格式，使用默认格式
        if not custom_format:
            custom_format = "{name}_{index}"
        
        for i, file_path in enumerate(self.filtered_files):
            file_obj = Path(file_path)
            original_name = file_obj.stem
            
            # 应用智能清理
            cleaned_name = self.clean_filename(original_name)
            
            extension = file_obj.suffix if self.keep_extension.isChecked() else ""
            
            # 获取文件信息
            file_stat = os.stat(file_path)
            
            # 准备所有可用的格式变量
            format_vars = {
                'name': cleaned_name,  # 使用清理后的名称
                'original': original_name,  # 添加原始名称变量
                'date': datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y%m%d"),
                'datetime': datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y%m%d_%H%M%S"),
                'time': datetime.fromtimestamp(file_stat.st_mtime).strftime("%H%M%S"),
                'year': datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y"),
                'month': datetime.fromtimestamp(file_stat.st_mtime).strftime("%m"),
                'day': datetime.fromtimestamp(file_stat.st_mtime).strftime("%d"),
                'index': str(start_num + i).zfill(digits),
                'size': str(file_stat.st_size),
                'size_kb': str(round(file_stat.st_size / 1024, 1)),
                'size_mb': str(round(file_stat.st_size / (1024*1024), 1)),
                'ext': extension.lstrip('.'),
                'parent': file_obj.parent.name,
            }
            
            try:
                # 使用自定义格式生成新文件名
                new_name = custom_format.format(**format_vars) + extension
            except (KeyError, ValueError) as e:
                # 如果格式有错误，使用安全的默认格式
                new_name = f"{original_name}_{str(start_num + i).zfill(digits)}{extension}"
                
            new_names.append(new_name)
            
        return new_names
        
    def check_conflicts(self, new_names):
        """检查命名冲突"""
        conflicts = {}
        name_counts = {}
        
        # 检查重复的新名称
        for i, name in enumerate(new_names):
            if name in name_counts:
                name_counts[name].append(i)
            else:
                name_counts[name] = [i]
                
        # 检查与现有文件的冲突
        existing_files = set(os.path.basename(f) for f in os.listdir(self.current_folder) 
                           if os.path.isfile(os.path.join(self.current_folder, f)))
        
        for name, indices in name_counts.items():
            if len(indices) > 1:
                for idx in indices:
                    conflicts[idx] = "重复名称"
            elif name in existing_files and not self.overwrite_existing.isChecked():
                conflicts[indices[0]] = "文件已存在"
                
        return conflicts
        
    def refresh_preview(self):
        """刷新预览表格"""
        self.filter_and_sort_files()
        new_names = self.generate_new_names()
        conflicts = self.check_conflicts(new_names)
        
        # 更新统计信息
        total_files = len(self.filtered_files)
        self.total_files_label.setText(f"总文件数: {total_files}")
        self.selected_files_label.setText(f"将重命名: {total_files}")
        self.conflicts_label.setText(f"冲突: {len(conflicts)}")
        
        # 冲突提示颜色
        if conflicts:
            self.conflicts_label.setStyleSheet("""
                QLabel {
                    background-color: #F44336;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: 1px solid #D32F2F;
                }
            """)
        else:
            self.conflicts_label.setStyleSheet("""
                QLabel {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-weight: bold;
                    border: 1px solid #45a049;
                }
            """)
        
        # 更新表格
        self.preview_table.setRowCount(len(self.filtered_files))
        
        for i, (file_path, new_name) in enumerate(zip(self.filtered_files, new_names)):
            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            # 连接复选框变化事件以更新统计
            checkbox.toggled.connect(self.update_selection_count)
            self.preview_table.setCellWidget(i, 0, checkbox)
            
            # 原文件名
            original_item = QTableWidgetItem(os.path.basename(file_path))
            original_item.setFlags(original_item.flags() & ~Qt.ItemIsEditable)
            original_item.setToolTip(os.path.basename(file_path))  # 添加完整文件名提示
            self.preview_table.setItem(i, 1, original_item)
            
            # 新文件名
            new_item = QTableWidgetItem(new_name)
            new_item.setFlags(new_item.flags() & ~Qt.ItemIsEditable)
            new_item.setToolTip(new_name)  # 添加完整文件名提示
            self.preview_table.setItem(i, 2, new_item)
            
            # 状态
            if i in conflicts:
                status_item = QTableWidgetItem(f"⚠️ {conflicts[i]}")
                status_item.setBackground(QColor("#F44336"))
            else:
                status_item = QTableWidgetItem("✅ 就绪")
                status_item.setBackground(QColor("#4CAF50"))
                
            status_item.setFlags(status_item.flags() & ~Qt.ItemIsEditable)
            self.preview_table.setItem(i, 3, status_item)
            
        # 初始更新选择计数
        self.update_selection_count()
            
    def update_selection_count(self):
        """更新选择文件的计数"""
        selected_count = 0
        for i in range(self.preview_table.rowCount()):
            checkbox = self.preview_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        
        self.selected_files_label.setText(f"将重命名: {selected_count}")
            
    def select_all_files(self):
        """全选文件"""
        for i in range(self.preview_table.rowCount()):
            checkbox = self.preview_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(True)
        # 手动触发一次计数更新（因为批量操作可能不会触发所有信号）
        self.update_selection_count()
                
    def select_no_files(self):
        """全不选文件"""
        for i in range(self.preview_table.rowCount()):
            checkbox = self.preview_table.cellWidget(i, 0)
            if checkbox:
                checkbox.setChecked(False)
        # 手动触发一次计数更新
        self.update_selection_count()
                
    def get_selected_files(self):
        """获取选中的文件"""
        selected_files = []
        selected_new_names = []
        new_names = self.generate_new_names()
        
        for i in range(self.preview_table.rowCount()):
            checkbox = self.preview_table.cellWidget(i, 0)
            if checkbox and checkbox.isChecked():
                selected_files.append(self.filtered_files[i])
                selected_new_names.append(new_names[i])
                
        return selected_files, selected_new_names
        
    def execute_rename(self):
        """执行重命名"""
        if not self.filtered_files:
            QMessageBox.warning(self, "警告", "没有文件可以重命名！")
            return
            
        selected_files, selected_new_names = self.get_selected_files()
        
        if not selected_files:
            QMessageBox.warning(self, "警告", "请至少选择一个文件进行重命名！")
            return
            
        # 检查冲突
        conflicts = self.check_conflicts(self.generate_new_names())
        if conflicts and not self.overwrite_existing.isChecked():
            reply = QMessageBox.question(
                self, "确认", 
                f"检测到 {len(conflicts)} 个命名冲突。是否继续？\n冲突的文件将被跳过。",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # 确认对话框
        if self.overwrite_existing.isChecked():
            reply = QMessageBox.question(
                self, "确认重命名", 
                f"确定要重命名 {len(selected_files)} 个文件吗？\n⚠️ 启用了覆盖模式，同名文件将被删除！\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No
            )
        else:
            reply = QMessageBox.question(
                self, "确认重命名", 
                f"确定要重命名 {len(selected_files)} 个文件吗？\n同名文件将自动添加序号。\n此操作不可撤销！",
                QMessageBox.Yes | QMessageBox.No
            )
        
        if reply == QMessageBox.Yes:
            self.start_rename_process(selected_files, selected_new_names)
            
    def start_rename_process(self, file_list, new_names):
        """开始重命名进程"""
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("准备重命名...")
        
        # 禁用按钮
        self.execute_btn.setEnabled(False)
        self.execute_btn.setText("重命名中...")
        
        # 获取高级选项设置
        backup_enabled = self.backup_original.isChecked()
        overwrite_enabled = self.overwrite_existing.isChecked()
        
        # 创建并启动工作线程
        self.rename_worker = RenameWorker(
            file_list, 
            new_names, 
            self.current_folder,
            backup_enabled,
            overwrite_enabled
        )
        self.rename_worker.progress_updated.connect(self.update_progress)
        self.rename_worker.finished.connect(self.rename_finished)
        self.rename_worker.start()
        
    def update_progress(self, progress, message):
        """更新进度"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        
    def rename_finished(self, success, message):
        """重命名完成"""
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # 恢复按钮
        self.execute_btn.setEnabled(True)
        self.execute_btn.setText("🚀 执行重命名")
        
        # 显示结果
        if success:
            QMessageBox.information(self, "完成", message)
            # 重新扫描文件夹并刷新预览
            self.scan_files()
            self.refresh_preview()
        else:
            QMessageBox.critical(self, "错误", message)


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("现代化批量文件重命名工具")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("ModernTools")
    
    # 创建并显示主窗口
    window = BatchRenameApp()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
