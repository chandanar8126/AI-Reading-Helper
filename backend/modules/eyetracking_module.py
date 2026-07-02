"""
Eye-tracking / difficulty-detection module.

This is a STANDALONE diagnostic script, not something called from a Flask
route. Continuous webcam capture doesn't fit a request/response web cycle —
the real, browser-based eye tracking that powers the live reading experience
is WebGazer.js, running client-side in result.html. This module exists for
local testing/research: run it directly (python eyetracking_module.py) to
log webcam-based attention data to a file, headless (no GUI window).
"""

import os
import time
from datetime import datetime

import cv2

LOG_PATH = "logs"
LOG_FILE = os.path.join(LOG_PATH, "difficulty_events.txt")
os.makedirs(LOG_PATH, exist_ok=True)

# How many consecutive frames with a face but no detected eyes before we
# treat it as a "difficulty" signal (looking away, squinting, disengaged).
EYES_LOST_THRESHOLD_FRAMES = 15


def log_event(message):
    """Append a timestamped line to the difficulty log."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().isoformat()} - {message}\n")


def log_difficulty_event():
    """Kept for backward compatibility with app.py's /log-difficulty route."""
    log_event("Difficulty detected")


def start_eye_tracking(max_duration_seconds=None):
    """
    Run headless face/eye detection against the default webcam and log
    attention/difficulty events to logs/difficulty_events.txt.

    No GUI window is opened — this is safe to run from a terminal on a
    machine without a display, and won't hang a web request if ever
    imported elsewhere (though it still should not be called from a
    Flask route; it blocks and owns the camera until stopped).

    Args:
        max_duration_seconds: optional auto-stop after N seconds. If None,
            runs until interrupted with Ctrl+C.
    """
    eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_eye.xml")
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Camera not accessible.")
        log_event("Session failed: camera not accessible")
        return

    print("Eye tracking started (headless). Press Ctrl+C to stop.")
    log_event("Session started")

    eyes_lost_streak = 0
    start_time = time.time()

    try:
        while True:
            if max_duration_seconds and (time.time() - start_time) > max_duration_seconds:
                print(f"Reached max duration of {max_duration_seconds}s, stopping.")
                break

            ret, frame = cam.read()
            if not ret:
                print("Camera read failed, stopping.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)

            if len(faces) == 0:
                eyes_lost_streak += 1
            else:
                for (x, y, w, h) in faces:
                    roi_gray = gray[y:y + h, x:x + w]
                    eyes = eye_cascade.detectMultiScale(roi_gray)

                    if len(eyes) == 0:
                        eyes_lost_streak += 1
                    else:
                        eyes_lost_streak = 0

            if eyes_lost_streak == EYES_LOST_THRESHOLD_FRAMES:
                log_event("Difficulty detected: eyes not tracked for sustained period")
                print("Difficulty signal logged.")

            time.sleep(0.05)  # ~20 fps cap, avoids pegging the CPU

    except KeyboardInterrupt:
        print("\nStopped by user.")

    finally:
        cam.release()
        log_event("Session ended")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Headless eye-tracking diagnostic logger")
    parser.add_argument(
        "--duration", type=int, default=None,
        help="Auto-stop after this many seconds (default: run until Ctrl+C)"
    )
    args = parser.parse_args()

    start_eye_tracking(max_duration_seconds=args.duration)