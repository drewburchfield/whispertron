#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import threading
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QPushButton, QComboBox,
                            QFileDialog, QProgressBar, QTextEdit, QCheckBox,
                            QListWidget, QGroupBox, QRadioButton, QTabWidget,
                            QMessageBox)
from PyQt6.QtCore import Qt, pyqtSignal, QObject, QUrl
from PyQt6.QtGui import QFont, QDragEnterEvent, QDropEvent

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.transcribe import transcribe_file

# Global output directory
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "exports")

class Worker(QObject):
    """Worker thread for transcription to avoid freezing UI"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, file_path, model, language, formats, use_coreml, output_dir=None):
        super().__init__()
        self.file_path = file_path
        self.model = model
        self.language = language
        self.formats = formats
        self.use_coreml = use_coreml
        self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
    
    def run(self):
        try:
            self.progress.emit(f"Starting transcription of {os.path.basename(self.file_path)}")
            result = transcribe_file(
                self.file_path,
                model=self.model,
                language=self.language,
                output_formats=self.formats,
                use_coreml=self.use_coreml
            )
            
            # Check output dirs - this is for debugging
            if result:
                output_dir = result["output_dir"]
                self.progress.emit(f"Output directory: {output_dir}")
                
                # Check if directory exists
                if os.path.exists(output_dir):
                    # List files in the output directory
                    files = os.listdir(output_dir)
                    if files:
                        self.progress.emit(f"Files in output directory: {', '.join(files)}")
                    else:
                        self.progress.emit("Output directory exists but is empty")
                        
                        # Try to manually copy the file as a fallback
                        try:
                            base_name = os.path.basename(self.file_path)
                            name_without_ext = os.path.splitext(base_name)[0]
                            
                            for fmt in self.formats:
                                # Check if files exist in project dir and not in output dir
                                potential_file = f"{name_without_ext}.{fmt}"
                                if os.path.exists(potential_file):
                                    self.progress.emit(f"Found file in project root: {potential_file}")
                                    shutil.copy(potential_file, os.path.join(output_dir, potential_file))
                                    self.progress.emit(f"Copied to output directory")
                        except Exception as e:
                            self.progress.emit(f"Error copying files: {str(e)}")
                else:
                    self.progress.emit("Output directory does not exist")
                
                self.finished.emit(result)
            else:
                self.error.emit("Transcription failed")
        except Exception as e:
            self.error.emit(f"Error during transcription: {str(e)}")

class DropArea(QWidget):
    """Widget that accepts drag and drop of audio files"""
    fileDropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        layout = QVBoxLayout()
        
        self.label = QLabel("Drop Audio Files Here\nor")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Arial", 18))
        
        self.button = QPushButton("Browse Files...")
        self.button.clicked.connect(self.browse_files)
        
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        self.setLayout(layout)
        
        # Set min size
        self.setMinimumHeight(200)
        
        # Set styling
        self.setStyleSheet("""
            border: 2px dashed #aaa;
            border-radius: 8px;
            padding: 20px;
            background-color: #f8f8f8;
        """)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            self.fileDropped.emit(file_path)
    
    def browse_files(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select Audio File", "", 
            "Audio Files (*.mp3 *.wav *.m4a *.mp4 *.mov *.ogg *.opus)"
        )
        if file_path:
            self.fileDropped.emit(file_path)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whispertron - Audio Transcription")
        self.setMinimumSize(800, 600)
        
        # Initialize output directory
        self.output_dir = DEFAULT_OUTPUT_DIR
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create tabs
        tabs = QTabWidget()
        transcribe_tab = QWidget()
        settings_tab = QWidget()
        about_tab = QWidget()
        
        tabs.addTab(transcribe_tab, "Transcribe")
        tabs.addTab(settings_tab, "Settings")
        tabs.addTab(about_tab, "About")
        
        # Transcribe tab layout
        transcribe_layout = QVBoxLayout(transcribe_tab)
        
        # Create drop area
        self.drop_area = DropArea()
        self.drop_area.fileDropped.connect(self.handle_file_dropped)
        transcribe_layout.addWidget(self.drop_area)
        
        # Settings group
        settings_group = QGroupBox("Transcription Settings")
        settings_layout = QHBoxLayout()
        
        # Model selection
        model_layout = QVBoxLayout()
        model_label = QLabel("Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny.en", "base.en", "small.en", "medium.en", "large-v3"])
        self.model_combo.setCurrentText("tiny.en")  # Start with tiny for testing
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        settings_layout.addLayout(model_layout)
        
        # Language selection
        language_layout = QVBoxLayout()
        language_label = QLabel("Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Auto Detect", "English", "Spanish", "French", "German", "Chinese"])
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)
        settings_layout.addLayout(language_layout)
        
        # Export formats
        formats_layout = QVBoxLayout()
        formats_label = QLabel("Export formats:")
        self.txt_checkbox = QCheckBox("Text (.txt)")
        self.txt_checkbox.setChecked(True)
        self.srt_checkbox = QCheckBox("Subtitles (.srt)")
        self.srt_checkbox.setChecked(True)
        self.vtt_checkbox = QCheckBox("Web Subtitles (.vtt)")
        self.vtt_checkbox.setChecked(True)
        
        formats_layout.addWidget(formats_label)
        formats_layout.addWidget(self.txt_checkbox)
        formats_layout.addWidget(self.srt_checkbox)
        formats_layout.addWidget(self.vtt_checkbox)
        settings_layout.addLayout(formats_layout)
        
        # CoreML checkbox
        coreml_layout = QVBoxLayout()
        self.coreml_checkbox = QCheckBox("Use CoreML Acceleration")
        self.coreml_checkbox.setChecked(True)
        coreml_layout.addWidget(self.coreml_checkbox)
        settings_layout.addLayout(coreml_layout)
        
        settings_group.setLayout(settings_layout)
        transcribe_layout.addWidget(settings_group)
        
        # Create log area
        log_group = QGroupBox("Transcription Log")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        log_layout.addWidget(self.log_text)
        log_layout.addWidget(self.progress_bar)
        log_group.setLayout(log_layout)
        transcribe_layout.addWidget(log_group)
        
        # Settings tab content
        settings_tab_layout = QVBoxLayout(settings_tab)
        
        # Default output directory
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()
        
        # Display current output directory
        self.output_dir_label = QLabel(f"Current output directory: {self.output_dir}")
        output_layout.addWidget(self.output_dir_label)
        
        # Add button to change output directory
        self.output_dir_button = QPushButton("Change Default Output Directory")
        self.output_dir_button.clicked.connect(self.change_output_directory)
        output_layout.addWidget(self.output_dir_button)
        
        # Add button to open output directory
        self.open_output_dir_button = QPushButton("Open Output Directory")
        self.open_output_dir_button.clicked.connect(self.open_output_directory)
        output_layout.addWidget(self.open_output_dir_button)
        
        output_group.setLayout(output_layout)
        settings_tab_layout.addWidget(output_group)
        
        # Advanced settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QVBoxLayout()
        threads_label = QLabel("Number of CPU Threads:")
        self.threads_combo = QComboBox()
        self.threads_combo.addItems(["1", "2", "4", "8", "12", "16"])
        self.threads_combo.setCurrentText("8")
        advanced_layout.addWidget(threads_label)
        advanced_layout.addWidget(self.threads_combo)
        advanced_group.setLayout(advanced_layout)
        settings_tab_layout.addWidget(advanced_group)
        
        # Padding at the bottom of settings tab
        settings_tab_layout.addStretch()
        
        # About tab content
        about_tab_layout = QVBoxLayout(about_tab)
        about_text = QLabel(
            "Whispertron - A powerful audio transcription tool\n\n"
            "Built with OpenAI's Whisper model (via whisper.cpp)\n"
            "Optimized for Apple Silicon with CoreML\n\n"
            "All processing happens locally on your device.\n"
            "No data is sent to external servers.\n\n"
            "© 2025 - Created with ❤️"
        )
        about_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        about_text.setFont(QFont("Arial", 14))
        about_tab_layout.addWidget(about_text)
        
        # Add tabs to main layout
        main_layout.addWidget(tabs)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Initialize worker thread
        self.worker_thread = None
        
        # Log initialization
        self.log("Whispertron initialized and ready to transcribe")
    
    def log(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def change_output_directory(self):
        """Change the default output directory"""
        dir_dialog = QFileDialog()
        dir_dialog.setFileMode(QFileDialog.FileMode.Directory)
        dir_dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        
        if dir_dialog.exec():
            selected_dir = dir_dialog.selectedFiles()[0]
            self.output_dir = selected_dir
            self.output_dir_label.setText(f"Current output directory: {self.output_dir}")
            self.log(f"Output directory changed to: {self.output_dir}")
    
    def open_output_directory(self):
        """Open the output directory in the system file explorer"""
        if os.path.exists(self.output_dir):
            self.log(f"Opening output directory: {self.output_dir}")
            
            # Open file explorer with the directory
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', self.output_dir])
            elif sys.platform == 'win32':  # Windows
                subprocess.run(['explorer', self.output_dir])
            elif sys.platform == 'linux':  # Linux
                subprocess.run(['xdg-open', self.output_dir])
        else:
            self.log(f"Error: Output directory does not exist: {self.output_dir}")
            QMessageBox.warning(self, "Directory Not Found", 
                               f"The output directory does not exist: {self.output_dir}")
    
    def handle_file_dropped(self, file_path):
        """Handle file dropped or selected"""
        # Check if file is supported
        extensions = ['.mp3', '.wav', '.m4a', '.mp4', '.mov', '.ogg', '.opus']
        if not any(file_path.lower().endswith(ext) for ext in extensions):
            self.log(f"Error: Unsupported file format for {file_path}")
            return
        
        self.log(f"Processing file: {file_path}")
        
        # Get selected model
        model = self.model_combo.currentText()
        
        # Get language (convert from display name to code if needed)
        language_display = self.language_combo.currentText()
        language_map = {
            "Auto Detect": None,
            "English": "en",
            "Spanish": "es",
            "French": "fr",
            "German": "de",
            "Chinese": "zh"
        }
        language = language_map.get(language_display)
        
        # Get formats
        formats = []
        if self.txt_checkbox.isChecked():
            formats.append("txt")
        if self.srt_checkbox.isChecked():
            formats.append("srt")
        if self.vtt_checkbox.isChecked():
            formats.append("vtt")
        
        # Check if at least one format is selected
        if not formats:
            self.log("Error: Please select at least one output format")
            return
        
        # Get CoreML setting
        use_coreml = self.coreml_checkbox.isChecked()
        
        # Start worker thread
        self.worker = Worker(file_path, model, language, formats, use_coreml, self.output_dir)
        self.worker_thread = threading.Thread(target=self.worker.run)
        self.worker.progress.connect(self.log)
        self.worker.finished.connect(self.handle_transcription_finished)
        self.worker.error.connect(self.handle_transcription_error)
        
        # Show progress bar
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        
        # Start transcription
        self.worker_thread.start()
    
    def handle_transcription_finished(self, result):
        """Handle successful transcription"""
        self.log(f"Transcription completed successfully!")
        
        # Check if there are any output files
        if not result["outputs"]:
            self.log("Warning: No output files were generated.")
            
            # Show a message box with option to open the directory
            msg_box = QMessageBox()
            msg_box.setWindowTitle("No Output Files")
            msg_box.setText("The transcription process completed, but no output files were found.")
            msg_box.setInformativeText("Would you like to open the output directory to check?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                self.open_output_directory()
        else:
            for fmt, path in result["outputs"].items():
                self.log(f"- {fmt.upper()} output: {path}")
            
            # Ask if the user wants to open the directory
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Transcription Complete")
            msg_box.setText("Transcription completed successfully!")
            msg_box.setInformativeText("Would you like to open the output directory?")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            if msg_box.exec() == QMessageBox.StandardButton.Yes:
                output_dir = result["output_dir"]
                if os.path.exists(output_dir):
                    if sys.platform == 'darwin':  # macOS
                        subprocess.run(['open', output_dir])
                    elif sys.platform == 'win32':  # Windows
                        subprocess.run(['explorer', output_dir])
                    elif sys.platform == 'linux':  # Linux
                        subprocess.run(['xdg-open', output_dir])
        
        # Reset progress bar
        self.progress_bar.setVisible(False)
        
        # Clean up thread
        self.worker_thread = None
    
    def handle_transcription_error(self, error_message):
        """Handle transcription error"""
        self.log(f"Error: {error_message}")
        
        # Reset progress bar
        self.progress_bar.setVisible(False)
        
        # Clean up thread
        self.worker_thread = None

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main() 