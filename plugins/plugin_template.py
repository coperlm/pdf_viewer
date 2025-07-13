"""
插件开发模板
使用此模板创建新插件
"""

import sys
import os

# 添加父目录到路径以便导入插件接口
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_viewer.plugin_manager import PluginInterface
from PyQt5.QtWidgets import QMessageBox


class MyCustomPlugin(PluginInterface):
    """自定义插件模板"""
    
    @property
    def name(self):
        """插件名称"""
        return "我的插件"
    
    @property
    def version(self):
        """插件版本"""
        return "1.0.0"
    
    @property
    def description(self):
        """插件描述"""
        return "这是一个插件模板"
    
    def initialize(self, main_window):
        """初始化插件"""
        self.main_window = main_window
        
        # 在这里添加初始化代码
        # 例如：添加菜单项、工具栏按钮、快捷键等
        
        # 示例：添加菜单项
        my_action = main_window.plugins_menu.addAction("我的功能")
        my_action.triggered.connect(self.my_function)
        
        print(f"插件 {self.name} 初始化完成")
        
    def finalize(self):
        """清理插件资源"""
        # 在这里添加清理代码
        # 例如：关闭对话框、保存设置等
        
        print(f"插件 {self.name} 已清理")
        
    def my_function(self):
        """插件功能实现"""
        # 检查是否有打开的PDF文件
        if not self.main_window.current_pdf:
            QMessageBox.warning(self.main_window, "警告", "请先打开PDF文件")
            return
        
        # 在这里实现具体功能
        QMessageBox.information(
            self.main_window, 
            "信息", 
            f"当前PDF有 {self.main_window.total_pages} 页"
        )


# 可选：如果插件需要多个类，可以在这里定义
class MyCustomDialog:
    """自定义对话框示例"""
    pass


# 可选：如果插件需要工具函数，可以在这里定义
def helper_function():
    """辅助函数示例"""
    pass
