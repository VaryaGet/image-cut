"""Pydantic models for HTTP API request and response schemas."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Response for /health endpoint."""
    status: str = 'ok'
    version: str = '1.0'


class ProcessFolderRequest(BaseModel):
    """Request body for POST /process-folder."""
    input: str = Field(..., description='Path to input folder')
    output: str = Field(..., description='Path to output folder')


class ProcessFolderResponse(BaseModel):
    """Response for POST /process-folder."""
    success: bool = True
    images_found: int = 0
    task_id: str = ''


class ProcessFileByPathRequest(BaseModel):
    """Request body for POST /process-file with a file path."""
    path: str = Field(..., description='Path to the image file')
    output: str | None = Field(None, description='Optional output path')


class ProcessFileResponse(BaseModel):
    """Response for POST /process-file (path variant)."""
    success: bool = True
    output: str | None = None
    error: str | None = None


class TaskStatusResponse(BaseModel):
    """Response for GET /task/{task_id}."""
    status: str = 'unknown'
    progress: float = 0.0
    processed: int = 0
    total: int = 0
    errors: int = 0
    remaining_seconds: int = 0
    images_found: int = 0
    input_folder: str = ''
    output_folder: str = ''
    created_at: str = ''
    finished_at: str | None = None
    log: list[str] = Field(default_factory=list)


class TaskListItem(BaseModel):
    """Summary item for GET /tasks listing."""
    task_id: str
    status: str
    progress: float
    processed: int
    total: int
    created_at: str


class TasksListResponse(BaseModel):
    """Response for GET /tasks."""
    tasks: list[TaskListItem]


class CancelResponse(BaseModel):
    """Response for POST /task/{task_id}/cancel."""
    success: bool = True


class DeleteTasksResponse(BaseModel):
    """Response for DELETE /tasks."""
    success: bool = True
    deleted: int = 0


class AppSettingsResponse(BaseModel):
    """Response for GET /settings."""
    remove_background: bool = True
    trim: bool = True
    uniform_size: bool = False
    target_width: int = 512
    target_height: int = 512
    center_object: bool = False
    overwrite: bool = False
    save_structure: bool = True
    format: str = 'png'
    api_port: int = 8080
    api_key: str | None = None


class AppSettingsUpdateRequest(BaseModel):
    """Request body for POST /settings."""
    remove_background: bool | None = None
    trim: bool | None = None
    uniform_size: bool | None = None
    target_width: int | None = None
    target_height: int | None = None
    center_object: bool | None = None
    overwrite: bool | None = None
    save_structure: bool | None = None
    format: str | None = None
    api_port: int | None = None
    api_key: str | None = None


class OpenOutputRequest(BaseModel):
    """Request body for POST /open-output."""
    path: str = Field(..., description='Path to open in Explorer')


class OpenOutputResponse(BaseModel):
    """Response for POST /open-output."""
    success: bool = True


class ShutdownResponse(BaseModel):
    """Response for POST /shutdown."""
    success: bool = True
    message: str = 'HTTP server shutting down'


@dataclass
class TaskInfo:
    """In-memory task representation for internal use."""
    id: str
    status: str = 'queued'
    created_at: float = 0.0
    finished_at: float | None = None
    images_found: int = 0
    processed: int = 0
    total: int = 0
    errors: list[dict] = field(default_factory=list)
    progress: float = 0.0
    log: list[str] = field(default_factory=list)
    input_folder: str = ''
    output_folder: str = ''
    settings: dict | None = None
    remaining_seconds: int = 0
