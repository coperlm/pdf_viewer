import sys
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QScrollArea, QLabel, QToolBar, QMenuBar, QMenu, QAction,
    QFileDialog, QStatusBar, QSpinBox, QComboBox, QPushButton,
    QSlider, QMessageBox, QProgressBar, QTextEdit, QTabWidget,
    QTreeWidget, QTreeWidgetItem, QApplication
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSize, QTimer
from PyQt5.QtGui import QPixmap, QIcon, QFont, QKeySequence
import fitz  # PyMuPDF
from PIL import Image
import io

from .pdf_document import PDFDocument
from .pdf_viewer_widget import PDFViewerWidget
from .bookmark_manager import BookmarkManager
from .plugin_manager import PluginManager


class PDFViewerMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_pdf = None
        self.zoom_level = 1.0
        self.current_page = 1
        self.total_pages = 0
        
        # 初始化组件
        self.bookmark_manager = BookmarkManager()
        self.plugin_manager = PluginManager()
        
        self.init_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_shortcuts()
        self.setup_status_bar()
        
        # 加载插件
        self.plugin_manager.set_main_window(self)
        self.plugin_manager.load_plugins()
        
    def init_ui(self):
        """初始化用户界面"""
        self.setWindowTitle("PDF阅读器 - 未打开文件")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建侧边栏（书签和目录）
        self.create_sidebar(splitter)
        
        # 创建PDF查看器
        self.pdf_viewer = PDFViewerWidget()
        self.pdf_viewer.zoom_in_signal.connect(self.zoom_in)
        self.pdf_viewer.zoom_out_signal.connect(self.zoom_out)
        self.pdf_viewer.currentPageChanged.connect(self.on_page_changed)
        splitter.addWidget(self.pdf_viewer)
        
        # 设置分割器比例
        splitter.setStretchFactor(0, 1)  # 侧边栏
        splitter.setStretchFactor(1, 4)  # PDF查看器
        
    def create_sidebar(self, parent):
        """创建侧边栏"""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        
        # 创建选项卡组件
        tab_widget = QTabWidget()
        
        # 目录选项卡
        outline_widget = QTreeWidget()
        outline_widget.setHeaderLabel("目录")
        tab_widget.addTab(outline_widget, "目录")
        self.outline_widget = outline_widget
        
        # 书签选项卡
        bookmark_widget = QTreeWidget()
        bookmark_widget.setHeaderLabel("书签")
        tab_widget.addTab(bookmark_widget, "书签")
        self.bookmark_widget = bookmark_widget
        
        # 缩略图选项卡
        thumbnail_widget = QScrollArea()
        tab_widget.addTab(thumbnail_widget, "缩略图")
        self.thumbnail_widget = thumbnail_widget
        
        sidebar_layout.addWidget(tab_widget)
        parent.addWidget(sidebar_widget)
        
        # 连接信号
        outline_widget.itemClicked.connect(self.on_outline_clicked)
        bookmark_widget.itemClicked.connect(self.on_bookmark_clicked)
        
    def setup_menus(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        recent_menu = file_menu.addMenu("最近文件")
        self.recent_menu = recent_menu
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 查看菜单
        view_menu = menubar.addMenu("查看")
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        fit_width_action = QAction("适合宽度", self)
        fit_width_action.triggered.connect(self.fit_width)
        view_menu.addAction(fit_width_action)
        
        fit_page_action = QAction("适合页面", self)
        fit_page_action.triggered.connect(self.fit_page)
        view_menu.addAction(fit_page_action)
        
        view_menu.addSeparator()
        
        # 连续页面模式切换
        self.continuous_mode_action = QAction("连续页面模式", self)
        self.continuous_mode_action.setCheckable(True)
        self.continuous_mode_action.setChecked(True)  # 默认开启
        self.continuous_mode_action.triggered.connect(self.toggle_continuous_mode)
        view_menu.addAction(self.continuous_mode_action)
        
        view_menu.addSeparator()
        
        fullscreen_action = QAction("全屏", self)
        fullscreen_action.setShortcut(QKeySequence.FullScreen)
        fullscreen_action.triggered.connect(self.toggle_fullscreen)
        view_menu.addAction(fullscreen_action)
        
        # 工具菜单
        tools_menu = menubar.addMenu("工具")
        
        bookmark_action = QAction("添加书签", self)
        bookmark_action.setShortcut("Ctrl+B")
        bookmark_action.triggered.connect(self.add_bookmark)
        tools_menu.addAction(bookmark_action)
        
        # 插件菜单
        plugins_menu = menubar.addMenu("插件")
        self.plugins_menu = plugins_menu
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 打开文件按钮
        open_action = QAction("打开", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)
        
        toolbar.addSeparator()
        
        # 导航按钮
        prev_action = QAction("上一页", self)
        prev_action.triggered.connect(self.prev_page)
        toolbar.addAction(prev_action)
        
        # 页码输入
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.valueChanged.connect(self.goto_page)
        toolbar.addWidget(self.page_spinbox)
        
        self.page_label = QLabel("/ 0")
        toolbar.addWidget(self.page_label)
        
        next_action = QAction("下一页", self)
        next_action.triggered.connect(self.next_page)
        toolbar.addAction(next_action)
        
        toolbar.addSeparator()
        
        # 缩放控制
        zoom_out_action = QAction("缩小", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)
        
        self.zoom_combo = QComboBox()
        self.zoom_combo.setEditable(True)
        zoom_levels = ["25%", "50%", "75%", "100%", "125%", "150%", "200%", "300%", "400%"]
        self.zoom_combo.addItems(zoom_levels)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.set_zoom_level)
        toolbar.addWidget(self.zoom_combo)
        
        zoom_in_action = QAction("放大", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)
        
        toolbar.addSeparator()
        
        # 适应控制
        fit_width_action = QAction("适合宽度", self)
        fit_width_action.triggered.connect(self.fit_width)
        toolbar.addAction(fit_width_action)
        
        fit_page_action = QAction("适合页面", self)
        fit_page_action.triggered.connect(self.fit_page)
        toolbar.addAction(fit_page_action)
        
    def setup_shortcuts(self):
        """设置快捷键"""
        # 页面导航
        next_shortcut = QAction(self)
        next_shortcut.setShortcut(Qt.Key_Right)
        next_shortcut.triggered.connect(self.next_page)
        self.addAction(next_shortcut)
        
        prev_shortcut = QAction(self)
        prev_shortcut.setShortcut(Qt.Key_Left)
        prev_shortcut.triggered.connect(self.prev_page)
        self.addAction(prev_shortcut)
        
        # 空格键下一页
        space_shortcut = QAction(self)
        space_shortcut.setShortcut(Qt.Key_Space)
        space_shortcut.triggered.connect(self.next_page)
        self.addAction(space_shortcut)
        
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        
    def open_file(self):
        """打开文件对话框"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "打开PDF文件", "", "PDF文件 (*.pdf);;所有文件 (*)"
        )
        if file_path:
            self.open_pdf(file_path)
            
    def open_pdf(self, file_path):
        """打开PDF文件"""
        try:
            self.current_pdf = PDFDocument(file_path)
            self.total_pages = self.current_pdf.get_page_count()
            
            # 设置PDF文档到查看器
            self.pdf_viewer.set_pdf_document(self.current_pdf)
            
            # 更新UI
            self.setWindowTitle(f"PDF阅读器 - {os.path.basename(file_path)}")
            self.page_spinbox.setMaximum(self.total_pages)
            self.page_label.setText(f"/ {self.total_pages}")
            
            # 根据模式显示页面
            if self.pdf_viewer.continuous_mode:
                # 连续模式：加载所有页面
                self.pdf_viewer.load_all_pages(self.zoom_level)
                self.current_page = 1
            else:
                # 单页模式：显示第一页
                self.current_page = 1
                self.display_page()
            
            self.page_spinbox.setValue(1)
            
            # 加载目录
            self.load_outline()
            
            # 生成缩略图
            self.generate_thumbnails()
            
            self.status_bar.showMessage(f"已打开: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法打开PDF文件: {str(e)}")
            
    def display_page(self):
        """显示当前页面"""
        if self.current_pdf:
            try:
                if self.pdf_viewer.continuous_mode:
                    # 连续模式：跳转到指定页面
                    self.pdf_viewer.goto_page(self.current_page)
                else:
                    # 单页模式：显示单个页面
                    page_image = self.current_pdf.get_page_image(
                        self.current_page - 1, self.zoom_level
                    )
                    self.pdf_viewer.display_image(page_image)
                
                # 更新状态栏
                self.status_bar.showMessage(
                    f"页面 {self.current_page}/{self.total_pages} - 缩放: {int(self.zoom_level * 100)}%"
                )
                
            except Exception as e:
                QMessageBox.warning(self, "警告", f"无法显示页面: {str(e)}")
                
    def on_page_changed(self, page_num):
        """页面改变事件处理"""
        self.current_page = page_num
        self.page_spinbox.setValue(page_num)
        # 更新状态栏
        self.status_bar.showMessage(
            f"页面 {self.current_page}/{self.total_pages} - 缩放: {int(self.zoom_level * 100)}%"
        )
                
    def next_page(self):
        """下一页"""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.page_spinbox.setValue(self.current_page)
            if not self.pdf_viewer.continuous_mode:
                self.display_page()
            else:
                self.pdf_viewer.goto_page(self.current_page)
            
    def prev_page(self):
        """上一页"""
        if self.current_page > 1:
            self.current_page -= 1
            self.page_spinbox.setValue(self.current_page)
            if not self.pdf_viewer.continuous_mode:
                self.display_page()
            else:
                self.pdf_viewer.goto_page(self.current_page)
            
    def goto_page(self, page_num):
        """跳转到指定页面"""
        if 1 <= page_num <= self.total_pages:
            self.current_page = page_num
            if self.pdf_viewer.continuous_mode:
                self.pdf_viewer.goto_page(page_num)
            else:
                self.display_page()
            
    def zoom_in(self):
        """放大"""
        self.zoom_level = min(self.zoom_level * 1.25, 5.0)
        self.update_zoom_combo()
        if self.pdf_viewer.continuous_mode:
            self.pdf_viewer.zoom_to_level(self.zoom_level)
        else:
            self.display_page()
        
    def zoom_out(self):
        """缩小"""
        self.zoom_level = max(self.zoom_level / 1.25, 0.1)
        self.update_zoom_combo()
        if self.pdf_viewer.continuous_mode:
            self.pdf_viewer.zoom_to_level(self.zoom_level)
        else:
            self.display_page()
        
    def set_zoom_level(self, text):
        """设置缩放级别"""
        try:
            if text.endswith('%'):
                zoom = float(text[:-1]) / 100
            else:
                zoom = float(text) / 100
            self.zoom_level = max(0.1, min(zoom, 5.0))
            if self.pdf_viewer.continuous_mode:
                self.pdf_viewer.zoom_to_level(self.zoom_level)
            else:
                self.display_page()
        except ValueError:
            pass
            
    def update_zoom_combo(self):
        """更新缩放下拉框"""
        zoom_text = f"{int(self.zoom_level * 100)}%"
        self.zoom_combo.setCurrentText(zoom_text)
        
    def fit_width(self):
        """适合宽度"""
        if self.current_pdf:
            viewer_width = self.pdf_viewer.viewport().width()
            page_width = self.current_pdf.get_page_size(self.current_page - 1)[0]
            self.zoom_level = viewer_width / page_width * 0.95  # 留一点边距
            self.update_zoom_combo()
            if self.pdf_viewer.continuous_mode:
                self.pdf_viewer.zoom_to_level(self.zoom_level)
            else:
                self.display_page()
            
    def fit_page(self):
        """适合页面"""
        if self.current_pdf:
            viewer_size = self.pdf_viewer.viewport().size()
            page_size = self.current_pdf.get_page_size(self.current_page - 1)
            
            width_ratio = viewer_size.width() / page_size[0]
            height_ratio = viewer_size.height() / page_size[1]
            
            self.zoom_level = min(width_ratio, height_ratio) * 0.95
            self.update_zoom_combo()
            if self.pdf_viewer.continuous_mode:
                self.pdf_viewer.zoom_to_level(self.zoom_level)
            else:
                self.display_page()
                
    def toggle_continuous_mode(self):
        """切换连续页面模式"""
        continuous = self.continuous_mode_action.isChecked()
        self.pdf_viewer.set_continuous_mode(continuous)
        
        # 重新加载PDF以应用新模式
        if self.current_pdf:
            if continuous:
                self.pdf_viewer.load_all_pages(self.zoom_level)
                self.pdf_viewer.goto_page(self.current_page)
            else:
                self.pdf_viewer.clear_pages()
                self.display_page()
            
    def toggle_fullscreen(self):
        """切换全屏"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
            
    def load_outline(self):
        """加载PDF目录"""
        if self.current_pdf:
            self.outline_widget.clear()
            outline = self.current_pdf.get_outline()
            self.populate_outline(outline, self.outline_widget)
            
    def populate_outline(self, outline, parent):
        """填充目录树"""
        for item in outline:
            tree_item = QTreeWidgetItem(parent)
            tree_item.setText(0, item['title'])
            tree_item.setData(0, Qt.UserRole, item['page'])
            
            if 'children' in item:
                self.populate_outline(item['children'], tree_item)
                
    def on_outline_clicked(self, item):
        """目录项点击事件"""
        page = item.data(0, Qt.UserRole)
        if page is not None:
            self.current_page = page + 1  # PDF页面从0开始，显示从1开始
            self.page_spinbox.setValue(self.current_page)
            if self.pdf_viewer.continuous_mode:
                self.pdf_viewer.goto_page(self.current_page)
            else:
                self.display_page()
            
    def add_bookmark(self):
        """添加书签"""
        if self.current_pdf:
            title = f"页面 {self.current_page}"
            self.bookmark_manager.add_bookmark(title, self.current_page)
            self.refresh_bookmarks()
            
    def refresh_bookmarks(self):
        """刷新书签列表"""
        self.bookmark_widget.clear()
        for bookmark in self.bookmark_manager.get_bookmarks():
            item = QTreeWidgetItem(self.bookmark_widget)
            item.setText(0, bookmark['title'])
            item.setData(0, Qt.UserRole, bookmark['page'])
            
    def on_bookmark_clicked(self, item):
        """书签点击事件"""
        page = item.data(0, Qt.UserRole)
        if page is not None:
            self.current_page = page
            self.page_spinbox.setValue(self.current_page)
            if self.pdf_viewer.continuous_mode:
                self.pdf_viewer.goto_page(self.current_page)
            else:
                self.display_page()
            
    def generate_thumbnails(self):
        """生成缩略图"""
        # 这里可以实现缩略图生成逻辑
        pass
        
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于",
            "PDF阅读器 v1.0.0\n\n"
            "一个开源的PDF阅读器，支持插件扩展。\n"
            "基于PyQt5和PyMuPDF构建。"
        )
