"""FastAPI application with all HTTP API endpoints, task manager, and middleware."""

from __future__ import annotations

import logging
import os
import threading
import time
import uuid
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, StreamingResponse

from api_models import (
    AppSettingsResponse,
    AppSettingsUpdateRequest,
    CancelResponse,
    DeleteTasksResponse,
    HealthResponse,
    OpenOutputRequest,
    OpenOutputResponse,
    ProcessFileByPathRequest,
    ProcessFileResponse,
    ProcessFolderRequest,
    ProcessFolderResponse,
    ShutdownResponse,
    TaskInfo,
    TaskListItem,
    TaskStatusResponse,
    TasksListResponse,
)
from api_worker import process_folder_task, process_single_file_to_bytes
from utils.config import ProcessingSettings

logger = logging.getLogger('api')
logger.setLevel(logging.INFO)
_fh = logging.FileHandler('api.log', encoding='utf-8')
_fh.setFormatter(logging.Formatter('%(asctime)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logger.addHandler(_fh)
logger.propagate = False


class TaskManager:
    """Thread-safe in-memory task storage and execution queue.

    Manages the lifecycle of processing tasks: creation, execution,
    cancellation, and cleanup. Only one folder processing task runs
    at a time.
    """

    def __init__(self) -> None:
        """Initialize an empty task manager."""
        self._tasks: dict[str, TaskInfo] = {}
        self._lock = threading.Lock()
        self._cancel_flags: dict[str, 'threading.Event'] = {}
        self._current_task_id: str | None = None
        self._worker_thread: threading.Thread | None = None

    def create_task(self, input_folder: str, output_folder: str, settings: dict | None = None) -> str:
        """Create a new processing task and return its ID.

        Args:
            input_folder: Path to the input folder.
            output_folder: Path to the output folder.
            settings: Optional processing settings dict.

        Returns:
            Unique task ID string.
        """
        task_id = uuid.uuid4().hex[:12]
        task = TaskInfo(
            id=task_id,
            status='queued',
            created_at=time.time(),
            input_folder=input_folder,
            output_folder=output_folder,
            settings=settings,
        )
        with self._lock:
            self._tasks[task_id] = task
            self._cancel_flags[task_id] = threading.Event()

        self._start_next()
        return task_id

    def get_task(self, task_id: str) -> TaskInfo | None:
        """Get task info by ID.

        Args:
            task_id: The task identifier.

        Returns:
            TaskInfo or None if not found.
        """
        with self._lock:
            return self._tasks.get(task_id)

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running or queued task.

        Args:
            task_id: The task identifier.

        Returns:
            True if the task was found and cancelled.
        """
        with self._lock:
            task = self._tasks.get(task_id)
            if task is None:
                return False
            if task.status in ('running', 'queued'):
                task.status = 'cancelled'
                task.finished_at = time.time()
                if task_id in self._cancel_flags:
                    self._cancel_flags[task_id].set()
                return True
            return False

    def list_tasks(self) -> list[TaskListItem]:
        """List all tasks currently in memory.

        Returns:
            List of task summary items.
        """
        with self._lock:
            return [
                TaskListItem(
                    task_id=t.id,
                    status=t.status,
                    progress=t.progress,
                    processed=t.processed,
                    total=t.total,
                    created_at=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t.created_at)),
                )
                for t in self._tasks.values()
            ]

    def clear_completed(self) -> int:
        """Delete completed, failed, or cancelled tasks.

        Returns:
            Number of tasks deleted.
        """
        with self._lock:
            to_delete = [
                tid for tid, t in self._tasks.items()
                if t.status in ('finished', 'failed', 'cancelled')
            ]
            for tid in to_delete:
                del self._tasks[tid]
                self._cancel_flags.pop(tid, None)
            return len(to_delete)

    def _start_next(self) -> None:
        """Start the next queued task if no task is currently running."""
        with self._lock:
            if self._worker_thread and self._worker_thread.is_alive():
                return
            for task in self._tasks.values():
                if task.status == 'queued':
                    task.status = 'running'
                    self._current_task_id = task.id
                    self._worker_thread = threading.Thread(
                        target=self._run_task,
                        args=(task,),
                        daemon=True,
                    )
                    self._worker_thread.start()
                    return

    def _run_task(self, task: TaskInfo) -> None:
        """Execute a processing task in a background thread.

        Args:
            task: The TaskInfo instance to process.
        """
        stop_event = self._cancel_flags.get(task.id, threading.Event())

        def progress_cb(processed, total, elapsed_s, eta_s, result):
            with self._lock:
                task.processed = processed
                task.total = total
                task.progress = (processed / total) * 100 if total > 0 else 0
                task.remaining_seconds = int(eta_s)
                fname = Path(result.input_path).name if result.input_path else '?'
                if result.success:
                    task.log.append(f'[OK] {fname}')
                else:
                    err = {'file': fname, 'error': result.error or 'unknown'}
                    task.errors.append(err)
                    task.log.append(f'[FAIL] {fname}: {result.error}')

        try:
            total, success, fail = process_folder_task(
                input_folder=task.input_folder,
                output_folder=task.output_folder,
                settings=_dict_to_settings(task.settings or {}),
                stop_event=stop_event,
                progress_callback=progress_cb,
            )
            task.images_found = total
            with self._lock:
                if task.status == 'cancelled':
                    return
                task.status = 'finished'
                task.progress = 100.0
                task.processed = total
                task.finished_at = time.time()
                task.log.append(f'Done: {success} OK, {fail} errors')
        except Exception as e:
            with self._lock:
                task.status = 'failed'
                task.finished_at = time.time()
                task.log.append(f'Task failed: {e}')
        finally:
            with self._lock:
                self._current_task_id = None
            self._start_next()


def _dict_to_settings(d: dict) -> ProcessingSettings:
    """Convert a settings dict to a ProcessingSettings dataclass.

    Args:
        d: Dictionary with optional processing settings keys.

    Returns:
        ProcessingSettings instance with values from the dict.
    """
    return ProcessingSettings(
        remove_bg=d.get('remove_bg', d.get('remove_background', True)),
        trim_edges=d.get('trim_edges', d.get('trim', True)),
        uniform_size=d.get('uniform_size', d.get('uniform_size', False)),
        target_width=d.get('target_width', 512),
        target_height=d.get('target_height', 512),
        center_object=d.get('center_object', False),
        overwrite_existing=d.get('overwrite_existing', d.get('overwrite', False)),
        preserve_structure=d.get('preserve_structure', d.get('save_structure', True)),
    )


def _settings_to_dict(s: ProcessingSettings) -> dict:
    """Convert ProcessingSettings to a dict for API responses."""
    return {
        'remove_background': s.remove_bg,
        'trim': s.trim_edges,
        'uniform_size': s.uniform_size,
        'target_width': s.target_width,
        'target_height': s.target_height,
        'center_object': s.center_object,
        'overwrite': s.overwrite_existing,
        'save_structure': s.preserve_structure,
        'format': 'png',
    }


# --- App State ---
task_manager = TaskManager()
_default_settings = ProcessingSettings()
_app_api_key: str | None = None


def get_api_key() -> str | None:
    """Get the current API key."""
    return _app_api_key


def set_api_key(value: str | None) -> None:
    """Set the API key for authentication."""
    global _app_api_key
    _app_api_key = value if value else None


# --- FastAPI App ---
app = FastAPI(
    title='Batch Image Processor API',
    version='1.0.0',
    description='HTTP API for batch image background removal and processing.',
    docs_url='/docs',
    redoc_url='/redoc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.middleware('http')
async def api_key_middleware(request: Request, call_next: Any) -> Any:
    """Check X-API-Key header if an API key is configured."""
    key = get_api_key()
    if key:
        if request.url.path in ('/health', '/docs', '/redoc', '/openapi.json'):
            pass
        else:
            client_key = request.headers.get('X-API-Key', '')
            if client_key != key:
                return JSONResponse(
                    status_code=401,
                    content={'detail': 'Invalid or missing API key'},
                )
    return await call_next(request)


@app.middleware('http')
async def logging_middleware(request: Request, call_next: Any) -> Any:
    """Log every request to api.log with timing."""
    t0 = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception as e:
        elapsed = int((time.perf_counter() - t0) * 1000)
        logger.info(
            f'{request.client.host if request.client else "?"} | '
            f'{request.method} {request.url.path} | 500 | {elapsed}ms | {e}'
        )
        raise
    elapsed = int((time.perf_counter() - t0) * 1000)
    logger.info(
        f'{request.client.host if request.client else "?"} | '
        f'{request.method} {request.url.path} | {response.status_code} | {elapsed}ms'
    )
    return response


# --- Endpoints ---


@app.get('/health', response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status='ok', version='1.0')


@app.post('/process-folder', response_model=ProcessFolderResponse)
async def process_folder(req: ProcessFolderRequest) -> ProcessFolderResponse:
    """Start batch processing of a folder.

    Creates an async task and returns immediately with a task_id.
    Use GET /task/{task_id} to track progress.
    """
    input_path = Path(req.input)
    output_path = Path(req.output) if req.output else input_path.parent / f'{input_path.name}_processed'

    if not input_path.exists():
        raise HTTPException(status_code=404, detail=f'Input folder not found: {req.input}')

    from utils.file_utils import find_images
    images = find_images(input_path)

    task_id = task_manager.create_task(
        str(input_path.resolve()),
        str(output_path.resolve()),
        _settings_to_dict(_default_settings),
    )

    return ProcessFolderResponse(
        success=True,
        images_found=len(images),
        task_id=task_id,
    )


@app.post('/process-file')
async def process_file_endpoint(request: Request):
    """Process a single image file.

    Accepts either multipart/form-data with a file field,
    or JSON with a path field.
    Returns PNG bytes or a JSON response.
    """
    content_type = request.headers.get('content-type', '')

    if 'multipart/form-data' in content_type:
        form = await request.form()
        file = form.get('file')
        if file is None:
            raise HTTPException(status_code=400, detail='No file field in form data')
        file_data = await file.read()
        result_bytes = process_single_file_to_bytes(
            file_data=file_data,
            settings=_default_settings,
        )
        if result_bytes is None:
            raise HTTPException(status_code=500, detail='Processing failed')
        return Response(
            content=result_bytes,
            media_type='image/png',
            headers={'Content-Disposition': f'attachment; filename="{file.filename}.png"'},
        )

    body = await request.json()
    req_path = body.get('path', '')
    output_path = body.get('output')

    file_path = Path(req_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f'File not found: {req_path}')

    if output_path:
        out = Path(output_path)
    else:
        out = file_path.parent / f'{file_path.stem}_processed.png'

    result_bytes = process_single_file_to_bytes(
        file_path=str(file_path),
        settings=_default_settings,
    )

    if result_bytes is None:
        return ProcessFileResponse(success=False, error='Processing failed')

    out.write_bytes(result_bytes)
    return ProcessFileResponse(success=True, output=str(out.resolve()))


@app.post('/process-file-upload')
async def process_file_upload(file: UploadFile = File(...)):
    """Process an uploaded image file and return PNG bytes."""
    file_data = await file.read()
    result_bytes = process_single_file_to_bytes(
        file_data=file_data,
        settings=_default_settings,
    )
    if result_bytes is None:
        raise HTTPException(status_code=500, detail='Processing failed')
    return Response(
        content=result_bytes,
        media_type='image/png',
        headers={'Content-Disposition': f'attachment; filename="{file.filename}.png"'},
    )


@app.get('/task/{task_id}', response_model=TaskStatusResponse)
async def get_task(task_id: str) -> TaskStatusResponse:
    """Get the status and progress of a processing task."""
    task = task_manager.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail='Task not found')

    return TaskStatusResponse(
        status=task.status,
        progress=round(task.progress, 1),
        processed=task.processed,
        total=task.total,
        errors=len(task.errors),
        remaining_seconds=task.remaining_seconds,
        images_found=task.images_found or task.total,
        input_folder=task.input_folder,
        output_folder=task.output_folder,
        created_at=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task.created_at)),
        finished_at=(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task.finished_at))
            if task.finished_at else None
        ),
        log=task.log[-50:],
    )


@app.post('/task/{task_id}/cancel', response_model=CancelResponse)
async def cancel_task(task_id: str) -> CancelResponse:
    """Cancel a running or queued processing task."""
    ok = task_manager.cancel_task(task_id)
    if not ok:
        raise HTTPException(status_code=404, detail='Task not found or already finished')
    return CancelResponse(success=True)


@app.get('/tasks', response_model=TasksListResponse)
async def list_tasks() -> TasksListResponse:
    """List all tasks in memory."""
    return TasksListResponse(tasks=task_manager.list_tasks())


@app.delete('/tasks', response_model=DeleteTasksResponse)
async def delete_tasks() -> DeleteTasksResponse:
    """Delete all completed, failed, or cancelled tasks."""
    deleted = task_manager.clear_completed()
    return DeleteTasksResponse(success=True, deleted=deleted)


@app.get('/settings', response_model=AppSettingsResponse)
async def get_settings() -> AppSettingsResponse:
    """Get current processing settings."""
    s = _default_settings
    return AppSettingsResponse(
        remove_background=s.remove_bg,
        trim=s.trim_edges,
        uniform_size=s.uniform_size,
        target_width=s.target_width,
        target_height=s.target_height,
        center_object=s.center_object,
        overwrite=s.overwrite_existing,
        save_structure=s.preserve_structure,
        format='png',
        api_key=get_api_key(),
    )


@app.post('/settings', response_model=AppSettingsResponse)
async def update_settings(req: AppSettingsUpdateRequest) -> AppSettingsResponse:
    """Update processing settings at runtime."""
    global _default_settings
    updates = req.model_dump(exclude_none=True)

    if 'remove_background' in updates:
        _default_settings.remove_bg = updates['remove_background']
    if 'trim' in updates:
        _default_settings.trim_edges = updates['trim']
    if 'uniform_size' in updates:
        _default_settings.uniform_size = updates['uniform_size']
    if 'target_width' in updates:
        _default_settings.target_width = updates['target_width']
    if 'target_height' in updates:
        _default_settings.target_height = updates['target_height']
    if 'center_object' in updates:
        _default_settings.center_object = updates['center_object']
    if 'overwrite' in updates:
        _default_settings.overwrite_existing = updates['overwrite']
    if 'save_structure' in updates:
        _default_settings.preserve_structure = updates['save_structure']
    if 'api_key' in updates:
        set_api_key(updates['api_key'])

    return await get_settings()


@app.post('/open-output', response_model=OpenOutputResponse)
async def open_output(req: OpenOutputRequest) -> OpenOutputResponse:
    """Open a folder in Windows Explorer."""
    folder = Path(req.path)
    if folder.exists():
        os.startfile(str(folder))
    elif folder.parent.exists():
        os.startfile(str(folder.parent))
    return OpenOutputResponse(success=True)


@app.post('/shutdown', response_model=ShutdownResponse)
async def shutdown() -> ShutdownResponse:
    """Shut down the HTTP server gracefully. GUI is not affected."""
    from api import request_shutdown
    request_shutdown()
    return ShutdownResponse(success=True, message='HTTP server shutting down')


def get_app() -> FastAPI:
    """Return the FastAPI application instance."""
    return app
