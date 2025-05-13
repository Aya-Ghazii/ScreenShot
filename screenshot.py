# CodeSnap - Code Screenshot Generator
# main.py

import sys
import os
import traceback
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QColorDialog, QFontDialog, QSpinBox, 
                            QLabel, QFileDialog, QComboBox, QGroupBox, QSlider, QCheckBox,
                            QMessageBox)
from PyQt5.QtGui import QFont, QColor, QPixmap, QPainter
from PyQt5.QtCore import Qt, QRect

class CodeSnap(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setAttribute(Qt.WA_DeleteOnClose, False)  # Prevent premature closing
        
        try:
            self.initUI()
            
            # Default settings
            self.bg_color = QColor("#1D1F21")
            self.text_color = QColor("#FFFFFF")
            self.highlight_color = QColor("#3E4451")
            self.font = QFont("Consolas", 12)
            self.padding = 40
            self.highlight_lines = set()
            self.themes = {
                "Dark": {"bg": "#1D1F21", "text": "#FFFFFF", "highlight": "#3E4451"},
                "Light": {"bg": "#FFFFFF", "text": "#1D1F21", "highlight": "#E8E8E8"},
                "Monokai": {"bg": "#272822", "text": "#F8F8F2", "highlight": "#49483E"},
                "Solarized Light": {"bg": "#FDF6E3", "text": "#586E75", "highlight": "#EEE8D5"},
                "Solarized Dark": {"bg": "#002B36", "text": "#839496", "highlight": "#073642"},
                "Dracula": {"bg": "#282A36", "text": "#F8F8F2", "highlight": "#44475A"},
            }
            
            print("CodeSnap initialized successfully")
        except Exception as e:
            self.show_error("Initialization Error", f"Failed to initialize: {str(e)}")
            traceback.print_exc()

    def initUI(self):
        self.setWindowTitle('CodeSnap')
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Left panel (editor and options)
        left_panel = QVBoxLayout()
        
        # Code editor section
        editor_group = QGroupBox("Code Editor")
        editor_layout = QVBoxLayout()
        
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 12))
        self.code_editor.setPlaceholderText("Paste your code here...")
        
        # Line highlighting controls
        line_highlight_layout = QHBoxLayout()
        line_highlight_layout.addWidget(QLabel("From line:"))
        self.line_start = QSpinBox()
        self.line_start.setMinimum(1)
        line_highlight_layout.addWidget(self.line_start)
        
        line_highlight_layout.addWidget(QLabel("To:"))
        self.line_end = QSpinBox()
        self.line_end.setMinimum(1)
        line_highlight_layout.addWidget(self.line_end)
        
        highlight_btn = QPushButton("Highlight Lines")
        highlight_btn.clicked.connect(self.highlight_lines)
        line_highlight_layout.addWidget(highlight_btn)
        
        clear_highlight_btn = QPushButton("Clear Highlights")
        clear_highlight_btn.clicked.connect(self.clear_highlights)
        line_highlight_layout.addWidget(clear_highlight_btn)
        
        editor_layout.addWidget(self.code_editor)
        editor_layout.addLayout(line_highlight_layout)
        editor_group.setLayout(editor_layout)
        
        # Customization options
        options_group = QGroupBox("Customization")
        options_layout = QVBoxLayout()
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "Monokai", "Solarized Light", "Solarized Dark", "Dracula"])
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        options_layout.addLayout(theme_layout)
        
        # Font selection
        font_btn = QPushButton("Change Font")
        font_btn.clicked.connect(self.change_font)
        options_layout.addWidget(font_btn)
        
        # Color customization
        colors_layout = QHBoxLayout()
        bg_color_btn = QPushButton("Background Color")
        bg_color_btn.clicked.connect(lambda: self.change_color("bg"))
        text_color_btn = QPushButton("Text Color")
        text_color_btn.clicked.connect(lambda: self.change_color("text"))
        highlight_color_btn = QPushButton("Highlight Color")
        highlight_color_btn.clicked.connect(lambda: self.change_color("highlight"))
        colors_layout.addWidget(bg_color_btn)
        colors_layout.addWidget(text_color_btn)
        colors_layout.addWidget(highlight_color_btn)
        options_layout.addLayout(colors_layout)
        
        # Padding adjustment
        padding_layout = QHBoxLayout()
        padding_layout.addWidget(QLabel("Padding:"))
        self.padding_slider = QSlider(Qt.Horizontal)
        self.padding_slider.setRange(10, 100)
        self.padding_slider.setValue(40)
        self.padding_slider.valueChanged.connect(self.update_padding)
        self.padding_value = QLabel("40px")
        padding_layout.addWidget(self.padding_slider)
        padding_layout.addWidget(self.padding_value)
        options_layout.addLayout(padding_layout)
        
        # Size options
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width:"))
        self.width_spin = QSpinBox()
        self.width_spin.setRange(400, 2000)
        self.width_spin.setValue(800)
        size_layout.addWidget(self.width_spin)
        
        size_layout.addWidget(QLabel("Height:"))
        self.height_spin = QSpinBox()
        self.height_spin.setRange(300, 2000)
        self.height_spin.setValue(600)
        size_layout.addWidget(self.height_spin)
        options_layout.addLayout(size_layout)
        
        # Window controls toggle
        self.window_controls = QCheckBox("Show Window Controls")
        self.window_controls.setChecked(True)
        options_layout.addWidget(self.window_controls)
        
        # Generate button
        generate_btn = QPushButton("Generate Screenshot")
        generate_btn.clicked.connect(self.generate_screenshot)
        options_layout.addWidget(generate_btn)
        
        options_group.setLayout(options_layout)
        
        # Add to left panel
        left_panel.addWidget(editor_group)
        left_panel.addWidget(options_group)
        
        # Preview area
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel("Preview will appear here")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(400, 300)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        
        # Save button
        save_btn = QPushButton("Save Screenshot")
        save_btn.clicked.connect(self.save_screenshot)
        preview_layout.addWidget(self.preview_label)
        preview_layout.addWidget(save_btn)
        preview_group.setLayout(preview_layout)
        
        # Add to main layout
        main_layout.addLayout(left_panel, 2)
        main_layout.addWidget(preview_group, 1)

    def show_error(self, title, message):
        QMessageBox.critical(self, title, message)
        print(f"{title}: {message}")

    def change_theme(self, theme_name):
        theme = self.themes[theme_name]
        self.bg_color = QColor(theme["bg"])
        self.text_color = QColor(theme["text"])
        self.highlight_color = QColor(theme["highlight"])
        self.update_preview()

    def change_font(self):
        font, ok = QFontDialog.getFont(self.font, self)
        if ok:
            self.font = font
            self.code_editor.setFont(font)
            self.update_preview()

    def change_color(self, color_type):
        color = None
        if color_type == "bg":
            color = QColorDialog.getColor(self.bg_color, self, "Choose Background Color")
            if color.isValid():
                self.bg_color = color
        elif color_type == "text":
            color = QColorDialog.getColor(self.text_color, self, "Choose Text Color")
            if color.isValid():
                self.text_color = color
        elif color_type == "highlight":
            color = QColorDialog.getColor(self.highlight_color, self, "Choose Highlight Color")
            if color.isValid():
                self.highlight_color = color
        
        if color and color.isValid():
            self.update_preview()

    def update_padding(self):
        self.padding = self.padding_slider.value()
        self.padding_value.setText(f"{self.padding}px")
        self.update_preview()

    def highlight_lines(self):
        start = self.line_start.value()
        end = self.line_end.value()
        
        if start > end:
            start, end = end, start
            
        self.highlight_lines.update(range(start, end + 1))
        self.update_preview()

    def clear_highlights(self):
        self.highlight_lines.clear()
        self.update_preview()

    def update_preview(self):
        pixmap = self.create_code_snapshot()
        if pixmap:
            self.preview_label.setPixmap(
                pixmap.scaled(self.preview_label.width(), 
                             self.preview_label.height(),
                             Qt.KeepAspectRatio,
                             Qt.SmoothTransformation)
            )

    def generate_screenshot(self):
        self.update_preview()

    def create_code_snapshot(self):
        try:
            code = self.code_editor.toPlainText()
            if not code.strip():
                return None
                
            width = self.width_spin.value()
            height = self.height_spin.value()
            
            pixmap = QPixmap(width, height)
            pixmap.fill(self.bg_color)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setRenderHint(QPainter.TextAntialiasing)
            
            # Window controls
            if self.window_controls.isChecked():
                radius = 8
                y_pos = self.padding // 2
                painter.setPen(Qt.NoPen)
                
                # Close button (red)
                painter.setBrush(QColor("#FF5F56"))
                painter.drawEllipse(self.padding, y_pos, radius, radius)
                
                # Minimize button (yellow)
                painter.setBrush(QColor("#FFBD2E"))
                painter.drawEllipse(self.padding + radius * 2, y_pos, radius, radius)
                
                # Maximize button (green)
                painter.setBrush(QColor("#27C93F"))
                painter.drawEllipse(self.padding + radius * 4, y_pos, radius, radius)
            
            # Code drawing
            lines = code.split('\n')
            line_height = self.code_editor.fontMetrics().height()
            y_offset = self.padding + (20 if self.window_controls.isChecked() else 0)
            
            # Highlight lines
            painter.setPen(Qt.NoPen)
            painter.setBrush(self.highlight_color)
            for line_num in self.highlight_lines:
                if 1 <= line_num <= len(lines):
                    rect = QRect(
                        self.padding // 2,
                        y_offset + (line_num - 1) * line_height,
                        width - self.padding,
                        line_height
                    )
                    painter.drawRect(rect)
            
            # Draw text
            painter.setFont(self.font)
            painter.setPen(self.text_color)
            for i, line in enumerate(lines):
                y_pos = y_offset + (i + 0.8) * line_height
                painter.drawText(self.padding, int(y_pos), line)
            
            painter.end()
            return pixmap
            
        except Exception as e:
            self.show_error("Rendering Error", f"Failed to create snapshot: {str(e)}")
            traceback.print_exc()
            return None

    def save_screenshot(self):
        pixmap = self.create_code_snapshot()
        if not pixmap:
            return
            
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Save Screenshot",
            os.path.expanduser("~/codesnap.png"),
            "PNG Images (*.png);;JPEG Images (*.jpg *.jpeg)"
        )
        
        if filename:
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filename += '.png'
            pixmap.save(filename)

if __name__ == '__main__':
    try:
        # Set up global exception handler
        def excepthook(exctype, value, traceback_obj):
            error_msg = ''.join(traceback.format_exception(exctype, value, traceback_obj))
            print(f"ERROR: {error_msg}")
            with open("codesnap_error.log", "a") as f:
                f.write(f"=== {datetime.now()} ===\n{error_msg}\n====================\n\n")
            
            QMessageBox.critical(None, "Error", f"An error occurred:\n{str(value)}")
        
        sys.excepthook = excepthook
        
        # Create and run application
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        window = CodeSnap()
        window.show()
        
        app.main_window = window
        
        sys.exit(app.exec_())
        
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        traceback.print_exc()
        input("Press Enter to exit...")