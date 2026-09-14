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

## Setup

1. Clone the repository
   ```bash
   git clone https://github.com/sh-nipun/face-recognition-app.git
   cd face-recognition-app
   ```

2. Create and activate a virtual environment
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

   > Note: `face_recognition` depends on `dlib`, which needs CMake and a C++ compiler (Visual Studio Build Tools on Windows) to build from source.

4. Run the backend
   ```bash
   uvicorn main:app --reload
   ```
   The API runs at `http://127.0.0.1:8000`. Interactive docs are available at `http://127.0.0.1:8000/docs`.

5. Open the frontend
   Open `index.html` with a local server (e.g. the VS Code "Live Server" extension) — opening it directly as a `file://` URL blocks camera access in most browsers.

## API

| Method | Endpoint    | Description                                  |
|--------|-------------|-----------------------------------------------|
| POST   | `/register` | Register a face under a given name           |
| POST   | `/verify`   | Compare a face against all registered faces  |
| GET    | `/`         | Health check                                  |

## Notes

- Registered faces are stored in memory only — they reset when the server restarts.
- This project is for learning/prototyping purposes and is not hardened for production use.
