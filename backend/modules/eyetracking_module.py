import cv2
from datetime import datetime
import os

LOG_PATH = "logs"
os.makedirs(LOG_PATH, exist_ok=True)

def log_difficulty_event():
    with open(os.path.join(LOG_PATH, "difficulty_events.txt"), "a", encoding='utf-8') as f:
        f.write(f"{datetime.now()} - Difficulty detected\n")

def start_eye_tracking(test_mode=False):
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("❌ Camera not accessible.")
        return

    print("👁️ Eye tracking started... Press 'q' to stop.")

    while True:
        ret, frame = cam.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(frame, (x+ex, y+ey), (x+ex+ew, y+ey+eh), (0,255,0), 2)
                log_difficulty_event()

        cv2.imshow('Eye Tracking', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()
