"""Progress display widget with detailed statistics."""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QVBoxLayout,
    QWidget,
)


def _format_time(seconds: float) -> str:
    """Format seconds into a human-readable string.

    Args:
        seconds: Time in seconds.

    Returns:
        Formatted string like '1m 23s' or '45s'.
    """
    if seconds < 0:
        seconds = 0
    m, s = divmod(int(seconds), 60)
    if m > 0:
        return f'{m}m {s}s'
    return f'{s}s'


class ProgressWidget(QWidget):
    """Composite widget showing a progress bar with detailed statistics.

    Displays: processed count, total count, elapsed time, estimated time remaining.
    """

    def __init__(self, parent=None) -> None:
        """Initialize the progress widget."""
        super().__init__(parent)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self._progress_bar = QProgressBar()
        self._progress_bar.setValue(0)
        self._progress_bar.setFormat('Ready')

        stats_layout = QHBoxLayout()
        stats_layout.setContentsMargins(0, 0, 0, 0)

        self._processed_label = QLabel('Processed: 0 / 0')
        self._processed_label.setObjectName('folderLabel')
        self._time_label = QLabel('Elapsed: --')
        self._time_label.setObjectName('folderLabel')
        self._eta_label = QLabel('ETA: --')
        self._eta_label.setObjectName('folderLabel')

        stats_layout.addWidget(self._processed_label)
        stats_layout.addStretch()
        stats_layout.addWidget(self._time_label)
        stats_layout.addSpacing(12)
        stats_layout.addWidget(self._eta_label)

        layout.addWidget(self._progress_bar)
        layout.addLayout(stats_layout)

    def update_progress(self, processed: int, total: int, elapsed_s: float, eta_s: float) -> None:
        """Update all progress indicators.

        Args:
            processed: Number of images processed so far.
            total: Total number of images to process.
            elapsed_s: Elapsed time in seconds.
            eta_s: Estimated time remaining in seconds.
        """
        if total > 0:
            pct = int((processed / total) * 100)
            self._progress_bar.setValue(pct)
            self._progress_bar.setFormat(f'{processed}/{total} ({pct}%)')
        else:
            self._progress_bar.setValue(0)
            self._progress_bar.setFormat('0/0')

        self._processed_label.setText(f'Processed: {processed} / {total}')
        self._time_label.setText(f'Elapsed: {_format_time(elapsed_s)}')

        if processed >= total:
            self._eta_label.setText('ETA: Done!')
        elif processed > 0:
            self._eta_label.setText(f'ETA: {_format_time(eta_s)}')
        else:
            self._eta_label.setText('ETA: --')

    def reset(self) -> None:
        """Reset the progress display to initial state."""
        self._progress_bar.setValue(0)
        self._progress_bar.setFormat('Ready')
        self._processed_label.setText('Processed: 0 / 0')
        self._time_label.setText('Elapsed: --')
        self._eta_label.setText('ETA: --')

    def set_scan_result(self, total: int) -> None:
        """Update after scan completion, before processing starts.

        Args:
            total: Total number of images found.
        """
        self._processed_label.setText(f'Found: {total} image(s)')
        self._progress_bar.setFormat(f'0 / {total}')
