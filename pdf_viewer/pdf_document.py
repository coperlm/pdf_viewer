import fitz  # PyMuPDF
from PIL import Image
import io
from .render_config import RenderConfig


class PDFDocument:
    """PDF文档处理类"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.doc = fitz.open(file_path)
        self.render_config = RenderConfig()
        
        # 设置PyMuPDF的全局渲染选项
        if hasattr(fitz, 'set_aa_level'):
            fitz.set_aa_level(8)  # 设置抗锯齿级别
        
    def get_page_count(self):
        """获取页面总数"""
        return len(self.doc)
        
    def get_page_image(self, page_num, zoom_level=1.0):
        """获取指定页面的图像"""
        page = self.doc[page_num]
        
        # 计算渲染参数
        dpi = self.render_config.get_render_dpi(zoom_level)
        use_hq = self.render_config.should_use_high_quality(zoom_level)
        
        # 计算缩放矩阵 - 使用DPI计算更精确的缩放
        scale_factor = dpi / 72.0  # PDF默认是72 DPI
        mat = fitz.Matrix(scale_factor, scale_factor)
        
        # 使用高质量渲染参数
        pix = page.get_pixmap(
            matrix=mat,
            alpha=False,        # 不使用alpha通道以提高性能
            annots=True,        # 包含注释
            clip=None,          # 不裁剪
            colorspace=fitz.csRGB  # 明确指定RGB色彩空间
        )
        
        # 如果需要高质量，进行额外处理
        if use_hq:
            # 设置更好的渲染标志
            pix.set_origin(0, 0)
        
        # 转换为PIL图像
        img_data = pix.tobytes("ppm")
        pil_image = Image.open(io.BytesIO(img_data))
        
        # 确保图像质量和格式
        if pil_image.mode != 'RGB':
            pil_image = pil_image.convert('RGB')
            
        # 如果缩放级别不是预期的，进行高质量重采样
        if zoom_level != scale_factor:
            target_size = (
                int(pil_image.width * zoom_level / scale_factor),
                int(pil_image.height * zoom_level / scale_factor)
            )
            if target_size != pil_image.size:
                # 使用LANCZOS重采样以获得最佳质量
                pil_image = pil_image.resize(target_size, Image.Resampling.LANCZOS)
        
        return pil_image
        
    def get_page_size(self, page_num):
        """获取页面尺寸"""
        page = self.doc[page_num]
        rect = page.rect
        return (rect.width, rect.height)
        
    def get_outline(self):
        """获取PDF目录"""
        outline = self.doc.get_toc()
        return self._build_outline_tree(outline)
        
    def _build_outline_tree(self, toc):
        """构建目录树结构"""
        if not toc:
            return []
            
        result = []
        stack = []
        
        for level, title, page in toc:
            item = {
                'title': title,
                'page': page - 1,  # 转换为0基索引
                'level': level,
                'children': []
            }
            
            # 找到正确的父级
            while stack and stack[-1]['level'] >= level:
                stack.pop()
                
            if stack:
                stack[-1]['children'].append(item)
            else:
                result.append(item)
                
            stack.append(item)
            
        return result
        
    def search_text(self, query, page_num=None):
        """搜索文本"""
        results = []
        
        if page_num is not None:
            # 搜索指定页面
            page = self.doc[page_num]
            text_instances = page.search_for(query)
            for inst in text_instances:
                results.append({
                    'page': page_num,
                    'bbox': inst,
                    'text': query
                })
        else:
            # 搜索整个文档
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                text_instances = page.search_for(query)
                for inst in text_instances:
                    results.append({
                        'page': page_num,
                        'bbox': inst,
                        'text': query
                    })
                    
        return results
        
    def get_page_text(self, page_num):
        """获取页面文本"""
        page = self.doc[page_num]
        return page.get_text()
        
    def get_metadata(self):
        """获取文档元数据"""
        return self.doc.metadata
        
    def close(self):
        """关闭文档"""
        if self.doc:
            self.doc.close()
            
    def __del__(self):
        """析构函数"""
        self.close()
