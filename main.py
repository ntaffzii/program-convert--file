from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QComboBox, QLabel, QSpacerItem, QSizePolicy
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtWidgets import QProgressDialog, QMessageBox
import threading
import convert_file as cf

class DownloadThread(QThread):
    finished = Signal()
    error = Signal(str)

    def __init__(self, url, format_type, resolution=None, video_bitrate=None, audio_bitrate=None, fps=None):
        super().__init__()
        self.url = url
        self.format_type = format_type
        self.resolution = resolution
        self.video_bitrate = video_bitrate
        self.audio_bitrate = audio_bitrate
        self.fps = fps
        self._is_running = True  # ใช้สำหรับหยุดโปรเซส
        self.process = None
        self.yt_dlp_process = None

    def run(self):
        try:
            if self.format_type == "MP4":
                cf.download_and_resize(self.url, self.resolution, self.video_bitrate, self.audio_bitrate, self, self.fps)
            else:
                cf.download_mp3(self.url, self.audio_bitrate, self)

            if self._is_running:
                self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube to MP3/MP4 Downloader")
        self.setFixedSize(600, 300)  # Increase window height
        self.setStyleSheet("font-size: 16px; font-family: Arial;")
        # Add variable for QProgressDialog
        self.progress_dialog = None

        # Main layout
        layout = QVBoxLayout()

        # Row for link input and file format selection
        link_layout = QHBoxLayout()
        self.link_input = QLineEdit(self)
        self.link_input.setPlaceholderText("Enter YouTube link here")
        self.format_selector = QComboBox(self)
        self.format_selector.addItems(["MP3", "MP4"])
        self.format_selector.currentIndexChanged.connect(self.update_options)

        link_layout.addWidget(self.link_input)
        link_layout.addWidget(self.format_selector)
        layout.addLayout(link_layout)

        # Audio bitrate options
        self.quality_label = QLabel("Audio bitrate quality:")
        self.quality_selector = QComboBox(self)
        self.quality_selector.addItems(["Please select audio bitrate quality", "128k", "192k", "256k", "320k"])

        quality_layout = QHBoxLayout()
        quality_layout.addWidget(self.quality_label)
        quality_layout.addWidget(self.quality_selector)
        layout.addLayout(quality_layout)

        # Video resolution options
        self.resolution_label = QLabel("Video resolution:")
        self.resolution_selector = QComboBox(self)
        self.resolution_selector.addItems(["Please select video resolution", "360p", "720p", "1080p", "1440p", "2160p"])

        resolution_layout = QHBoxLayout()
        resolution_layout.addWidget(self.resolution_label)
        resolution_layout.addWidget(self.resolution_selector)
        layout.addLayout(resolution_layout)

        # Video bitrate options
        self.video_bitrate_label = QLabel("Video bitrate quality:")
        self.video_bitrate_input = QComboBox(self)
        self.video_bitrate_input.addItems(["Please select video bitrate quality", "4M", "6M", "10M", "15M", "20M", "25M", "30M"])

        video_bitrate_layout = QHBoxLayout()
        video_bitrate_layout.addWidget(self.video_bitrate_label)
        video_bitrate_layout.addWidget(self.video_bitrate_input)
        layout.addLayout(video_bitrate_layout)
        
        self.fps_label = QLabel("FPS:")
        self.fps_input = QComboBox(self)
        self.fps_input.addItems(["Please select frame rate (default)", "25", "30", "35", "45", "60"])

        # Audio bitrate options (for MP4)
        self.audio_bitrate_label_mp4 = QLabel("Audio bitrate quality:")
        self.audio_bitrate_input_mp4 = QComboBox(self)
        self.audio_bitrate_input_mp4.addItems(["Please select audio bitrate quality", "128k", "192k", "256k", "320k"])

        audio_bitrate_mp4_layout = QHBoxLayout()
        audio_bitrate_mp4_layout.addWidget(self.audio_bitrate_label_mp4)
        audio_bitrate_mp4_layout.addWidget(self.audio_bitrate_input_mp4)
        fps_layout = QHBoxLayout()
        fps_layout.addWidget(self.fps_label)
        fps_layout.addWidget(self.fps_input)
    
        layout.addLayout(audio_bitrate_mp4_layout)
        layout.addLayout(fps_layout)

        # Center the download button
        button_layout = QHBoxLayout()
        button_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.download_button = QPushButton("Download", self)
        self.download_button.setFixedSize(150, 40)  # Adjust button size
        self.download_button.clicked.connect(self.download_video)
        button_layout.addWidget(self.download_button)
        button_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum))
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_options()

    def update_options(self):
        """Update options when switching between MP3 and MP4 formats"""
        if self.format_selector.currentText() == "MP4":
            self.resolution_label.show()
            self.resolution_selector.show()
            self.video_bitrate_label.show()
            self.video_bitrate_input.show()
            self.audio_bitrate_label_mp4.show()
            self.audio_bitrate_input_mp4.show()
            self.fps_label.show()
            self.fps_input.show()

            self.quality_label.hide()
            self.quality_selector.hide()
        else:
            self.quality_label.show()
            self.quality_selector.show()

            # Hide video options
            self.resolution_label.hide()
            self.resolution_selector.hide()
            self.video_bitrate_label.hide()
            self.video_bitrate_input.hide()
            self.audio_bitrate_label_mp4.hide()
            self.audio_bitrate_input_mp4.hide()
            self.fps_input.hide()
            self.fps_label.hide()

    def download_video(self):
        """Function to download video or audio"""
        url = self.link_input.text()
        format_type = self.format_selector.currentText()
        resolution = self.resolution_selector.currentText() if format_type == "MP4" else None
        video_bitrate = self.video_bitrate_input.currentText() if format_type == "MP4" else None
        audio_bitrate = self.audio_bitrate_input_mp4.currentText() if format_type == "MP4" else self.quality_selector.currentText()
        fps = self.fps_input.currentText() if format_type == "MP4" else None
        
        # Show QProgressDialog
        self.show_progress_dialog()

        # Create a thread for downloading
        self.thread = DownloadThread(url, format_type, resolution, video_bitrate, audio_bitrate, fps)
        self.thread.finished.connect(self.on_download_finished)
        self.thread.error.connect(self.on_download_error)
        self.thread.start()
        
    def show_progress_dialog(self):
        """Show QProgressDialog"""
        self.progress_dialog = QProgressDialog("Converting file...", "Cancel", 0, 0, self)
        self.progress_dialog.setWindowTitle("File Conversion Status")
        self.progress_dialog.setFixedSize(300, 100)  # Adjust dialog size
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.setMinimumDuration(0)
        self.progress_dialog.setAutoClose(True)
        self.progress_dialog.setAutoReset(True)
        self.progress_dialog.canceled.connect(self.cancel_download)
        self.progress_dialog.show()

    def cancel_download(self):
        """Stop downloading and converting files"""
        if self.thread and self.thread.isRunning():
            self.thread._is_running = False  # Set to stop the thread
            self.thread.wait()  # Wait for the thread to stop

        if self.progress_dialog:
            self.progress_dialog.close()

    def on_download_finished(self):
        """Called when the download is complete"""
        if self.progress_dialog:
            self.progress_dialog.setValue(100)
            self.progress_dialog.close()
        QMessageBox.information(self, "Success", "File conversion completed!")

    def on_download_error(self, error_message):
        """Called when an error occurs"""
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Error", f"An error occurred: {error_message}")

if __name__ == "__main__":
    app = QApplication([])
    window = YouTubeDownloader()
    window.show()
    app.exec()