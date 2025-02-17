from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QTextEdit, QLabel, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from qt_material import apply_stylesheet
import sys

class AudioRecordThread(QThread):
    """音频录制线程"""
    finished = pyqtSignal(str)  # 录制完成信号
    progress = pyqtSignal(int)  # 进度信号

    def __init__(self):
        super().__init__()
        from src.main import InterviewAssistant
        self.assistant = InterviewAssistant()
        self.is_recording = False

    def run(self):
        # 开始录音
        self.assistant.start_recording()
        self.is_recording = True
        
        # 模拟进度更新
        while self.is_recording:
            self.progress.emit(50)  # 显示录音进行中
            self.msleep(100)
        
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self.assistant.stop_recording())
        self.finished.emit(result if result else "录音完成")
        loop.close()

class ProcessingThread(QThread):
    """文本处理线程"""
    finished = pyqtSignal(str)  # 处理完成信号
    progress = pyqtSignal(dict)  # 进度信号，包含各步骤进度

    def __init__(self, text):
        super().__init__()
        self.text = text
        from src.postprocess.processor import TextProcessor
        self.processor = TextProcessor()

    def run(self):
        # 处理文本
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 更新进度
        self.progress.emit({
            "拼写检查": 0,
            "语法检查": 0,
            "语义分析": 0,
            "术语检查": 0
        })
        
        # 执行处理
        result = loop.run_until_complete(self.processor.process(self.text))
        
        # 更新最终进度
        self.progress.emit({
            "拼写检查": 100,
            "语法检查": 100,
            "语义分析": 100,
            "术语检查": 100
        })
        
        # 发送结果
        self.finished.emit(result if result else "处理完成")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.record_thread = None
        self.init_ui()

    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("AI Interview Assistant")
        self.setMinimumSize(800, 600)

        # 主布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 录音控制区域
        self.init_record_controls(layout)
        
        # 文本显示区域
        self.init_text_display(layout)
        
        # 处理进度区域
        self.init_progress_display(layout)

    def init_record_controls(self, layout):
        """初始化录音控制"""
        self.record_btn = QPushButton("开始录音")
        self.record_btn.clicked.connect(self.toggle_recording)
        layout.addWidget(self.record_btn)

        self.record_status = QLabel("准备就绪")
        layout.addWidget(self.record_status)

    def init_text_display(self, layout):
        """初始化文本显示区域"""
        # 原文显示
        self.original_text = QTextEdit()
        self.original_text.setPlaceholderText("这里显示语音识别结果...")
        layout.addWidget(QLabel("语音识别结果:"))
        layout.addWidget(self.original_text)

        # 处理后文本显示
        self.processed_text = QTextEdit()
        self.processed_text.setPlaceholderText("这里显示处理后的文本...")
        layout.addWidget(QLabel("处理结果:"))
        layout.addWidget(self.processed_text)

    def init_progress_display(self, layout):
        """初始化进度显示"""
        self.progress_bars = {}
        for step in ["拼写检查", "语法检查", "语义分析", "术语检查"]:
            label = QLabel(step)
            progress = QProgressBar()
            layout.addWidget(label)
            layout.addWidget(progress)
            self.progress_bars[step] = progress

    def toggle_recording(self):
        """切换录音状态"""
        if not self.record_thread or not self.record_thread.isRunning():
            # 开始录音
            self.record_btn.setText("停止录音")
            self.record_thread = AudioRecordThread()
            self.record_thread.finished.connect(self.on_record_finished)
            self.record_thread.progress.connect(self.update_record_progress)
            self.record_thread.start()
        else:
            # 停止录音
            self.record_btn.setText("开始录音")
            self.record_thread.stop_recording()

    def on_record_finished(self, text):
        """录音完成处理"""
        self.original_text.setText(text)
        self.start_processing(text)

    def start_processing(self, text):
        """开始文本处理"""
        self.process_thread = ProcessingThread(text)
        self.process_thread.finished.connect(self.on_process_finished)
        self.process_thread.progress.connect(self.update_process_progress)
        self.process_thread.start()

    def update_record_progress(self, value):
        """更新录音进度"""
        self.record_status.setText(f"录音中... {value}%")

    def update_process_progress(self, progress_dict):
        """更新处理进度"""
        for step, value in progress_dict.items():
            if step in self.progress_bars:
                self.progress_bars[step].setValue(value)

    def on_process_finished(self, result):
        """处理完成"""
        self.processed_text.setText(result) 