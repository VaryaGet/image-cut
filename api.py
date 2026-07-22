"""HTTP API server lifecycle management.

Starts uvicorn in a separate daemon thread so the GUI never blocks.
Provides clean shutdown via a threading.Event.
"""

from __future__ import annotations

import threading
import time

import uvicorn


class _ApiServerState:
    """Internal state for the API server thread."""

    def __init__(self) -> None:
        self._server: uvicorn.Server | None = None
        self._thread: threading.Thread | None = None
        self._shutdown_requested = threading.Event()
        self._host = '127.0.0.1'
        self._port = 8080
        self._running = False

    @property
    def is_running(self) -> bool:
        """Check if the server is currently running."""
        return self._running

    def start(self, host: str = '127.0.0.1', port: int = 8080) -> None:
        """Start the HTTP API server in a background daemon thread.

        Args:
            host: Host address to bind to.
            port: Port to listen on.
        """
        if self._running:
            return

        self._host = host
        self._port = port
        self._shutdown_requested.clear()

        config = uvicorn.Config(
            'api_server:app',
            host=host,
            port=port,
            log_level='warning',
            loop='asyncio',
        )
        self._server = uvicorn.Server(config)

        self._thread = threading.Thread(target=self._run_server, daemon=True)
        self._thread.start()
        self._running = True

    def _run_server(self) -> None:
        """Internal method: runs the uvicorn server loop."""
        if self._server:
            self._server.run()

    def stop(self) -> None:
        """Request server shutdown and wait for it to exit."""
        if not self._running:
            return

        self._shutdown_requested.set()

        if self._server:
            self._server.should_exit = True

        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=3)

        self._running = False


_state = _ApiServerState()


def start_api_server(host: str = '127.0.0.1', port: int = 8080) -> bool:
    """Start the HTTP API server.

    Args:
        host: Host address to bind to.
        port: Port to listen on.

    Returns:
        True if the server started successfully.
    """
    try:
        from api_server import app
        _state.start(host, port)
        return True
    except Exception as e:
        print(f'Failed to start API server: {e}')
        return False


def stop_api_server() -> None:
    """Stop the HTTP API server and wait for it to exit."""
    _state.stop()


def request_shutdown() -> None:
    """Set the shutdown flag (called from /shutdown endpoint)."""
    _state._shutdown_requested.set()
    if _state._server:
        _state._server.should_exit = True


def is_api_running() -> bool:
    """Check if the API server is currently running."""
    return _state.is_running
