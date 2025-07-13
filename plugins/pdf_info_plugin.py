"""
PDF信息查看插件
显示PDF文档的详细信息，包括元数据、页面信息等
"""

import sys
import os

# 添加父目录到路径以便导入插件接口
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_viewer.plugin_manager import PluginInterface
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton,
    QLabel, QTabWidget, QWidget, QFormLayout, QLineEdit,
    QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont


class PDFInfoDialog(QDialog):
    """PDF信息对话框"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("PDF文档信息")
        self.setModal(False)
        self.resize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 基本信息选项卡
        info_tab = self.create_info_tab()
        tab_widget.addTab(info_tab, "基本信息")
        
        # 页面信息选项卡
        pages_tab = self.create_pages_tab()
        tab_widget.addTab(pages_tab, "页面信息")
        
        # 文档结构选项卡
        structure_tab = self.create_structure_tab()
        tab_widget.addTab(structure_tab, "文档结构")
        
        # 关闭按钮
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
    def create_info_tab(self):
        """创建基本信息选项卡"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # 创建只读文本框
        self.title_edit = QLineEdit()
        self.title_edit.setReadOnly(True)
        
        self.author_edit = QLineEdit()
        self.author_edit.setReadOnly(True)
        
        self.subject_edit = QLineEdit()
        self.subject_edit.setReadOnly(True)
        
        self.creator_edit = QLineEdit()
        self.creator_edit.setReadOnly(True)
        
        self.producer_edit = QLineEdit()
        self.producer_edit.setReadOnly(True)
        
        self.creation_date_edit = QLineEdit()
        self.creation_date_edit.setReadOnly(True)
        
        self.mod_date_edit = QLineEdit()
        self.mod_date_edit.setReadOnly(True)
        
        self.pages_edit = QLineEdit()
        self.pages_edit.setReadOnly(True)
        
        # 添加到表单
        layout.addRow("标题:", self.title_edit)
        layout.addRow("作者:", self.author_edit)
        layout.addRow("主题:", self.subject_edit)
        layout.addRow("创建者:", self.creator_edit)
        layout.addRow("制作程序:", self.producer_edit)
        layout.addRow("创建日期:", self.creation_date_edit)
        layout.addRow("修改日期:", self.mod_date_edit)
        layout.addRow("总页数:", self.pages_edit)
        
        return widget
        
    def create_pages_tab(self):
        """创建页面信息选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.pages_text = QTextEdit()
        self.pages_text.setReadOnly(True)
        self.pages_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.pages_text)
        
        return widget
        
    def create_structure_tab(self):
        """创建文档结构选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        self.structure_text = QTextEdit()
        self.structure_text.setReadOnly(True)
        self.structure_text.setFont(QFont("Courier", 9))
        layout.addWidget(self.structure_text)
        
        return widget
        
    def update_info(self):
        """更新信息显示"""
        if not self.main_window.current_pdf:
            return
            
        try:
            # 获取文档元数据
            metadata = self.main_window.current_pdf.get_metadata()
            
            # 更新基本信息
            self.title_edit.setText(metadata.get('title', '未知'))
            self.author_edit.setText(metadata.get('author', '未知'))
            self.subject_edit.setText(metadata.get('subject', '未知'))
            self.creator_edit.setText(metadata.get('creator', '未知'))
            self.producer_edit.setText(metadata.get('producer', '未知'))
            self.creation_date_edit.setText(metadata.get('creationDate', '未知'))
            self.mod_date_edit.setText(metadata.get('modDate', '未知'))
            self.pages_edit.setText(str(self.main_window.current_pdf.get_page_count()))
            
            # 更新页面信息
            self.update_pages_info()
            
            # 更新文档结构
            self.update_structure_info()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"获取文档信息失败: {str(e)}")
            
    def update_pages_info(self):
        """更新页面信息"""
        text = "页面详细信息:\n\n"
        try:
            for i in range(self.main_window.current_pdf.get_page_count()):
                width, height = self.main_window.current_pdf.get_page_size(i)
                text += f"页面 {i+1}: {width:.1f} x {height:.1f} 像素\n"
        except Exception as e:
            text += f"无法获取页面信息: {str(e)}"
        
        self.pages_text.setText(text)
        
    def update_structure_info(self):
        """更新文档结构信息"""
        text = "文档目录结构:\n\n"
        try:
            outline = self.main_window.current_pdf.get_outline()
            if outline:
                self.format_outline(outline, text, 0)
            else:
                text += "此文档没有目录结构"
        except Exception as e:
            text += f"无法获取文档结构: {str(e)}"
            
        self.structure_text.setText(text)
        
    def format_outline(self, outline, text, level):
        """格式化目录结构"""
        for item in outline:
            indent = "  " * level
            text += f"{indent}- {item['title']} (页面 {item['page'] + 1})\n"
            if 'children' in item and item['children']:
                self.format_outline(item['children'], text, level + 1)


class PDFInfoPlugin(PluginInterface):
    """PDF信息查看插件"""
    
    @property
    def name(self):
        return "PDF信息查看器"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "查看PDF文档的详细信息，包括元数据和结构"
    
    def initialize(self, main_window):
        """初始化插件"""
        self.main_window = main_window
        
        # 创建信息对话框
        self.info_dialog = PDFInfoDialog(main_window)
        
        # 添加菜单项
        info_action = main_window.plugins_menu.addAction("文档信息")
        info_action.setShortcut("Ctrl+I")
        info_action.triggered.connect(self.show_info_dialog)
        
        print(f"插件 {self.name} 初始化完成")
        
    def finalize(self):
        """清理插件资源"""
        if hasattr(self, 'info_dialog'):
            self.info_dialog.close()
        print(f"插件 {self.name} 已清理")
        
    def show_info_dialog(self):
        """显示信息对话框"""
        if not self.main_window.current_pdf:
            QMessageBox.warning(self.main_window, "警告", "请先打开PDF文件")
            return
            
        self.info_dialog.update_info()
        self.info_dialog.show()
        self.info_dialog.raise_()
        self.info_dialog.activateWindow()
