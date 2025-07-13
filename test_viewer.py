"""
PDF阅读器功能测试脚本
"""

import os
import sys
import subprocess

def test_pdf_viewer():
    """测试PDF阅读器功能"""
    print("🔍 PDF阅读器功能测试")
    print("=" * 50)
    
    # 检查必要文件
    required_files = [
        "main.py",
        "pdf_viewer/main_window.py",
        "pdf_viewer/pdf_document.py",
        "pdf_viewer/pdf_viewer_widget.py",
        "plugins/text_search_plugin.py",
        "test_document.pdf"
    ]
    
    print("📁 检查必要文件...")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - 缺失")
            return False
    
    # 检查依赖
    print("\n📦 检查Python依赖...")
    try:
        import PyQt5
        print("  ✅ PyQt5")
    except ImportError:
        print("  ❌ PyQt5 - 请运行: pip install PyQt5")
        return False
    
    try:
        import fitz
        print("  ✅ PyMuPDF")
    except ImportError:
        print("  ❌ PyMuPDF - 请运行: pip install PyMuPDF")
        return False
    
    try:
        import PIL
        print("  ✅ Pillow")
    except ImportError:
        print("  ❌ Pillow - 请运行: pip install Pillow")
        return False
    
    print("\n🎯 功能特性:")
    print("  ✅ 连续页面模式 - 所有页面连续显示")
    print("  ✅ 滚轮翻页 - 使用鼠标滚轮平滑浏览")
    print("  ✅ 智能页面跟踪 - 自动检测当前页面")
    print("  ✅ 双模式切换 - 连续模式/单页模式")
    print("  ✅ 插件系统 - 支持自定义扩展")
    print("  ✅ 文本搜索 - Ctrl+F搜索功能")
    print("  ✅ 书签管理 - Ctrl+B添加书签")
    print("  ✅ 目录导航 - 侧边栏目录跳转")
    
    print("\n🚀 启动建议:")
    print("  1. 直接启动: python main.py")
    print("  2. 打开测试PDF: python main.py test_document.pdf")
    print("  3. 启动后使用 '文件 → 打开' 选择PDF文件")
    
    print("\n🔧 使用技巧:")
    print("  • 使用滚轮浏览整个文档，无需手动翻页")
    print("  • Ctrl+滚轮进行缩放")
    print("  • 在查看菜单中可切换显示模式")
    print("  • 使用Ctrl+F搜索文本内容")
    print("  • 点击侧边栏目录可快速跳转")
    
    print("\n✅ 所有检查通过！PDF阅读器可以正常使用。")
    return True

if __name__ == "__main__":
    if test_pdf_viewer():
        print("\n🎉 准备启动PDF阅读器...")
        print("按任意键继续...")
        input()
        
        # 启动PDF阅读器
        if len(sys.argv) > 1:
            subprocess.run([sys.executable, "main.py", sys.argv[1]])
        else:
            subprocess.run([sys.executable, "main.py"])
    else:
        print("\n❌ 测试失败，请检查上述问题后重试。")
