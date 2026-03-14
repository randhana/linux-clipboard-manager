import sys
import os
import subprocess
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QLabel,
    QSystemTrayIcon, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont, QKeyEvent, QIcon, QClipboard

from . import db

def simulate_paste():
    # Wait a tiny bit for the GUI window to close and focus to return to previous window
    time.sleep(0.1)
    
    session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
    
    try:
        if session_type == 'wayland':
            # wtype simulates keystrokes in Wayland
            subprocess.run(['wtype', '-M', 'ctrl', '-k', 'v', '-m', 'ctrl'], check=False)
            # fallback if wtype isn't installed: skip or try ydotool
        else:
            # X11 fallback
            subprocess.run(['xdotool', 'key', 'ctrl+v'], check=False)
    except FileNotFoundError:
        print("wtype or xdotool not found. Auto-paste will not work.")

class ClipboardGUI(QWidget):
    def __init__(self):
        super().__init__()
        # Frameless, kept on top, and doesn't steal focus from other apps
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.resize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e2e;
                color: #cdd6f4;
                border: 1px solid #45475a;
                border-radius: 8px;
            }
            QLabel {
                padding: 10px;
                font-weight: bold;
                font-size: 14px;
                background-color: #313244;
                border-bottom: 1px solid #45475a;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QListWidget {
                border: none;
                outline: none;
                margin: 5px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #313244;
            }
            QListWidget::item:selected {
                background-color: #89b4fa;
                color: #1e1e2e;
                border-radius: 4px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        title = QLabel("Clipboard History")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        font = QFont("Sans Serif", 11)
        self.list_widget.setFont(font)
        self.list_widget.itemClicked.connect(self.on_item_clicked)
        self.list_widget.currentItemChanged.connect(self.on_current_item_changed)
        self.load_items()

        # Flag for tracking internal updates so we don't reload list
        self.internal_clipboard_update_text = None
        layout.addWidget(self.list_widget)

        # Auto-hide timer
        self.hide_timer = QTimer(self)
        self.hide_timer.timeout.connect(self.hide)
        self.hide_timer.setInterval(60000) # 1 minute of inactivity

        # Add old_pos for window dragging
        self.old_pos = None

    def on_current_item_changed(self, current, previous):
        if current:
            self.reset_hide_timer()
            content = current.data(Qt.ItemDataRole.UserRole)
            self.internal_clipboard_update_text = content
            
            # Update clipboard silently
            clipboard = QApplication.clipboard()
            clipboard.setText(content, QClipboard.Mode.Clipboard)
            if clipboard.supportsSelection():
                clipboard.setText(content, QClipboard.Mode.Selection)
            
            import pyperclip
            try:
                pyperclip.copy(content)
            except Exception:
                pass

    def mousePressEvent(self, event):
        self.reset_hide_timer()
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        self.reset_hide_timer()
        if self.old_pos is not None:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.reset_hide_timer()
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    def on_clipboard_change(self):
        text = self.clipboard.text()
        if text:
            db.add_item(text)
            if self.isVisible():
                self.load_items()

    def showEvent(self, event):
        self.reset_hide_timer()
        self.load_items()
        super().showEvent(event)

    def reset_hide_timer(self):
        if self.isVisible():
            self.hide_timer.start()

    def hideEvent(self, event):
        self.hide_timer.stop()
        super().hideEvent(event)

    def load_items(self):
        self.list_widget.clear()
        items = db.get_items(50)
        for item_id, content in items:
            # Truncate content for display if too long, replace newlines
            display_text = content.replace('\n', ' \N{RETURN SYMBOL} ')
            if len(display_text) > 200:
                display_text = display_text[:200] + "..."
            
            list_item = QListWidgetItem(display_text)
            list_item.setData(Qt.ItemDataRole.UserRole, content)
            self.list_widget.addItem(list_item)
            
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def on_item_clicked(self, item):
        self.perform_paste(item)

    def keyPressEvent(self, event: QKeyEvent):
        self.reset_hide_timer()
        if event.key() == Qt.Key.Key_Escape:
            self.hide()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            item = self.list_widget.currentItem()
            if item:
                self.perform_paste(item)
        else:
            super().keyPressEvent(event)

    def perform_paste(self, item):
        content = item.data(Qt.ItemDataRole.UserRole)
        # Update DB to bring it to top
        db.add_item(content)
        
        self.on_current_item_changed(item, None)
        
        # We no longer hide automatically or auto-paste natively here
        # so the user can easily select multiple items and paste manually
        # whenever they decide to switch back to their app.

class ClipboardMonitor:
    def __init__(self, clipboard, gui_instance):
        self.clipboard = clipboard
        self.gui = gui_instance
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        
        # Initial save
        text = self.clipboard.text()
        if text:
            db.add_item(text)

    def on_clipboard_change(self):
        text = self.clipboard.text()
        if text:
            # Ignore clipboard updates that were triggered by us selecting an item
            if getattr(self.gui, 'internal_clipboard_update_text', None) == text:
                return
                
            db.add_item(text)
            if self.gui.isVisible():
                self.gui.load_items()

def main():
    app = QApplication(sys.argv)
    
    # Keep the application running even if the window is closed
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize DB in case GUI runs before daemon
    db.init_db()
    
    gui = ClipboardGUI()
    
    # Initialize Clipboard Monitor
    # we assign it to a variable so it doesn't get garbage collected
    monitor = ClipboardMonitor(app.clipboard(), gui)
    
    # Setup System Tray Icon
    # We use a standard system icon like 'edit-paste' or generic document
    tray_icon = QSystemTrayIcon(QIcon.fromTheme('edit-paste'), app)
    if not tray_icon.icon().isNull():
        pass
    else:
        # Fallback to another standard icon if 'edit-paste' is not found
        tray_icon = QSystemTrayIcon(QIcon.fromTheme('document-properties'), app)
    
    tray_icon.setToolTip("Clipboard Manager")
    
    # Create tray menu
    menu = QMenu()
    show_action = menu.addAction("Show History")
    show_action.triggered.connect(gui.show)
    quit_action = menu.addAction("Quit")
    quit_action.triggered.connect(app.quit)
    tray_icon.setContextMenu(menu)
    
    # Show window when clicking the tray icon
    tray_icon.activated.connect(
        lambda reason: gui.show() if reason == QSystemTrayIcon.ActivationReason.Trigger else None
    )
    
    tray_icon.show()
    
    # Center on screen
    screen_geometry = app.primaryScreen().geometry()
    x = (screen_geometry.width() - gui.width()) // 2
    y = (screen_geometry.height() - gui.height()) // 2
    gui.move(x, y)
    
    gui.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
