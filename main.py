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


def eye_aspect_ratio(eye_points):
    """6-point eye landmark theke Eye Aspect Ratio (EAR) calculate kore.
    Chokh khola thakle EAR beshi, bondho thakle EAR kome jay."""
    eye = np.array(eye_points)
    v1 = np.linalg.norm(eye[1] - eye[5])
    v2 = np.linalg.norm(eye[2] - eye[4])
    h = np.linalg.norm(eye[0] - eye[3])
    if h == 0:
        return 0
    return (v1 + v2) / (2.0 * h)


def face_metrics(landmarks):
    """Ekta frame-er landmark theke:
    - EAR (eye-openness, blink bujhar jonno)
    - signed head-turn offset (face-er nijer eye-to-eye axis onujayi — tai camera
      je angle-e rotate thakuk na kеn, thik moto kaj kore). Positive/negative dui
      dik-e move korle turn-left ar turn-right আলাদা kore bujha jay."""
    left_eye = np.array(landmarks["left_eye"])
    right_eye = np.array(landmarks["right_eye"])

    ear = (eye_aspect_ratio(landmarks["left_eye"]) + eye_aspect_ratio(landmarks["right_eye"])) / 2.0

    left_center = left_eye.mean(axis=0)
    right_center = right_eye.mean(axis=0)
    eye_mid = (left_center + right_center) / 2.0
    eye_vector = right_center - left_center
    inter_eye_dist = np.linalg.norm(eye_vector)

    nose_points = landmarks.get("nose_tip") or landmarks.get("nose_bridge")
    offset = 0.0
    if nose_points and inter_eye_dist > 0:
        nose = np.array(nose_points).mean(axis=0)
        nose_vec = nose - eye_mid
        eye_dir = eye_vector / inter_eye_dist
        offset = float(np.dot(nose_vec, eye_dir) / inter_eye_dist)

    return float(ear), offset


@app.post("/pose-check")
async def pose_check(file: UploadFile = File(...)):
    """Ekta single frame-e face ache kina, chokh koto khola (EAR), ar matha
    koto/kon-dike ghurano (signed offset) — eita instant return kore. Frontend
    ei endpoint-ke bar bar call kore real-time-e guided scan-er progress dekhe."""
    image = face_recognition.load_image_file(file.file)
    landmarks_list = face_recognition.face_landmarks(image)

    if not landmarks_list:
        return {"found": False}

    landmarks = landmarks_list[0]
    if "left_eye" not in landmarks or "right_eye" not in landmarks:
        return {"found": False}

    ear, offset = face_metrics(landmarks)
    return {"found": True, "ear": ear, "offset": offset}


@app.post("/register")
async def register_face(name: str, file: UploadFile = File(...), force: bool = False):
    image = face_recognition.load_image_file(file.file)
    encodings = face_recognition.face_encodings(image)

    if len(encodings) == 0:
        return {"status": "error", "message": "Kono face detect hoyni"}

    new_encoding = encodings[0]

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
