"""Main application window for the batch image processor."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from ui.styles import DARK_THEME, LIGHT_THEME
from ui.widgets.drop_area import DropArea
from ui.widgets.log_widget import LogWidget
from ui.widgets.progress_widget import ProgressWidget
from utils.config import ProcessingSettings
from workers.processor import ProcessingWorker


class MainWindow(QMainWindow):
    """Main application window.

    Provides the full UI for selecting input/output folders,
    configuring processing options, starting/stopping batch processing,
    and viewing progress and logs.
    """

    def __init__(self) -> None:
        """Initialize the main window and all UI components."""
        super().__init__()
        self.setWindowTitle('Batch Image Processor')
        self.setMinimumSize(760, 620)
        self.resize(820, 720)

        self._settings = ProcessingSettings()
        self._input_folder: Path | None = None
        self._output_folder: Path | None = None
        self._worker: ProcessingWorker | None = None
        self._theme = 'dark'

        self._init_ui()
        self._apply_theme()

    def _init_ui(self) -> None:
        """Build the complete user interface."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(12)

        # --- Title bar ---
        title_bar = QHBoxLayout()
        title = QLabel('Batch Image Processor')
        title.setObjectName('titleLabel')
        title_bar.addWidget(title)
        title_bar.addStretch()

        self._theme_btn = QPushButton('\u263C')
        self._theme_btn.setObjectName('secondaryButton')
        self._theme_btn.setFixedSize(36, 36)
        self._theme_btn.setToolTip('Toggle light/dark theme')
        self._theme_btn.clicked.connect(self._toggle_theme)
        title_bar.addWidget(self._theme_btn)
        main_layout.addLayout(title_bar)

        # --- Folder selection ---
        self._drop_area = DropArea()
        self._drop_area.folder_dropped.connect(self._on_folder_selected)
        main_layout.addWidget(self._drop_area)

        folder_row = QHBoxLayout()
        self._folder_label = QLabel('No folder selected')
        self._folder_label.setObjectName('folderLabel')
        self._folder_label.setWordWrap(True)
        folder_row.addWidget(self._folder_label, 1)

        self._select_btn = QPushButton('Select Folder')
        self._select_btn.setObjectName('secondaryButton')
        self._select_btn.clicked.connect(self._browse_folder)
        folder_row.addWidget(self._select_btn)
        main_layout.addLayout(folder_row)

        # --- Settings ---
        settings_group = QGroupBox('Processing Options')
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(6)

        self._remove_bg_cb = QCheckBox('Remove background (rembg)')
        self._remove_bg_cb.setChecked(self._settings.remove_bg)
        self._remove_bg_cb.toggled.connect(self._on_setting_changed)
        settings_layout.addWidget(self._remove_bg_cb)

        self._trim_edges_cb = QCheckBox('Trim transparent edges')
        self._trim_edges_cb.setChecked(self._settings.trim_edges)
        self._trim_edges_cb.toggled.connect(self._on_setting_changed)
        settings_layout.addWidget(self._trim_edges_cb)

        uniform_row = QHBoxLayout()
        self._uniform_size_cb = QCheckBox('Resize all to uniform size')
        self._uniform_size_cb.setChecked(self._settings.uniform_size)
        self._uniform_size_cb.toggled.connect(self._on_uniform_toggled)
        uniform_row.addWidget(self._uniform_size_cb)

        self._width_spin = QSpinBox()
        self._width_spin.setRange(32, 8192)
        self._width_spin.setValue(self._settings.target_width)
        self._width_spin.setSuffix(' px')
        self._width_spin.setEnabled(self._uniform_size_cb.isChecked())
        uniform_row.addWidget(QLabel('W:'))
        uniform_row.addWidget(self._width_spin)

        self._height_spin = QSpinBox()
        self._height_spin.setRange(32, 8192)
        self._height_spin.setValue(self._settings.target_height)
        self._height_spin.setSuffix(' px')
        self._height_spin.setEnabled(self._uniform_size_cb.isChecked())
        uniform_row.addWidget(QLabel('H:'))
        uniform_row.addWidget(self._height_spin)
        uniform_row.addStretch()
        settings_layout.addLayout(uniform_row)

        self._center_cb = QCheckBox('Center object on canvas')
        self._center_cb.setChecked(self._settings.center_object)
        self._center_cb.setEnabled(self._uniform_size_cb.isChecked())
        self._center_cb.toggled.connect(self._on_setting_changed)
        settings_layout.addWidget(self._center_cb)

        settings_layout.addSpacing(4)

        self._overwrite_cb = QCheckBox('Overwrite existing files')
        self._overwrite_cb.setChecked(self._settings.overwrite_existing)
        self._overwrite_cb.toggled.connect(self._on_setting_changed)
        settings_layout.addWidget(self._overwrite_cb)

        self._preserve_structure_cb = QCheckBox('Preserve folder structure')
        self._preserve_structure_cb.setChecked(self._settings.preserve_structure)
        self._preserve_structure_cb.toggled.connect(self._on_setting_changed)
        settings_layout.addWidget(self._preserve_structure_cb)

        main_layout.addWidget(settings_group)

        # --- Progress ---
        self._progress_widget = ProgressWidget()
        main_layout.addWidget(self._progress_widget)

        # --- Log ---
        self._log_widget = LogWidget()
        self._log_widget.setMinimumHeight(140)
        main_layout.addWidget(self._log_widget, 1)

        # --- Action buttons ---
        btn_row = QHBoxLayout()
        self._start_btn = QPushButton('Start Processing')
        self._start_btn.setMinimumHeight(36)
        self._start_btn.clicked.connect(self._start_processing)
        btn_row.addWidget(self._start_btn)

        self._stop_btn = QPushButton('Stop')
        self._stop_btn.setObjectName('dangerButton')
        self._stop_btn.setMinimumHeight(36)
        self._stop_btn.setEnabled(False)
        self._stop_btn.clicked.connect(self._stop_processing)
        btn_row.addWidget(self._stop_btn)

        self._open_output_btn = QPushButton('Open Output')
        self._open_output_btn.setObjectName('secondaryButton')
        self._open_output_btn.setMinimumHeight(36)
        self._open_output_btn.clicked.connect(self._open_output_folder)
        self._open_output_btn.setEnabled(False)
        btn_row.addWidget(self._open_output_btn)
        main_layout.addLayout(btn_row)

        # --- Status bar ---
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_bar.showMessage('Ready')

    def _browse_folder(self) -> None:
        """Open a folder selection dialog."""
        start_dir = str(self._input_folder) if self._input_folder else ''
        folder = QFileDialog.getExistingDirectory(
            self, 'Select Input Folder', start_dir,
        )
        if folder:
            self._on_folder_selected(folder)

    def _on_folder_selected(self, folder_path: str) -> None:
        """Handle folder selection from dialog or drag & drop.

        Args:
            folder_path: Path to the selected folder.
        """
        path = Path(folder_path).resolve()
        if path.is_dir():
            self._input_folder = path
            self._output_folder = path.parent / f'{path.name}_processed'
            self._folder_label.setText(str(path))
            self._log_widget.add_entry('', f'Selected folder: {path}', 'info')
            self._log_widget.add_entry(
                '', f'Output folder: {self._output_folder}', 'info',
            )
            self._open_output_btn.setEnabled(True)

    def _on_uniform_toggled(self, checked: bool) -> None:
        """Enable or disable size-related controls based on uniform size checkbox.

        Args:
            checked: Whether uniform resizing is enabled.
        """
        self._width_spin.setEnabled(checked)
        self._height_spin.setEnabled(checked)
        self._center_cb.setEnabled(checked)
        self._on_setting_changed()

    def _on_setting_changed(self) -> None:
        """Sync internal settings from UI controls."""
        self._settings.remove_bg = self._remove_bg_cb.isChecked()
        self._settings.trim_edges = self._trim_edges_cb.isChecked()
        self._settings.uniform_size = self._uniform_size_cb.isChecked()
        self._settings.target_width = self._width_spin.value()
        self._settings.target_height = self._height_spin.value()
        self._settings.center_object = self._center_cb.isChecked()
        self._settings.overwrite_existing = self._overwrite_cb.isChecked()
        self._settings.preserve_structure = self._preserve_structure_cb.isChecked()

    def _start_processing(self) -> None:
        """Start the batch processing operation."""
        if not self._input_folder or not self._input_folder.exists():
            self._log_widget.add_entry('', 'Please select a valid input folder', 'error')
            return

        self._on_setting_changed()

        self._start_btn.setEnabled(False)
        self._select_btn.setEnabled(False)
        self._stop_btn.setEnabled(True)
        self._progress_widget.reset()
        self._log_widget.clear_log()
        self._status_bar.showMessage('Processing...')

        output_folder = self._output_folder or (self._input_folder.parent / f'{self._input_folder.name}_processed')

        self._worker = ProcessingWorker()
        self._worker.configure(
            str(self._input_folder),
            str(output_folder),
            self._settings,
        )
        self._worker.log_message.connect(self._log_widget.add_entry)
        self._worker.scan_complete.connect(self._progress_widget.set_scan_result)
        self._worker.progress_updated.connect(self._progress_widget.update_progress)
        self._worker.processing_finished.connect(self._on_processing_finished)
        self._worker.stopped.connect(self._on_processing_stopped)
        self._worker.finished.connect(self._worker_cleanup)
        self._worker.start()

    def _stop_processing(self) -> None:
        """Stop the running batch process."""
        if self._worker and self._worker.isRunning():
            self._stop_btn.setEnabled(False)
            self._stop_btn.setText('Stopping...')
            self._status_bar.showMessage('Stopping...')
            self._worker.stop()

    def _on_processing_finished(self, success: int, failed: int) -> None:
        """Handle completion of batch processing.

        Args:
            success: Number of successfully processed images.
            failed: Number of failed images.
        """
        self._start_btn.setEnabled(True)
        self._select_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._stop_btn.setText('Stop')
        self._status_bar.showMessage(
            f'Done! {success} succeeded, {failed} failed',
        )

    def _on_processing_stopped(self) -> None:
        """Handle user-requested stop."""
        self._start_btn.setEnabled(True)
        self._select_btn.setEnabled(True)
        self._stop_btn.setEnabled(False)
        self._stop_btn.setText('Stop')
        self._status_bar.showMessage('Stopped by user')

    def _worker_cleanup(self) -> None:
        """Clean up worker resources after thread exits."""
        if self._worker:
            self._worker.deleteLater()
            self._worker = None

    def _open_output_folder(self) -> None:
        """Open the output folder in the system file explorer."""
        if self._output_folder and self._output_folder.exists():
            __import__('os').startfile(str(self._output_folder))
        elif self._output_folder:
            __import__('os').startfile(str(self._output_folder.parent))

    def _toggle_theme(self) -> None:
        """Switch between light and dark themes."""
        self._theme = 'light' if self._theme == 'dark' else 'dark'
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Apply the current theme stylesheet."""
        if self._theme == 'dark':
            self.setStyleSheet(DARK_THEME)
        else:
            self.setStyleSheet(LIGHT_THEME)

    def closeEvent(self, event) -> None:
        """Handle window close - ensure worker is stopped.

        Args:
            event: The close event.
        """
        if self._worker and self._worker.isRunning():
            self._worker.stop()
            self._worker.wait(5000)
        super().closeEvent(event)
