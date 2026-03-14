import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QClipboard
import db

class ClipboardDaemon:
    def __init__(self, app):
        self.app = app
        self.clipboard = app.clipboard()
        self.clipboard.dataChanged.connect(self.on_clipboard_change)
        
        # Store initial value
        text = self.clipboard.text()
        if text:
            db.add_item(text)

    def on_clipboard_change(self):
        text = self.clipboard.text()
        if text:
            db.add_item(text)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # Initialize DB before starting
    db.init_db()
    
    daemon = ClipboardDaemon(app)
    print("Clipboard daemon started.")
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
