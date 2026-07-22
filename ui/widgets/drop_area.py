"""Drag & drop area widget for folder selection."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout


class DropArea(QFrame):
    """A framed area that accepts folder drag & drop.

    Emits a signal when a valid folder is dropped.
    """

    folder_dropped = Signal(str)

    def __init__(self, parent=None) -> None:
        """Initialize the drop area widget."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName('dropArea')
        self.setMinimumHeight(120)
        self.setFrameStyle(QFrame.StyledPanel)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self._icon_label = QLabel('\U0001F4C1')
        self._icon_label.setStyleSheet('font-size: 36px; padding: 0;')
        self._icon_label.setAlignment(Qt.AlignCenter)

        self._text_label = QLabel('Drag & Drop folder here')
        self._text_label.setAlignment(Qt.AlignCenter)
        self._text_label.setObjectName('dropText')
        self._text_label.setStyleSheet(
            'font-size: 14px; font-weight: 600; padding: 4px;'
        )

        layout.addWidget(self._icon_label)
        layout.addWidget(self._text_label)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter event - accept folder drops."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setProperty('dragOver', True)
            self.style().unpolish(self)
            self.style().polish(self)

    def dragLeaveEvent(self, event) -> None:
        """Handle drag leave event - reset visual state."""
        self.setProperty('dragOver', False)
        self.style().unpolish(self)
        self.style().polish(self)

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop event - extract folder path."""
        self.setProperty('dragOver', False)
        self.style().unpolish(self)
        self.style().polish(self)

        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if __import__('os').path.isdir(path):
                self.folder_dropped.emit(path)
                return
