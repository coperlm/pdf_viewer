from PyQt5.QtWidgets import QScrollArea, QLabel, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from PIL import Image
import numpy as np


class PDFViewerWidget(QScrollArea):
    """PDF查看器组件"""
    
    pageClicked = pyqtSignal(int, int)  # 页面点击信号 (x, y)
    currentPageChanged = pyqtSignal(int)  # 当前页面改变信号
    zoom_in_signal = pyqtSignal()  # 放大信号
    zoom_out_signal = pyqtSignal()  # 缩小信号
    
    def __init__(self):
        super().__init__()
        self.current_images = []  # 存储所有页面图像
        self.page_labels = []  # 存储所有页面标签
        self.page_positions = []  # 存储每页的垂直位置
        self.current_page = 1
        self.total_pages = 0
        self.zoom_level = 1.0
        self.pdf_document = None
        self.continuous_mode = True  # 连续页面模式
        self.page_spacing = 10  # 页面间距
        
        # 用于检测当前页面的定时器
        self.page_check_timer = QTimer()
        self.page_check_timer.timeout.connect(self.check_current_page)
        self.page_check_timer.setInterval(100)  # 100ms检查一次
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建容器widget用于放置所有页面
        self.container_widget = QWidget()
        self.container_layout = QVBoxLayout(self.container_widget)
        self.container_layout.setSpacing(self.page_spacing)
        self.container_layout.setContentsMargins(10, 10, 10, 10)
        
        # 设置容器为滚动区域的widget
        self.setWidget(self.container_widget)
        
        # 添加提示标签
        self.placeholder_label = QLabel("请打开PDF文件")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setStyleSheet("color: gray; font-size: 14px;")
        self.container_layout.addWidget(self.placeholder_label)
        
    def set_pdf_document(self, pdf_document):
        """设置PDF文档"""
        self.pdf_document = pdf_document
        self.total_pages = pdf_document.get_page_count() if pdf_document else 0
        
    def load_all_pages(self, zoom_level=1.0):
        """加载所有页面（连续模式）"""
        if not self.pdf_document:
            return
            
        self.zoom_level = zoom_level
        self.clear_pages()
        
        # 隐藏占位符
        self.placeholder_label.hide()
        
        # 为每一页创建标签并加载图像
        self.page_positions = []
        current_y = 10  # 起始位置
        
        for page_num in range(self.total_pages):
            # 获取页面图像
            pil_image = self.pdf_document.get_page_image(page_num, zoom_level)
            
            # 创建页面标签
            page_label = QLabel()
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setStyleSheet("""
                background-color: white; 
                border: 1px solid #ddd;
                margin: 2px;
                padding: 5px;
            """)
            
            # 转换并设置图像
            pixmap = self.pil_to_pixmap(pil_image)
            
            # 确保高质量渲染
            page_label.setPixmap(pixmap)
            page_label.setFixedSize(pixmap.size())
            page_label.setScaledContents(False)  # 禁用自动缩放以保持质量
            
            # 添加到布局
            self.container_layout.addWidget(page_label)
            self.page_labels.append(page_label)
            
            # 记录页面位置
            self.page_positions.append(current_y)
            current_y += pixmap.height() + self.page_spacing
            
        # 开始监控当前页面
        self.page_check_timer.start()
        
    def display_image(self, pil_image):
        """显示单个页面图像（兼容性方法）"""
        if self.continuous_mode:
            # 连续模式下，这个方法用于更新单个页面
            if hasattr(self, 'current_page') and self.current_page <= len(self.page_labels):
                pixmap = self.pil_to_pixmap(pil_image)
                page_index = self.current_page - 1
                if page_index < len(self.page_labels):
                    self.page_labels[page_index].setPixmap(pixmap)
                    self.page_labels[page_index].setFixedSize(pixmap.size())
        else:
            # 单页模式
            self.clear_pages()
            self.placeholder_label.hide()
            
            page_label = QLabel()
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setStyleSheet("background-color: white;")
            
            pixmap = self.pil_to_pixmap(pil_image)
            page_label.setPixmap(pixmap)
            page_label.setFixedSize(pixmap.size())
            
            self.container_layout.addWidget(page_label)
            self.page_labels = [page_label]
            
    def pil_to_pixmap(self, pil_image):
        """将PIL图像转换为QPixmap - 高质量版本"""
        # 确保图像为RGB模式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
        
        # 获取图像信息
        width, height = pil_image.size
        
        # 使用numpy进行更精确的转换（如果可用）
        try:
            import numpy as np
            
            # 转换为numpy数组
            img_array = np.array(pil_image, dtype=np.uint8)
            
            # 确保数据类型和形状正确
            if len(img_array.shape) == 3 and img_array.shape[2] == 3:
                # RGB格式，交换轴以匹配Qt的内存布局
                height, width, channel = img_array.shape
                
                # 确保数据是连续的
                if not img_array.flags['C_CONTIGUOUS']:
                    img_array = np.ascontiguousarray(img_array)
                
                bytes_per_line = 3 * width
                
                # 创建QImage
                from PyQt5.QtGui import QImage
                qt_image = QImage(
                    img_array.data, 
                    width, 
                    height, 
                    bytes_per_line, 
                    QImage.Format_RGB888
                )
                
                # 创建QPixmap并确保质量
                pixmap = QPixmap.fromImage(qt_image)
                
                # 设置设备像素比例确保清晰度
                if hasattr(pixmap, 'setDevicePixelRatio'):
                    pixmap.setDevicePixelRatio(1.0)
                
                return pixmap
                
        except (ImportError, Exception):
            # 如果numpy不可用或出错，使用备用方法
            pass
        
        # 备用方法：直接从PIL转换
        # 获取图像字节数据
        img_data = pil_image.tobytes('raw', 'RGB')
        
        # 计算正确的字节对齐
        bytes_per_line = width * 3
        
        from PyQt5.QtGui import QImage
        qt_image = QImage(img_data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        # 确保QImage有效
        if qt_image.isNull():
            # 如果转换失败，创建一个错误图像
            qt_image = QImage(100, 100, QImage.Format_RGB888)
            qt_image.fill(0xFFFFFF)  # 白色背景
        
        # 转换为QPixmap
        pixmap = QPixmap.fromImage(qt_image)
        
        return pixmap
        
    def clear_pages(self):
        """清空所有页面"""
        # 删除所有页面标签
        for label in self.page_labels:
            label.deleteLater()
        self.page_labels.clear()
        self.page_positions.clear()
        
        # 停止页面检查定时器
        self.page_check_timer.stop()
        
    def check_current_page(self):
        """检查当前显示的页面"""
        if not self.page_positions:
            return
            
        # 获取当前滚动位置
        scroll_y = self.verticalScrollBar().value()
        viewport_height = self.viewport().height()
        center_y = scroll_y + viewport_height // 2
        
        # 找到当前中心位置对应的页面
        current_page = 1
        for i, pos in enumerate(self.page_positions):
            if center_y >= pos:
                current_page = i + 1
            else:
                break
                
        # 如果页面改变了，发出信号
        if current_page != self.current_page:
            self.current_page = current_page
            self.currentPageChanged.emit(current_page)
            
    def goto_page(self, page_num):
        """跳转到指定页面"""
        if 1 <= page_num <= len(self.page_positions):
            self.current_page = page_num
            # 滚动到指定页面
            target_y = self.page_positions[page_num - 1]
            self.verticalScrollBar().setValue(target_y)
            
    def set_continuous_mode(self, continuous):
        """设置连续页面模式"""
        self.continuous_mode = continuous
        
    def zoom_to_level(self, zoom_level):
        """缩放到指定级别"""
        if self.pdf_document and self.continuous_mode:
            self.load_all_pages(zoom_level)
        elif self.pdf_document:
            # 单页模式下重新加载当前页
            page_image = self.pdf_document.get_page_image(self.current_page - 1, zoom_level)
            self.display_image(page_image)
        
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.LeftButton:
            # 获取相对于容器的坐标
            widget_pos = self.widget().mapFromGlobal(event.globalPos())
            self.pageClicked.emit(widget_pos.x(), widget_pos.y())
        super().mousePressEvent(event)
        
    def wheelEvent(self, event):
        """鼠标滚轮事件"""
        if event.modifiers() == Qt.ControlModifier:
            # Ctrl+滚轮缩放
            delta = event.angleDelta().y()
            if delta > 0:
                self.zoom_in_signal.emit()
            else:
                self.zoom_out_signal.emit()
        else:
            # 正常滚动
            super().wheelEvent(event)
            
    def clear(self):
        """清空显示"""
        self.clear_pages()
        self.placeholder_label.show()
        self.placeholder_label.setText("请打开PDF文件")
        
    def get_current_page(self):
        """获取当前页面号"""
        return self.current_page
        
    def get_total_pages(self):
        """获取总页数"""
        return self.total_pages
