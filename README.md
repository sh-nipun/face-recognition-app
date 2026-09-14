# Face Recognition App

A local face recognition web app built with FastAPI and `face_recognition` (dlib). Register a face under a name through your webcam, then verify new scans against everyone on file.

## Features

- Live camera capture, with a file-upload fallback when no camera is available
- Face registration with named encodings
- Face verification with match confidence score
- Animated, modern frontend (vanilla HTML/CSS/JS — no build step)
- Simple REST API with interactive docs (Swagger UI)

## Tech stack

**Backend**
- Python
- FastAPI — API framework
- Uvicorn — ASGI server
- `face_recognition` (dlib) — face detection and face encoding/embedding
- OpenCV, Pillow, NumPy — image handling

**Frontend**
- HTML, CSS, JavaScript (no framework)
- Browser `getUserMedia` API for camera capture

## Project structure

```
face-recognition-app/
├── main.py            # FastAPI backend (register / verify endpoints)
├── index.html          # Frontend UI
├── requirements.txt    # Python dependencies
└── .gitignore
```

## First-time setup

1. Clone the repository
   ```bash
   git clone https://github.com/sh-nipun/face-recognition-app.git
   cd face-recognition-app
   ```

2. Create a virtual environment
   ```bash
   python -m venv venv
   ```

3. Install dependencies (after activating the environment — see step 3 under "How to run")
   ```bash
   pip install -r requirements.txt
   ```

   > Note: `face_recognition` depends on `dlib`, which needs CMake and a C++ compiler (Visual Studio Build Tools on Windows, with the "Desktop development with C++" workload) to build from source.

## How to run (every time)

Two things need to run at the same time: the **backend** (in a terminal) and the **frontend** (in a browser, via a local server).

### 1. Open the project in VS Code
Open the `face-recognition-app` folder in VS Code (`File → Open Folder`, or right-click the folder → "Open with Code").

### 2. Open a terminal
`Terminal → New Terminal`, or press `` Ctrl+` ``.

### 3. Activate the virtual environment
```bash
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```
If PowerShell blocks the script with a permission error, run this once first:
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
You'll know it worked when the prompt starts with `(venv)`.

### 4. Start the backend server
```bash
uvicorn main:app --reload
```
Wait for `Application startup complete` in the terminal. **Leave this terminal running** — closing it stops the API.

The API is now live at `http://127.0.0.1:8000`, with interactive docs at `http://127.0.0.1:8000/docs`.

### 5. Open the frontend
In VS Code's Explorer, right-click `index.html` → **"Open with Live Server"** (requires the free "Live Server" VS Code extension).

This opens the app in your browser at a `http://127.0.0.1:5500/...` address. Opening `index.html` directly as a `file://` path will block camera access — Live Server (or any local HTTP server) is required for the camera to work.

> No camera on your machine? The app automatically falls back to a "Choose photo" upload button instead.

### To stop everything
Press `Ctrl+C` in the backend terminal, and close the browser tab.

## API

| Method | Endpoint    | Description                                  |
|--------|-------------|-----------------------------------------------|
| POST   | `/register` | Register a face under a given name           |
| POST   | `/verify`   | Compare a face against all registered faces  |
| GET    | `/`         | Health check                                  |

## Notes

- Registered faces are stored in memory only — they reset when the server restarts.
- This project is for learning/prototyping purposes and is not hardened for production use.
