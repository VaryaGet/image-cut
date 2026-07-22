"""Log display widget with colored entries."""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QTextEdit


class LogWidget(QTextEdit):
    """Read-only text area for displaying processing log entries.

    Supports color-coded messages: success (green), error (red), info (default).
    """

    def __init__(self, parent=None) -> None:
        """Initialize the log widget."""
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText('Processing log will appear here...')
        self._max_entries = 5000

    def add_entry(self, filename: str, message: str, level: str = 'info') -> None:
        """Append a colored log entry.

        Args:
            filename: Name of the file being processed (or empty for system messages).
            message: The log message text.
            level: Message level - 'success', 'error', or 'info'.
        """
        fmt = QTextCharFormat()

        if level == 'success':
            fmt.setForeground(QColor('#2ECC71'))
        elif level == 'error':
            fmt.setForeground(QColor('#E74C3C'))
        else:
            fmt.setForeground(QColor('#B0B4CC') if self._is_dark() else QColor('#6C757D'))

        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)

        if filename:
            name_fmt = QTextCharFormat()
            name_fmt.setForeground(QColor('#E4E6F0') if self._is_dark() else QColor('#212529'))
            name_fmt.setFontWeight(700)
            cursor.insertText(f'{filename} ', name_fmt)

        cursor.insertText(f'{message}\n', fmt)

        self._trim_entries()
        self._scroll_to_bottom()

    def clear_log(self) -> None:
        """Clear all log entries."""
        self.clear()

    def _is_dark(self) -> bool:
        """Detect if dark theme is active based on parent background."""
        try:
            bg = self.palette().color(self.backgroundRole())
            return bg.lightnessF() < 0.5
        except Exception:
            return False

    def _trim_entries(self) -> None:
        """Remove old entries if the log grows too large."""
        doc = self.document()
        if doc.blockCount() > self._max_entries:
            block = doc.begin()
            for _ in range(doc.blockCount() - self._max_entries):
                cursor = QTextCursor(block)
                cursor.select(QTextCursor.BlockUnderCursor)
                cursor.removeSelectedText()
                cursor.deleteChar()
                block = block.next()

    def _scroll_to_bottom(self) -> None:
        """Scroll the view to the bottom of the log."""
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())
