"""
创建测试PDF文件
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os


def create_test_pdf():
    """创建测试PDF文件"""
    filename = "test_document.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4,
                          rightMargin=72, leftMargin=72,
                          topMargin=72, bottomMargin=18)
    
    # 获取样式
    styles = getSampleStyleSheet()
    story = []
    
    # 标题页
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    story.append(Paragraph("PDF阅读器测试文档", title_style))
    story.append(Spacer(1, 20))
    story.append(Paragraph("这是一个用于测试PDF阅读器功能的示例文档", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # 目录
    story.append(Paragraph("目录", styles['Heading2']))
    toc_data = [
        ["章节", "页码"],
        ["第一章：基本功能测试", "2"],
        ["第二章：文本搜索测试", "3"],
        ["第三章：书签功能测试", "4"],
        ["第四章：插件系统测试", "5"],
    ]
    
    toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
    toc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(toc_table)
    story.append(PageBreak())
    
    # 第一章
    story.append(Paragraph("第一章：基本功能测试", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    content1 = """
    本章节用于测试PDF阅读器的基本功能，包括：
    
    1. 文件打开和显示
    2. 页面导航（上一页、下一页、跳转）
    3. 缩放功能（放大、缩小、适合宽度、适合页面）
    4. 全屏模式
    5. 滚动和浏览
    
    这些是PDF阅读器最基础的功能，用户可以通过工具栏按钮、菜单项或快捷键来使用这些功能。
    """
    
    story.append(Paragraph(content1, styles['Normal']))
    story.append(PageBreak())
    
    # 第二章
    story.append(Paragraph("第二章：文本搜索测试", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    content2 = """
    本章节包含用于测试文本搜索功能的关键词：
    
    测试关键词：PDF、阅读器、搜索、功能、插件、Python、PyQt5、开源
    
    文本搜索是PDF阅读器的重要功能之一。用户可以通过Ctrl+F快捷键或插件菜单来打开搜索对话框。
    搜索功能应该能够找到文档中的所有匹配文本，并显示在结果列表中。点击搜索结果可以跳转到对应页面。
    
    这段文本包含了多个测试用的关键词，可以用来验证搜索功能是否正常工作。
    搜索时应该忽略大小写，并且能够找到部分匹配的结果。
    """
    
    story.append(Paragraph(content2, styles['Normal']))
    story.append(PageBreak())
    
    # 第三章
    story.append(Paragraph("第三章：书签功能测试", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    content3 = """
    书签功能允许用户在PDF文档中标记重要的页面，以便快速访问。
    
    书签功能特性：
    • 添加书签：用户可以通过Ctrl+B或工具菜单添加当前页面的书签
    • 书签列表：侧边栏显示所有已添加的书签
    • 快速跳转：点击书签可以快速跳转到对应页面
    • 书签管理：可以重命名或删除书签
    
    建议在此页面添加一个书签来测试该功能！
    """
    
    story.append(Paragraph(content3, styles['Normal']))
    story.append(PageBreak())
    
    # 第四章
    story.append(Paragraph("第四章：插件系统测试", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    content4 = """
    PDF阅读器采用了模块化的插件架构，支持动态加载和扩展功能。
    
    已实现的插件：
    1. 文本搜索插件 - 在文档中搜索文本内容
    2. PDF信息查看插件 - 显示文档的详细信息和元数据
    3. 插件模板 - 用于开发新插件的模板
    
    插件开发指南：
    • 继承PluginInterface基类
    • 实现必要的属性和方法
    • 将插件文件放在plugins目录中
    • 程序启动时会自动加载所有插件
    
    插件系统使得PDF阅读器具有很强的扩展性，开发者可以根据需求添加新功能。
    """
    
    story.append(Paragraph(content4, styles['Normal']))
    story.append(PageBreak())
    
    # 最后一页
    story.append(Paragraph("结语", styles['Heading1']))
    story.append(Spacer(1, 12))
    
    content5 = """
    这个PDF阅读器项目展示了如何使用Python和PyQt5构建一个功能完整的桌面应用程序。
    
    主要特点：
    • 现代化的用户界面
    • 完善的PDF查看功能
    • 灵活的插件系统
    • 开源免费
    
    希望这个项目能够为您的学习和开发提供帮助！
    
    感谢使用PDF阅读器！
    """
    
    story.append(Paragraph(content5, styles['Normal']))
    
    # 构建PDF
    doc.build(story)
    print(f"测试PDF文件已创建: {filename}")


if __name__ == "__main__":
    create_test_pdf()
