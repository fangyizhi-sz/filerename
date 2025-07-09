
import sys
import os
import logging
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtCore import pyqtSignal, QObject

class Processor(QObject):
    update_progress = pyqtSignal(int, str)  # 进度百分比，当前文件
    finished = pyqtSignal(dict)  # 传递处理结果

    def __init__(self):
        super().__init__()


class QTextEditLogger(logging.Handler):
    def __init__(self, text_edit):
        super().__init__()
        self.text_edit = text_edit

    def emit(self, record):
        msg = self.format(record)
        self.text_edit.insertPlainText(msg + "\n")        
        self.text_edit.ensureCursorVisible()

class VideoProcessor(QThread):
    finished = pyqtSignal(dict)  # 传递处理结果

    def __init__(self, qtake_folder, input_folder, output_folder, processor):
        super().__init__()
        self.qtake_folder = qtake_folder
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.processor = processor  # 传入Processor对象
        self.running = True

    def run(self):
        try:
            # 延迟导入 copy_mov_file
            from movrename import copy_mov_file
            result = copy_mov_file(self.qtake_folder, self.input_folder, self.output_folder, self.processor)
            self.finished.emit(result)
        except Exception as e:
            self.finished.emit({
                'success_count': 0,
                'failure_count': 0,
                'failure_logs': [f"全局错误: {str(e)}"]
            })

    def stop(self):
        self.running = False
        self.wait()  # 等待线程完全退出

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("基于时间码的改名工具")
        self.setGeometry(100, 100, 800, 600)
        self.init_ui()
        self.processor = None
        self.video_processor = None

    def init_ui(self):
        main_widget = QWidget()
        layout = QVBoxLayout()

        self.input_btn = QPushButton("选择需要改名的文件夹")
        self.input_btn.clicked.connect(self.select_input)
        self.input_label = QLabel(r"")
        layout.addWidget(self.input_btn)
        layout.addWidget(self.input_label)

        # 输入qtake
        self.qtake_btn = QPushButton("选择QTake文件夹")
        self.qtake_btn.clicked.connect(self.select_qtake)
        self.qtake_label = QLabel(r"")
        layout.addWidget(self.qtake_btn)
        layout.addWidget(self.qtake_label)       

        # 输出文件夹选择
        self.output_btn = QPushButton("选择输出文件夹")
        self.output_btn.clicked.connect(self.select_output)
        self.output_label = QLabel(r"")
        layout.addWidget(self.output_btn)
        layout.addWidget(self.output_label)

        # 进度显示
        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        # 日志显示
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # 控制按钮
        self.start_btn = QPushButton("开始处理")
        self.start_btn.clicked.connect(self.start_processing)
        self.stop_btn = QPushButton("停止处理")
        self.stop_btn.clicked.connect(self.stop_processing)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.start_btn)
        btn_layout.addWidget(self.stop_btn)
        layout.addLayout(btn_layout)

        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

        # 设置日志处理器
        self.setup_logging()

    def setup_logging(self):
        log_handler = QTextEditLogger(self.log_area)
        log_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

        logger = logging.getLogger()
        logger.addHandler(log_handler)
        logger.setLevel(logging.INFO)

    def select_qtake(self):
        folder = QFileDialog.getExistingDirectory(self, "选择QTake文件夹")
        if folder:
            self.qtake_folder = folder
            self.qtake_label.setText(f"输入文件夹：{folder}")
            

    def select_input(self):
        folder = QFileDialog.getExistingDirectory(self, "选择Cam文件夹")
        if folder:
            self.input_folder = folder
            self.input_label.setText(f"输入文件夹：{folder}")

    def select_output(self):
        folder = QFileDialog.getExistingDirectory(self, "选择输出文件夹")
        if folder:
            self.output_folder = folder
            self.output_label.setText(f"输出文件夹：{folder}")

    def start_processing(self):
        if hasattr(self, 'qtake_folder') and hasattr(self, 'input_folder') and hasattr(self, 'output_folder'):
            self.processor = Processor()
            self.processor.update_progress.connect(self.update_progress)  # 连接进度更新信号
            qtake_count = len(os.listdir(self.qtake_folder))
            print("qtake_count",qtake_count)
            self.progress_bar.setRange(0, qtake_count)
            self.video_processor = VideoProcessor(self.qtake_folder, self.input_folder, self.output_folder, self.processor)
            self.video_processor.finished.connect(self.processing_finished)
            self.video_processor.start()            
            self.start_btn.setEnabled(False)
            self.log_area.clear()
        else:
            QMessageBox.warning(self, "警告", "请先选择qtake, 输入和输出文件夹")

    def stop_processing(self):
        if self.video_processor and self.video_processor.isRunning():
            self.video_processor.stop()  # 停止线程
            self.log_area.insertPlainText("处理已中止\n")

    def update_progress(self, progress, current_file):
        self.progress_bar.setValue(progress)
        logging.info(f"{current_file}")

    def processing_finished(self, result):
        self.start_btn.setEnabled(True)
        # success_count = result.get('success_count', 0)
        # failure_count = result.get('failure_count', 0)
        # failure_logs = result.get('failure_logs', [])

        # message = f"处理完成！\n成功: {success_count} 个，失败: {failure_count} 个。"
        # if failure_logs:
        #     message += "\n失败的视频和错误信息如下：\n" + "\n".join(failure_logs)

        # QMessageBox.information(self, "完成", message)
        self.log_area.insertPlainText("完成\n")

    def closeEvent(self, event):
        # 确保在关闭时停止线程
        if self.video_processor and self.video_processor.isRunning():
            self.video_processor.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
