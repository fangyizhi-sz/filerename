import os
import PyInstaller.__main__

# 获取当前脚本的目录
base_dir = os.path.dirname(os.path.abspath(__file__))

# 定义打包参数
PyInstaller.__main__.run([
    '--name=基于时间码的改名工具',  # 可执行文件的名称
    '--onefile',  # 打包为单个文件
    '--windowed',  # 不显示命令行窗口
    # f'--add-data={os.path.join(base_dir, "ffmpeg")};ffmpeg',  # 添加FFmpeg文件夹
    # f'--add-data={os.path.join(base_dir, "tesseract")};tesseract',  # 添加Tesseract-OCR文件夹
    '--distpath=dist',  # 输出目录
    '--workpath=build',  # 临时构建目录
    '--specpath=build',  # spec文件目录
    os.path.join(base_dir, 'QT.py')  # 主程序入口
])