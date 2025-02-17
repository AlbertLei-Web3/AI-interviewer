import sys
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from src.gui.main_window import MainWindow

def run_gui():
    app = QApplication(sys.argv)
    
    # 应用材料设计风格
    apply_stylesheet(app, theme='dark_teal.xml')
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    run_gui() 