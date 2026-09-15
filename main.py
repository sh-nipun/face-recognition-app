from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import face_recognition
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ekjon-er jonno multiple encoding store hobe: { "name": [encoding1, encoding2, ...] }
known_faces = {}


def eye_aspect_ratio(eye_points):
    """6-point eye landmark theke Eye Aspect Ratio (EAR) calculate kore.
    Chokh khola thakle EAR beshi, bondho thakle EAR kome jay."""
    eye = np.array(eye_points)
    # Vertical distances
    v1 = np.linalg.norm(eye[1] - eye[5])
    v2 = np.linalg.norm(eye[2] - eye[4])
    # Horizontal distance
    h = np.linalg.norm(eye[0] - eye[3])
    if h == 0:
        return 0
    return (v1 + v2) / (2.0 * h)


@app.post("/register")
async def register_face(name: str, file: UploadFile = File(...), force: bool = False):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    new_encoding = encodings[0]

    # Duplicate check: ei face ki onno kono name-e already registered?
    if not force:
        for existing_name, encoding_list in known_faces.items():
            if existing_name == name:
                continue
            distances = face_recognition.face_distance(encoding_list, new_encoding)
            if len(distances) > 0 and min(distances) <= 0.5:
                return {
                    "status": "duplicate_warning",
                    "message": f"Ei face ta already '{existing_name}' name-e registered ache",
                    "matched_name": existing_name
                }

    if name not in known_faces:
        known_faces[name] = []

    known_faces[name].append(new_encoding)
    count = len(known_faces[name])

    return {
        "status": "success",
        "message": f"{name} — {count}-no photo register hoyeche",
        "count": count
    }


@app.post("/verify")
async def verify_face(file: UploadFile = File(...), tolerance: float = 0.5):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    unknown_encoding = encodings[0]

    best_name = None
    best_distance = None

    for name, encoding_list in known_faces.items():
        distances = face_recognition.face_distance(encoding_list, unknown_encoding)
        min_distance = min(distances)
        if best_distance is None or min_distance < best_distance:
            best_distance = min_distance
            best_name = name

    if best_distance is not None and best_distance <= tolerance:
        confidence = round((1 - best_distance) * 100, 2)
        return {"status": "success", "match": True, "name": best_name, "confidence": confidence}

    return {"status": "success", "match": False, "name": None}


@app.get("/list")
async def list_faces():
    people = [{"name": name, "count": len(encodings)} for name, encodings in known_faces.items()]
    return {"status": "success", "people": people}


@app.delete("/delete")
async def delete_face(name: str):
    if name not in known_faces:
        return {"status": "error", "message": f"'{name}' registered nei"}

    del known_faces[name]
    return {"status": "success", "message": f"{name} remove kora hoyeche"}


@app.post("/verify-live")
async def verify_live(files: List[UploadFile] = File(...), tolerance: float = 0.5):
    """Multiple frame (burst capture) diye blink-based liveness check kore,
    tarpor blink confirm hole shob-cheye clear (eye-open) frame diye recognition kore."""

    OPEN_THRESHOLD = 0.23
    CLOSED_THRESHOLD = 0.19

    ear_sequence = []
    frame_data = []  # (encoding, ear)

    for f in files:
        image = face_recognition.load_image_file(f.file)
        landmarks_list = face_recognition.face_landmarks(image)
        encodings = face_recognition.face_encodings(image)

        if not landmarks_list or not encodings:
            continue

        landmarks = landmarks_list[0]
        if "left_eye" not in landmarks or "right_eye" not in landmarks:
            continue

        left_ear = eye_aspect_ratio(landmarks["left_eye"])
        right_ear = eye_aspect_ratio(landmarks["right_eye"])
        avg_ear = (left_ear + right_ear) / 2.0

        ear_sequence.append(avg_ear)
        frame_data.append((encodings[0], avg_ear))

    if len(ear_sequence) < 3:
        return {
            "status": "error",
            "message": "Face clearly dekha jayni. Aro kache ashun ar alo thik korun."
        }

    min_ear = min(ear_sequence)
    max_ear = max(ear_sequence)
    blink_detected = (min_ear < CLOSED_THRESHOLD) and (max_ear > OPEN_THRESHOLD)

    if not blink_detected:
        return {
            "status": "success",
            "liveness": False,
            "message": "Blink detect kora jayni. Ekbar chokh bondho-khola korun ar abar try korun."
        }

    # Recognition-er jonno shob-cheye clear (chokh sবচেয়ে khola) frame-ta use kora hoy
    best_encoding, _ = max(frame_data, key=lambda item: item[1])

    best_name = None
    best_distance = None

    for name, encoding_list in known_faces.items():
        distances = face_recognition.face_distance(encoding_list, best_encoding)
        d = min(distances)
        if best_distance is None or d < best_distance:
            best_distance = d
            best_name = name

    if best_distance is not None and best_distance <= tolerance:
        confidence = round((1 - best_distance) * 100, 2)
        return {
            "status": "success",
            "liveness": True,
            "match": True,
            "name": best_name,
            "confidence": confidence
        }

    return {"status": "success", "liveness": True, "match": False, "name": None}


@app.get("/")
async def root():
    return {"message": "Face Recognition API is running"}
