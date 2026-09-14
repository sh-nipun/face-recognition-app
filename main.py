from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import face_recognition
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registered faces gula memory te store thakbe (server restart hole delete hoye jabe)
known_faces = {}  # { "name": encoding }


@app.post("/register")
async def register_face(name: str, file: UploadFile = File(...)):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    known_faces[name] = encodings[0]
    return {"status": "success", "message": f"{name} register hoyeche"}


@app.post("/verify")
async def verify_face(file: UploadFile = File(...)):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    unknown_encoding = encodings[0]

    for name, known_encoding in known_faces.items():
        results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.5)
        if results[0]:
            distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            return {
                "status": "success",
                "match": True,
                "name": name,
                "confidence": round((1 - distance) * 100, 2)
            }

    return {"status": "success", "match": False, "name": None}


@app.get("/")
async def root():
    return {"message": "Face Recognition API is running"}