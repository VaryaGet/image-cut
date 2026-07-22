"""Entry point for the Batch Image Processor application."""

from __future__ import annotations

import atexit
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

    from settings.app_settings import AppSettings
    settings = AppSettings()

    if settings.api_enabled:
        from api import start_api_server
        host = settings.api_host
        port = settings.api_port
        key = settings.api_key
        if key:
            from api_server import set_api_key
            set_api_key(key)
        started = start_api_server(host, port)
        if started:
            print(f'API server started at http://{host}:{port}')
            print(f'Swagger UI: http://{host}:{port}/docs')

    def shutdown_api():
        from api import stop_api_server
        stop_api_server()

    atexit.register(shutdown_api)

    window = MainWindow()
    window.show()

    preload_rembg()

    exit_code = app.exec()

    shutdown_api()

    sys.exit(exit_code)


if __name__ == '__main__':
    main()
