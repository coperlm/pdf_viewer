import sys
import os
from PyQt5.QtWidgets import QApplication
from pdf_viewer.main_window import PDFViewerMainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PDF阅读器")
    app.setApplicationVersion("1.0.0")
    
    # 设置应用程序图标和样式
    app.setStyle('Fusion')
    
    # 创建主窗口
    main_window = PDFViewerMainWindow()
    main_window.show()
    
    # 如果命令行提供了PDF文件路径，自动打开
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        main_window.open_pdf(sys.argv[1])
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
