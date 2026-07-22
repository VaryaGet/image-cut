# Batch Image Processor

Desktop application for batch image background removal and transparent edge trimming. Built with PySide6 and FastAPI.

## Features

- **Background removal** using `rembg` (ONNX runtime, fully local)
- **Transparent edge trimming** via alpha channel
- **Uniform resize** with aspect ratio preservation and centering
- **Batch processing** — recursive folder scanning, preserves folder structure
- **Multi-threaded** — uses all CPU cores via `ThreadPoolExecutor`
- **Dark / light theme**
- **Drag & Drop** folder selection
- **HTTP API** with 12 endpoints and Swagger UI

## Supported Formats

`.png` `.jpg` `.jpeg` `.webp` `.bmp` `.tiff`

Output is always **PNG** with alpha channel.

## Installation

```powershell
pip install -r requirements.txt
```

## Usage

### GUI

```powershell
python main.py
```

1. Drag & drop a folder onto the drop area, or click **Select Folder**
2. Configure processing options:
   - Remove background
   - Trim transparent edges
   - Resize all to uniform size (with centering)
   - Overwrite existing files
   - Preserve folder structure
3. Click **Start Processing**
4. Results are saved to `YourFolder_processed/`

### HTTP API

The API starts automatically alongside the GUI on `http://127.0.0.1:8080`.

**Swagger UI:** `http://127.0.0.1:8080/docs`

```
# Health check
GET http://127.0.0.1:8080/health

# Start batch processing
POST http://127.0.0.1:8080/process-folder
Content-Type: application/json
{"input": "D:/Images", "output": "D:/Result"}

# Check task progress
GET http://127.0.0.1:8080/task/{task_id}

# Process single file (multipart)
POST http://127.0.0.1:8080/process-file
Content-Type: multipart/form-data
file: image.png

# Process single file (by path)
POST http://127.0.0.1:8080/process-file
Content-Type: application/json
{"path": "D:/image.jpg"}

# Cancel task
POST http://127.0.0.1:8080/task/{task_id}/cancel

# Get all tasks
GET http://127.0.0.1:8080/tasks

# Delete completed tasks
DELETE http://127.0.0.1:8080/tasks

# Get/update settings
GET http://127.0.0.1:8080/settings
POST http://127.0.0.1:8080/settings
Content-Type: application/json
{"remove_background": true, "trim": false}

# Open output folder in Explorer
POST http://127.0.0.1:8080/open-output
Content-Type: application/json
{"path": "D:/Result"}

# Shut down HTTP server (GUI stays open)
POST http://127.0.0.1:8080/shutdown
```

### API Key (optional)

Set via settings:
```json
POST /settings
{"api_key": "my-secret-key"}
```

All requests (except `/health`, `/docs`) must then include:
```
X-API-Key: my-secret-key
```

## API Logging

All requests are logged to `api.log`:
```
2026-01-22 14:30:15 | 127.0.0.1 | POST /process-folder | 200 | 45ms
2026-01-22 14:30:16 | 127.0.0.1 | GET /health | 200 | 2ms
```

## Project Structure

```
├── main.py                         # Entry point (GUI + API)
├── api.py                          # Uvicorn server lifecycle
├── api_models.py                   # Pydantic request/response schemas
├── api_server.py                   # FastAPI app, TaskManager, endpoints
├── api_worker.py                   # API-side image processing
├── requirements.txt
├── build.bat                       # PyInstaller single-exe build
├── ui/
│   ├── main_window.py              # Main GUI window
│   ├── styles.py                   # Light & dark QSS themes
│   └── widgets/
│       ├── drop_area.py            # Drag & drop area
│       ├── log_widget.py           # Color-coded log
│       └── progress_widget.py      # Progress with ETA stats
├── workers/
│   └── processor.py                # QThread worker for GUI
├── image_processing/
│   ├── bg_remover.py               # Background removal (rembg)
│   ├── trimmer.py                  # Transparent edge trimming
│   ├── resizer.py                  # Uniform resize with aspect ratio
│   └── plugin_base.py              # Plugin system for extensibility
├── utils/
│   ├── config.py                   # ProcessingSettings, ProcessingResult
│   └── file_utils.py               # Image discovery, path building
├── settings/
│   └── app_settings.py             # QSettings persistence
└── resources/                      # Static assets placeholder
```

## Build (single .exe)

```powershell
.\build.bat
```

Output: `dist\BatchImageProcessor.exe`

## Requirements

- Python 3.12+
- PySide6
- Pillow
- rembg
- onnxruntime
- FastAPI
- uvicorn
- python-multipart
