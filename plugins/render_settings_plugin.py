"""
渲染质量设置插件
允许用户调整PDF渲染质量和性能参数
"""

import sys
import os

# 添加父目录到路径以便导入插件接口
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pdf_viewer.plugin_manager import PluginInterface
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QPushButton, QCheckBox, QSpinBox, QGroupBox, QFormLayout,
    QComboBox, QMessageBox, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt


class RenderSettingsDialog(QDialog):
    """渲染设置对话框"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.main_window = main_window
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("渲染质量设置")
        self.setModal(True)
        self.resize(400, 500)
        
        layout = QVBoxLayout(self)
        
        # 创建选项卡
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # 质量设置选项卡
        quality_tab = self.create_quality_tab()
        tab_widget.addTab(quality_tab, "渲染质量")
        
        # 性能设置选项卡
        performance_tab = self.create_performance_tab()
        tab_widget.addTab(performance_tab, "性能优化")
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        self.apply_button = QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_settings)
        
        self.reset_button = QPushButton("重置默认")
        self.reset_button.clicked.connect(self.reset_settings)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 加载当前设置
        self.load_current_settings()
        
    def create_quality_tab(self):
        """创建质量设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # DPI设置组
        dpi_group = QGroupBox("DPI设置")
        dpi_layout = QFormLayout(dpi_group)
        
        self.default_dpi_spin = QSpinBox()
        self.default_dpi_spin.setRange(72, 600)
        self.default_dpi_spin.setValue(150)
        self.default_dpi_spin.setSuffix(" DPI")
        dpi_layout.addRow("默认DPI:", self.default_dpi_spin)
        
        self.max_dpi_spin = QSpinBox()
        self.max_dpi_spin.setRange(150, 1200)
        self.max_dpi_spin.setValue(300)
        self.max_dpi_spin.setSuffix(" DPI")
        dpi_layout.addRow("最大DPI:", self.max_dpi_spin)
        
        layout.addWidget(dpi_group)
        
        # 抗锯齿设置组
        aa_group = QGroupBox("抗锯齿设置")
        aa_layout = QVBoxLayout(aa_group)
        
        self.use_antialiasing_cb = QCheckBox("启用图形抗锯齿")
        self.use_antialiasing_cb.setChecked(True)
        aa_layout.addWidget(self.use_antialiasing_cb)
        
        self.use_text_antialiasing_cb = QCheckBox("启用文本抗锯齿")
        self.use_text_antialiasing_cb.setChecked(True)
        aa_layout.addWidget(self.use_text_antialiasing_cb)
        
        self.use_high_quality_cb = QCheckBox("高质量渲染模式")
        self.use_high_quality_cb.setChecked(True)
        aa_layout.addWidget(self.use_high_quality_cb)
        
        layout.addWidget(aa_group)
        
        # 缩放设置组
        zoom_group = QGroupBox("缩放设置")
        zoom_layout = QFormLayout(zoom_group)
        
        self.scale_smooth_cb = QCheckBox("平滑缩放")
        self.scale_smooth_cb.setChecked(True)
        zoom_layout.addRow("缩放选项:", self.scale_smooth_cb)
        
        layout.addWidget(zoom_group)
        
        layout.addStretch()
        return widget
        
    def create_performance_tab(self):
        """创建性能设置选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 缓存设置组
        cache_group = QGroupBox("缓存设置")
        cache_layout = QFormLayout(cache_group)
        
        self.cache_pages_cb = QCheckBox("启用页面缓存")
        self.cache_pages_cb.setChecked(True)
        cache_layout.addRow("缓存选项:", self.cache_pages_cb)
        
        self.max_cache_spin = QSpinBox()
        self.max_cache_spin.setRange(10, 200)
        self.max_cache_spin.setValue(50)
        self.max_cache_spin.setSuffix(" 页")
        cache_layout.addRow("最大缓存:", self.max_cache_spin)
        
        layout.addWidget(cache_group)
        
        # 加载设置组
        loading_group = QGroupBox("加载设置")
        loading_layout = QVBoxLayout(loading_group)
        
        self.lazy_loading_cb = QCheckBox("延迟加载（大文档优化）")
        self.lazy_loading_cb.setChecked(False)
        loading_layout.addWidget(self.lazy_loading_cb)
        
        layout.addWidget(loading_group)
        
        # 显示设置组
        display_group = QGroupBox("显示设置")
        display_layout = QVBoxLayout(display_group)
        
        self.page_shadow_cb = QCheckBox("页面阴影效果")
        self.page_shadow_cb.setChecked(True)
        display_layout.addWidget(self.page_shadow_cb)
        
        self.page_border_cb = QCheckBox("页面边框")
        self.page_border_cb.setChecked(True)
        display_layout.addWidget(self.page_border_cb)
        
        layout.addWidget(display_group)
        
        layout.addStretch()
        return widget
        
    def load_current_settings(self):
        """加载当前设置"""
        if hasattr(self.main_window, 'current_pdf') and self.main_window.current_pdf:
            config = self.main_window.current_pdf.render_config
            
            # 加载DPI设置
            self.default_dpi_spin.setValue(config.default_dpi)
            self.max_dpi_spin.setValue(config.max_dpi)
            
            # 加载抗锯齿设置
            self.use_antialiasing_cb.setChecked(config.use_antialiasing)
            self.use_text_antialiasing_cb.setChecked(config.use_text_antialiasing)
            self.use_high_quality_cb.setChecked(config.use_high_quality)
            
            # 加载其他设置
            self.scale_smooth_cb.setChecked(config.scale_smooth)
            self.cache_pages_cb.setChecked(config.cache_pages)
            self.max_cache_spin.setValue(config.max_cache_size)
            self.lazy_loading_cb.setChecked(config.lazy_loading)
            self.page_shadow_cb.setChecked(config.page_shadow)
            self.page_border_cb.setChecked(config.page_border)
            
    def apply_settings(self):
        """应用设置"""
        if hasattr(self.main_window, 'current_pdf') and self.main_window.current_pdf:
            config = self.main_window.current_pdf.render_config
            
            # 应用DPI设置
            config.default_dpi = self.default_dpi_spin.value()
            config.max_dpi = self.max_dpi_spin.value()
            
            # 应用抗锯齿设置
            config.use_antialiasing = self.use_antialiasing_cb.isChecked()
            config.use_text_antialiasing = self.use_text_antialiasing_cb.isChecked()
            config.use_high_quality = self.use_high_quality_cb.isChecked()
            
            # 应用其他设置
            config.scale_smooth = self.scale_smooth_cb.isChecked()
            config.cache_pages = self.cache_pages_cb.isChecked()
            config.max_cache_size = self.max_cache_spin.value()
            config.lazy_loading = self.lazy_loading_cb.isChecked()
            config.page_shadow = self.page_shadow_cb.isChecked()
            config.page_border = self.page_border_cb.isChecked()
            
            # 重新渲染当前页面
            self.main_window.display_page()
            
            QMessageBox.information(self, "成功", "渲染设置已应用，页面将重新渲染。")
        else:
            QMessageBox.warning(self, "警告", "请先打开PDF文件再调整设置。")
            
    def reset_settings(self):
        """重置为默认设置"""
        self.default_dpi_spin.setValue(150)
        self.max_dpi_spin.setValue(300)
        self.use_antialiasing_cb.setChecked(True)
        self.use_text_antialiasing_cb.setChecked(True)
        self.use_high_quality_cb.setChecked(True)
        self.scale_smooth_cb.setChecked(True)
        self.cache_pages_cb.setChecked(True)
        self.max_cache_spin.setValue(50)
        self.lazy_loading_cb.setChecked(False)
        self.page_shadow_cb.setChecked(True)
        self.page_border_cb.setChecked(True)


class RenderSettingsPlugin(PluginInterface):
    """渲染设置插件"""
    
    @property
    def name(self):
        return "渲染质量设置"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "调整PDF渲染质量和性能参数"
    
    def initialize(self, main_window):
        """初始化插件"""
        self.main_window = main_window
        
        # 创建设置对话框
        self.settings_dialog = RenderSettingsDialog(main_window)
        
        # 添加菜单项
        settings_action = main_window.plugins_menu.addAction("渲染设置")
        settings_action.triggered.connect(self.show_settings_dialog)
        
        print(f"插件 {self.name} 初始化完成")
        
    def finalize(self):
        """清理插件资源"""
        if hasattr(self, 'settings_dialog'):
            self.settings_dialog.close()
        print(f"插件 {self.name} 已清理")
        
    def show_settings_dialog(self):
        """显示设置对话框"""
        self.settings_dialog.show()
        self.settings_dialog.raise_()
        self.settings_dialog.activateWindow()
