"""Entry point for the Batch Image Processor application."""

from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from ui.main_window import MainWindow


def preload_rembg() -> None:
    """Preload rembg model in background to avoid first-run delay."""
    try:
        from threading import Thread
        def _load():
            try:
                from rembg import new_session
                new_session('u2net')
            except Exception:
                pass
        Thread(target=_load, daemon=True).start()
    except Exception:
        pass


def main() -> None:
    """Initialize and run the application."""
    app = QApplication(sys.argv)
    app.setApplicationName('Batch Image Processor')
    app.setApplicationVersion('1.0.0')
    app.setOrganizationName('GovnyakHelper')

    window = MainWindow()
    window.show()

    preload_rembg()

    sys.exit(app.exec())


if __name__ == '__main__':
    main()
