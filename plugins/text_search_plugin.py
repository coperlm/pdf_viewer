"""
文本搜索插件示例
提供在PDF中搜索文本的功能
"""

import sys
import os

# 添加父目录到路径以便导入插件接口
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_viewer.plugin_manager import PluginInterface
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QListWidget, QListWidgetItem, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal


class SearchThread(QThread):
    """搜索线程"""
    result_found = pyqtSignal(dict)
    search_finished = pyqtSignal()
    
    def __init__(self, pdf_document, query):
        super().__init__()
        self.pdf_document = pdf_document
        self.query = query
        
    def run(self):
        """执行搜索"""
        try:
            results = self.pdf_document.search_text(self.query)
            for result in results:
                self.result_found.emit(result)
            self.search_finished.emit()
        except Exception as e:
            print(f"搜索错误: {e}")
            self.search_finished.emit()


class SearchDialog(QDialog):
    """搜索对话框"""
    
    goto_page = pyqtSignal(int)  # 跳转页面信号
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.search_thread = None
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("文本搜索")
        self.setModal(False)
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # 搜索输入
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入要搜索的文本...")
        self.search_input.returnPressed.connect(self.start_search)
        
        self.search_button = QPushButton("搜索")
        self.search_button.clicked.connect(self.start_search)
        
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)
        
        # 结果列表
        self.results_label = QLabel("搜索结果:")
        layout.addWidget(self.results_label)
        
        self.results_list = QListWidget()
        self.results_list.itemDoubleClicked.connect(self.on_result_clicked)
        layout.addWidget(self.results_list)
        
    def start_search(self):
        """开始搜索"""
        query = self.search_input.text().strip()
        if not query:
            return
            
        if not self.main_window.current_pdf:
            QMessageBox.warning(self, "警告", "请先打开PDF文件")
            return
            
        # 清空之前的结果
        self.results_list.clear()
        self.results_label.setText(f"搜索 \"{query}\" 中...")
        
        # 启动搜索线程
        self.search_thread = SearchThread(self.main_window.current_pdf, query)
        self.search_thread.result_found.connect(self.add_result)
        self.search_thread.search_finished.connect(self.search_completed)
        self.search_thread.start()
        
    def add_result(self, result):
        """添加搜索结果"""
        page_num = result['page'] + 1  # 转换为1基索引
        text = f"页面 {page_num}: {result['text']}"
        
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, page_num)
        self.results_list.addItem(item)
        
    def search_completed(self):
        """搜索完成"""
        count = self.results_list.count()
        query = self.search_input.text().strip()
        self.results_label.setText(f"搜索 \"{query}\" 完成，找到 {count} 个结果:")
        
    def on_result_clicked(self, item):
        """结果项被点击"""
        page_num = item.data(Qt.UserRole)
        if page_num:
            self.goto_page.emit(page_num)


class TextSearchPlugin(PluginInterface):
    """文本搜索插件"""
    
    @property
    def name(self):
        return "文本搜索"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "在PDF文档中搜索文本内容"
    
    def initialize(self, main_window):
        """初始化插件"""
        self.main_window = main_window
        
        # 创建搜索对话框
        self.search_dialog = SearchDialog(main_window)
        self.search_dialog.goto_page.connect(self.goto_page)
        
        # 添加菜单项
        search_action = main_window.plugins_menu.addAction("文本搜索")
        search_action.setShortcut("Ctrl+F")
        search_action.triggered.connect(self.show_search_dialog)
        
        print(f"插件 {self.name} 初始化完成")
        
    def finalize(self):
        """清理插件资源"""
        if hasattr(self, 'search_dialog'):
            self.search_dialog.close()
        print(f"插件 {self.name} 已清理")
        
    def show_search_dialog(self):
        """显示搜索对话框"""
        if not self.main_window.current_pdf:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self.main_window, "警告", "请先打开PDF文件")
            return
            
        self.search_dialog.show()
        self.search_dialog.raise_()
        self.search_dialog.activateWindow()
        
    def goto_page(self, page_num):
        """跳转到指定页面"""
        self.main_window.current_page = page_num
        self.main_window.page_spinbox.setValue(page_num)
        self.main_window.display_page()
