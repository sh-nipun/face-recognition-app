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
async def register_face(name: str, file: UploadFile = File(...)):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    if name not in known_faces:
        known_faces[name] = []

    known_faces[name].append(encodings[0])
    count = len(known_faces[name])

    return {
        "status": "success",
        "message": f"{name} — {count}-no photo register hoyeche",
        "count": count
    }


@app.post("/verify")
async def verify_face(file: UploadFile = File(...)):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    unknown_encoding = encodings[0]

    best_name = None
    best_distance = None

    # Prottek registered person-er shob photo-r sathe compare kore, sবচেয়ে kache-r ta khuje ber kora
    for name, encoding_list in known_faces.items():
        distances = face_recognition.face_distance(encoding_list, unknown_encoding)
        min_distance = min(distances)
        if best_distance is None or min_distance < best_distance:
            best_distance = min_distance
            best_name = name

    if best_distance is not None and best_distance <= 0.5:
        confidence = round((1 - best_distance) * 100, 2)
        return {"status": "success", "match": True, "name": best_name, "confidence": confidence}

    return {"status": "success", "match": False, "name": None}


@app.get("/")
async def root():
    return {"message": "Face Recognition API is running"}