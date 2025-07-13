# PDF阅读器

一个开源的PDF阅读器，基于Python、PyQt5和PyMuPDF构建，支持插件扩展。

## 功能特性

### 基本功能
- ✅ 打开和查看PDF文件
- ✅ **连续页面模式** - 所有页面连续显示，支持滚轮翻页
- ✅ **单页模式** - 传统的单页显示模式
- ✅ 页面导航（上一页/下一页/跳转）
- ✅ 缩放控制（放大/缩小/适合宽度/适合页面）
- ✅ 全屏模式
- ✅ 书签管理
- ✅ 目录导航
- ✅ 状态栏显示
- ✅ 快捷键支持

### 插件系统
- ✅ 插件接口定义
- ✅ 动态插件加载
- ✅ 插件管理器
- ✅ 示例插件（文本搜索）

### 已包含插件
- **文本搜索插件**: 在PDF中搜索文本内容
- **PDF信息查看插件**: 查看文档详细信息和元数据  
- **渲染质量设置插件**: 调整PDF渲染质量和性能参数

## 依赖库

- PyQt5 >= 5.15.0
- PyMuPDF >= 1.23.0
- Pillow >= 9.0.0

## 安装和运行

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行程序：
```bash
python main.py
```

3. 或者指定PDF文件：
```bash
python main.py example.pdf
```

## 快捷键

- `Ctrl+O`: 打开文件
- `Ctrl+Q`: 退出程序
- `Ctrl++`: 放大
- `Ctrl+-`: 缩小
- `F11`: 全屏
- `Ctrl+B`: 添加书签
- `Ctrl+F`: 文本搜索（插件）
- `→` / `Space`: 下一页
- `←`: 上一页
- `Ctrl+滚轮`: 缩放
- **滚轮**: 连续模式下平滑翻页

## 🆕 连续页面模式

PDF阅读器默认采用**连续页面模式**，提供更流畅的阅读体验：

### 连续模式特性
- 📄 **所有页面连续显示**: 无需手动翻页，所有内容一次性加载
- 🖱️ **滚轮浏览**: 使用鼠标滚轮平滑浏览整个文档
- 🎯 **智能页面跟踪**: 自动检测当前浏览位置并更新页码
- ⚡ **快速跳转**: 点击目录或书签可快速跳转到指定位置
- 🔄 **模式切换**: 可在菜单中切换回传统单页模式

### 使用方法
1. **打开PDF**: 文档将以连续模式加载所有页面
2. **浏览**: 使用鼠标滚轮或滚动条浏览
3. **缩放**: `Ctrl+滚轮`进行缩放，页面布局自动调整
4. **跳转**: 工具栏页码输入框或目录点击快速跳转
5. **切换模式**: 查看菜单 → "连续页面模式" 可切换显示模式

## 插件开发

### 创建新插件

1. 在 `plugins` 目录下创建Python文件
2. 继承 `PluginInterface` 类
3. 实现必要的方法：
   - `name`: 插件名称
   - `version`: 插件版本
   - `description`: 插件描述
   - `initialize(main_window)`: 初始化插件
   - `finalize()`: 清理资源

### 插件示例

```python
from pdf_viewer.plugin_manager import PluginInterface

class MyPlugin(PluginInterface):
    @property
    def name(self):
        return "我的插件"
    
    @property
    def version(self):
        return "1.0.0"
    
    @property
    def description(self):
        return "这是一个示例插件"
    
    def initialize(self, main_window):
        # 初始化逻辑
        self.main_window = main_window
        # 添加菜单项、工具栏按钮等
        
    def finalize(self):
        # 清理逻辑
        pass
```

## 项目结构

```
PDF/
├── main.py                    # 程序入口
├── requirements.txt           # 依赖列表
├── config.ini                # 配置文件
├── bookmarks.json            # 书签文件（自动生成）
├── pdf_viewer/               # 核心模块
│   ├── __init__.py
│   ├── main_window.py        # 主窗口
│   ├── pdf_document.py       # PDF文档处理
│   ├── pdf_viewer_widget.py  # PDF查看器组件
│   ├── bookmark_manager.py   # 书签管理
│   └── plugin_manager.py     # 插件管理
└── plugins/                  # 插件目录
    └── text_search_plugin.py # 文本搜索插件
```

## 扩展计划

### ✅ 已完成功能
- 连续页面浏览模式
- 智能页面跟踪
- 双显示模式切换
- 插件系统架构
- 文本搜索插件
- PDF信息查看插件

### 即将添加的功能
- 注释和标记功能
- PDF表单填写
- 页面旋转
- 打印支持
- 多标签页支持
- 夜间模式
- PDF转图片
- 页面缩略图优化
- 更多插件示例

### 插件想法
- PDF编辑插件
- OCR文字识别插件
- 翻译插件
- 笔记管理插件
- 文档比较插件
- 密码保护插件

## 许可证

开源许可证（具体许可证待定）

## 贡献

欢迎提交Issue和Pull Request！

## 联系方式

如有问题或建议，请通过Issue联系。
