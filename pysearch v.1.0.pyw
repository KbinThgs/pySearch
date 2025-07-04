import sys
import os
import subprocess
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLineEdit, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QPushButton, QLabel,
    QScrollArea
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt

# Get user's home folder
USER_FOLDER = os.path.expanduser("~")

# File extensions
PHOTO_EXTS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".heic"]

# Emoji icons for different file types
FILE_ICONS = {
    ".png": "🖼️", ".jpg": "🖼️", ".jpeg": "🖼️", ".gif": "🖼️", ".webp": "🖼️", ".bmp": "🖼️", ".heic": "🖼️",
    ".pdf": "📄", ".doc": "📄", ".docx": "📄", ".txt": "🧾",
    ".mp3": "🎵", ".wav": "🎵", ".mp4": "🎥",
    ".lnk": "🔗", ".zip": "🗜️", ".py": "🐍"
}

# Function to get icon by extension
def get_file_icon(name):
    ext = os.path.splitext(name)[1].lower()
    if ext in FILE_ICONS:
        return FILE_ICONS[ext]
    else:
        # Pokud název nemá tečku (tedy složka), můžeš tam dát třeba 📁
        if "." not in name:
            return "📁"
        # Pokud má tečku, ale není v FILE_ICONS, tak ⚫
        return "⚫"

# Main spotlight class
class Spotlight(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PySearch")
        self.setFixedSize(500, 505)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet("background-color: #222; border-radius: 10px; color: white;")
        self.setWindowIcon(QIcon("pysearch.ico"))

        # Top bar: search input + close button
        top_layout = QHBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("Search anything...")
        self.input.textChanged.connect(self.update_results)
        self.input.setStyleSheet("""
            QLineEdit {
                background: #333;
                color: white;
                padding: 7px;
                font-size: 18px;
                border: none;
                border-radius: 10px;
            }
        """)

        self.close_btn = QPushButton("X")
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #555;
                color: white;
                font-weight: bold;
                border-radius: 15px;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #f33;
            }
        """)
        self.close_btn.clicked.connect(self.close)

        top_layout.addWidget(self.input)
        top_layout.addWidget(self.close_btn)

        # Scroll area for results
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("border: none;")
        self.scroll.setFixedHeight(450)

        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)

        # Welcome label inside result area
        self.welcome_label = QLabel("Welcome to pySearch, search anything on your computer.")
        self.welcome_label.setStyleSheet("color: #CACDCA; font-size: 16px; padding: 20px;")
        self.welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.container_layout.addWidget(self.welcome_label)

        self.scroll.setWidget(self.container)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.scroll)

        self.setLayout(main_layout)

        self.center()
        self.result_widgets = []
        self.max_rows_per_list = 5
        self.row_height = 25

    # Center the window on screen
    def center(self):
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, (screen.height() - self.height()) // 2)

    # Clear all result widgets (but not the welcome label)
    def clear_results(self):
        for widget in self.result_widgets:
            widget.deleteLater()
        self.result_widgets.clear()
        self.container_layout.update()

    # Handle searching and showing results
    def update_results(self):
        query = self.input.text().strip().lower()
        self.clear_results()

        if not query:
            self.welcome_label.show()
            return
        else:
            self.welcome_label.hide()

        folders, apps, docs, photos = [], [], [], []

        for root, dirs, files in os.walk(USER_FOLDER):
            for name in files + dirs:
                name_lower = name.lower()
                if query in name_lower or name_lower.startswith(query) or query in name_lower.replace(" ", ""):
                    full_path = os.path.join(root, name)
                    ext = os.path.splitext(name)[1].lower()

                    if os.path.isdir(full_path):
                        folders.append((name, full_path))
                    elif ext in PHOTO_EXTS:
                        photos.append((name, full_path))
                    elif ext == ".lnk":
                        apps.append((name, full_path))
                    else:
                        docs.append((name, full_path))

                    if len(folders + apps + docs + photos) >= 40:
                        break
            if len(folders + apps + docs + photos) >= 40:
                break

        self.add_list(folders)
        self.add_list(apps)
        self.add_list(docs)
        self.add_list(photos)

    # Add a list widget with search results
    def add_list(self, items):
        if not items:
            return
        list_widget = QListWidget()
        list_widget.setStyleSheet("""
            QListWidget {
                background: #111;
                color: white;
                font-size: 15px;
                border: none;
                margin-top: 5px;
                padding-top: 5px;
                padding-bottom: 5px;
            }
            QListWidget::item:selected {
                background-color: #444;
            }
        """)
        list_widget.setMaximumHeight(self.max_rows_per_list * self.row_height)

        for name, path in items:
            icon = get_file_icon(name)
            item = QListWidgetItem(f"{icon} {name}")
            item.setData(Qt.ItemDataRole.UserRole, path)
            list_widget.addItem(item)

        list_widget.itemDoubleClicked.connect(self.launch_item)
        self.container_layout.addWidget(list_widget)
        self.result_widgets.append(list_widget)

    # Open file or folder when item is double-clicked
    def launch_item(self, item):
        path = item.data(Qt.ItemDataRole.UserRole)
        try:
            if os.path.isfile(path):
                os.startfile(path)
            else:
                subprocess.Popen(['explorer', path])
        except Exception as e:
            print("Error:", e)
        self.close()

# Run app
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Spotlight()
    window.show()
    sys.exit(app.exec())
