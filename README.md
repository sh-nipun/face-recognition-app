# Face Recognition App

A local face recognition web app built with FastAPI and `face_recognition` (dlib). Complete a guided, real-time liveness scan (head turns + blink, confirmed step by step like Face ID) through your webcam, and the app either recognizes you or asks for a name to save a new face.

## Features

- **Real-time guided liveness scan** — the app asks you to turn your head one way, then the other, then blink; each step is confirmed live as you do it (not on a blind timer), which helps prevent someone from spoofing the scan with a static photo
- Live camera capture, with a file-upload fallback when no camera is available (uploaded photos skip the liveness check since a static image can't blink)
- Automatic recognition — no separate "Register"/"Verify" buttons; a recognized face shows "Welcome back", an unrecognized one asks for a name to save
- Multiple reference photos per person for better match accuracy
- Adjustable match strictness (tolerance) slider
- Manage registered faces — list and remove people
- Animated, modern frontend (vanilla HTML/CSS/JS — no build step)
- Simple REST API with interactive docs (Swagger UI)

## How the liveness scan works

1. **Look straight** — the app records a short baseline (your neutral head position and eye-openness)
2. **Turn your head to the right** — confirmed instantly once the head-turn is detected and held briefly
3. **Return to center** — you must come back near the baseline position before the next step counts (stops a simple relax-back from being mistaken for a turn)
4. **Turn your head to the left** — confirmed once you turn to the opposite side of the baseline
5. **Blink** — confirmed once a genuine eyes-open → closed → open-again pattern is detected against your own baseline
6. Once all steps pass, the clearest straight-on frame is matched against everyone on file

This runs on repeated lightweight calls to a `/pose-check` endpoint (eye-openness + head-turn angle from face landmarks) — no extra ML models or heavy libraries needed.

## Tech stack

**Backend**
- Python
- FastAPI — API framework
- Uvicorn — ASGI server
- `face_recognition` (dlib) — face detection, face landmarks, and face encoding/embedding
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

| Method | Endpoint      | Description                                                        |
|--------|---------------|---------------------------------------------------------------------|
| POST   | `/pose-check` | Single-frame check — returns eye-openness (EAR) and head-turn offset, used to drive the live guided scan |
| POST   | `/register`   | Register a face under a given name (with duplicate-face warning)   |
| POST   | `/verify`     | Compare a face against all registered faces                        |
| GET    | `/list`       | List all registered people and how many photos each has            |
| DELETE | `/delete`     | Remove a registered person                                         |
| GET    | `/`           | Health check                                                        |

## Notes

- Registered faces are stored in memory only — they reset when the server restarts.
- This project is for learning/prototyping purposes and is not hardened for production use.
