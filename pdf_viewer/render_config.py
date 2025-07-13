"""
PDF渲染配置和优化
"""

class RenderConfig:
    """PDF渲染配置类"""
    
    def __init__(self):
        # 基本渲染设置
        self.use_antialiasing = True
        self.use_text_antialiasing = True
        self.use_high_quality = True
        
        # DPI设置
        self.default_dpi = 150  # 默认DPI，影响渲染质量
        self.max_dpi = 300      # 最大DPI限制
        
        # 缩放相关
        self.scale_smooth = True  # 平滑缩放
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # 性能设置
        self.cache_pages = True      # 缓存页面图像
        self.max_cache_size = 50     # 最大缓存页面数
        self.lazy_loading = False    # 延迟加载（大文档）
        
        # 显示设置
        self.page_shadow = True      # 页面阴影
        self.page_border = True      # 页面边框
        self.background_color = "white"
        
    def get_render_dpi(self, zoom_level):
        """根据缩放级别计算渲染DPI"""
        dpi = self.default_dpi * zoom_level
        return min(dpi, self.max_dpi)
        
    def should_use_high_quality(self, zoom_level):
        """判断是否使用高质量渲染"""
        return self.use_high_quality and zoom_level >= 1.0
