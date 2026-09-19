# Face Recognition App

A face recognition web app that runs entirely on your own computer — no cloud, no external services, nothing sent over the internet. You look into your webcam, the app guides you through a quick liveness check (turn your head, blink), and it then either recognizes you ("Welcome back") or asks you to save your face under a name.

This README assumes **no prior coding experience**. Every step is spelled out — just follow along in order.

---

## Table of contents

1. [What this app actually does](#what-this-app-actually-does)
2. [How the liveness scan works](#how-the-liveness-scan-works)
3. [What you need before starting](#what-you-need-before-starting)
4. [Step-by-step: setting everything up (do this once)](#step-by-step-setting-everything-up-do-this-once)
5. [Running the app (do this every time)](#running-the-app-do-this-every-time)
6. [How to use the app](#how-to-use-the-app)
7. [Project files explained](#project-files-explained)
8. [API reference](#api-reference)
9. [Troubleshooting](#troubleshooting)
10. [Notes and limitations](#notes-and-limitations)

---

## What this app actually does

There are two halves working together:

- **The backend** (`main.py`) — a small Python program that does the actual face-recognition work. It reads images, figures out who's in them, and remembers who's been registered. It runs quietly in a terminal window.
- **The frontend** (`index.html`) — the page you actually see and click around in, opened in your browser. It turns on your webcam and talks to the backend behind the scenes.

Both need to be running **at the same time** for the app to work — think of the backend as the "brain" and the frontend as the "face" of the app.

---

## How the liveness scan works

Instead of a plain "take a photo and check it" flow, this app runs a short guided sequence — similar in spirit to how phone face-unlock works — so that a printed photo or a photo held up to the camera can't easily fool it:

1. **Look straight at the camera** — the app quietly records your normal, neutral position for about a second.
2. **Turn your head to the right** — the app is watching in real time; the moment it detects a clear turn, it confirms this step and moves on (no waiting for a timer).
3. **Return to center** — you're asked to come back to a neutral position before the next check starts. This stops "just relaxing back" from the previous step being mistaken for a second, separate motion.
4. **Turn your head to the left** — confirmed once you clearly turn to the opposite side.
5. **Blink** — confirmed once the app sees your eyes genuinely go from open → closed → open again.
6. Once every step passes, the clearest frame from step 1 is compared against everyone already registered.

If you're recognized, you'll see a "Welcome back" message with a confidence score. If you're not recognized, a small box appears asking for a name — type it in and it's saved for next time.

If any step doesn't complete in time, the scan stops and tells you exactly which part it couldn't confirm (e.g. "blink not detected"), so you know what to do differently on your next attempt.

> If your computer has no webcam, the app automatically switches to a "Choose photo" button instead. Uploaded photos skip the liveness steps (since a still image obviously can't blink) and go straight to recognition.

---

## What you need before starting

Install these first if you don't already have them. Each one only needs to be installed once.

| Tool | What it's for | Where to get it |
|---|---|---|
| **Python 3.10+** | Runs the backend | [python.org/downloads](https://www.python.org/downloads/) |
| **Visual Studio Code** | Where you'll write/run everything | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Git** | Used to download/update this project | [git-scm.com/downloads](https://git-scm.com/downloads) |
| **Live Server** (VS Code extension) | Lets your browser open the app properly (camera access needs this) | Install from inside VS Code — see step 6 below |
| **Visual Studio Build Tools** (Windows only) | Needed to install the face-recognition library | [visualstudio.microsoft.com/visual-cpp-build-tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) |

**When installing Python:** on the first screen of the installer, tick the box that says **"Add Python to PATH"** — this is easy to miss and causes problems later if skipped.

**When installing Visual Studio Build Tools (Windows only):** in the installer, tick **"Desktop development with C++"** and click Install. This step can take 10–15 minutes and needs a few GB of space — that's normal.

---

## Step-by-step: setting everything up (do this once)

### 1. Download the project
Open a terminal (Command Prompt on Windows) and run:
```bash
git clone https://github.com/sh-nipun/face-recognition-app.git
cd face-recognition-app
```
This downloads the project into a new `face-recognition-app` folder and moves you into it.

### 2. Open it in VS Code
```bash
code .
```
Or open VS Code manually and use **File → Open Folder** to select the `face-recognition-app` folder.

### 3. Open a terminal inside VS Code
Go to the menu **Terminal → New Terminal** (or press `` Ctrl+` ``, the backtick key, usually above Tab).

### 4. Create a virtual environment
A virtual environment keeps this project's Python packages separate from everything else on your computer.
```bash
python -m venv venv
```

### 5. Activate the virtual environment
```bash
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```
If Windows PowerShell shows a permission/security error, run this once first, then try activating again:
```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```
You'll know it worked when your terminal prompt starts with `(venv)`.

### 6. Install the Live Server extension
In VS Code, click the Extensions icon in the left sidebar (or press `Ctrl+Shift+X`), search for **"Live Server"** (by Ritwick Dey), and click Install.

### 7. Install the project's dependencies
With `(venv)` still showing in your terminal, run:
```bash
pip install -r requirements.txt
```
This installs everything the backend needs. It can take a few minutes — one of the packages (`dlib`) has to compile, so don't worry if it seems to hang for a bit.

> **If this step fails with an error mentioning "Microsoft Visual C++" or "CMake":** it means the Visual Studio Build Tools from the prerequisites table above aren't installed yet (or the "Desktop development with C++" option wasn't selected). Install that, restart your computer, then run the `pip install` command again.

Setup is done — you won't need to repeat any of this next time, only the steps in the next section.

---

## Running the app (do this every time)

Two things run side by side: the backend in a terminal, and the frontend in your browser.

### 1. Open the project and a terminal
Open the `face-recognition-app` folder in VS Code, then open a terminal (`` Ctrl+` ``).

### 2. Activate the virtual environment
```bash
venv\Scripts\activate        # Windows
source venv/bin/activate     # macOS/Linux
```
Confirm `(venv)` appears at the start of the prompt.

### 3. Start the backend
```bash
uvicorn main:app --reload
```
Wait until you see:
```
INFO:     Application startup complete.
```
**Leave this terminal open and running** the entire time you're using the app — closing it shuts down the backend.

### 4. Open the frontend
In the VS Code file explorer (left side), right-click **`index.html`** and choose **"Open with Live Server"**. Your browser opens automatically at an address like `http://127.0.0.1:5500/index.html`.

> Don't just double-click `index.html` to open it — opening it directly (as a `file://` link) blocks camera access in most browsers. It has to be opened through Live Server (or any local web server).

### 5. Allow camera access
Your browser will ask for camera permission — click **Allow**.

### To stop everything
In the backend terminal, press `Ctrl+C`. Close the browser tab. Next time, just repeat steps 1–5 above.

---

## How to use the app

1. Once the camera preview appears and the status line says **"Camera ready"**, click **Start Scan**.
2. Follow the on-screen prompts exactly as they appear — look straight, turn right, return to center, turn left, blink. Each instruction shows live feedback so you can tell how close you are to completing it.
3. When the scan finishes:
   - **If you're already registered** → you'll see "Welcome back, [name]" with a confidence percentage.
   - **If you're new** → a box appears asking for your name. Type it and press **Save** (or hit Enter).
4. You can adjust the **Match strictness** slider if verification feels too strict or too lenient.
5. Scroll down to **Registered Faces** to see everyone saved so far, and remove anyone with the **Remove** button.
6. **Recent Scans** keeps a short running log of the latest activity.

---

## Project files explained

```
face-recognition-app/
├── main.py            # Backend — the API server that does face recognition
├── index.html          # Frontend — the page you open in your browser
├── requirements.txt    # List of Python packages the backend needs
├── .gitignore          # Tells Git which files/folders to ignore
└── README.md            # This file
```

You generally won't need to touch `requirements.txt` or `.gitignore` — they're config housekeeping, not something to edit day-to-day.

---

## API reference

The backend exposes a small REST API. You can explore and test it directly in your browser at `http://127.0.0.1:8000/docs` while the backend is running.

| Method | Endpoint      | What it does                                                                 |
|--------|---------------|-------------------------------------------------------------------------------|
| POST   | `/pose-check` | Checks a single camera frame — returns eye-openness and head-turn angle. Used repeatedly during the live guided scan. |
| POST   | `/register`   | Saves a face under a given name (warns if that face looks already registered under a different name) |
| POST   | `/verify`     | Compares a face against everyone registered and returns the best match, if any |
| GET    | `/list`       | Lists everyone registered and how many reference photos each person has        |
| DELETE | `/delete`     | Removes a registered person                                                    |
| GET    | `/`           | Basic health check — confirms the backend is running                          |

---

## Troubleshooting

**"python is not recognized" / "python: command not found"**
Python isn't installed, or wasn't added to PATH during installation. Reinstall Python and make sure to tick "Add Python to PATH" on the first screen.

**`pip install -r requirements.txt` fails mentioning Visual C++ or CMake**
Install Visual Studio Build Tools with the "Desktop development with C++" workload (see the prerequisites table), then restart your computer and try again.

**Browser says camera not available, but you know you have one**
Make sure you opened `index.html` through Live Server (a `http://127.0.0.1:5500/...` address), not by double-clicking the file directly. Also check your browser's camera permission for the site is set to "Allow".

**"Connection error — is the backend running on port 8000?"**
The backend terminal isn't running, or was closed. Go back to it, make sure `(venv)` is active, and run `uvicorn main:app --reload` again.

**Liveness steps aren't confirming even though you're following the prompts**
Make sure you're in reasonably good, even lighting, your full face is inside the frame, and you turn your head clearly rather than just slightly. The live number shown next to each instruction increases as you move — the step confirms once it crosses the required amount.

**Face recognized with low confidence, or not recognized at all**
Register a few more reference photos for that person from slightly different angles and lighting — the more references on file, the more reliable matching becomes. You can also loosen the Match strictness slider.

**Port 8000 already in use**
Something else on your computer is already using that port. Either close that other program, or start the backend on a different port with `uvicorn main:app --reload --port 8001` (and update the `API_BASE` value near the top of the `<script>` section in `index.html` to match).

---

## Notes and limitations

- Registered faces are stored in memory only — everyone registered is forgotten when the backend restarts. This is a learning/prototyping project, not a production-ready system with permanent storage.
- Everything runs locally on your own machine; no images or data are sent anywhere else.
- This isn't a substitute for hardware-based biometric security (like a phone's infrared Face ID sensor) — it's a software-only liveness check meant to raise the bar against very basic spoofing (e.g. holding up a plain printed photo), not to withstand a determined attacker.
