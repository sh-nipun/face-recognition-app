from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/")
async def root():
    return {"message": "Face Recognition API is running"}
