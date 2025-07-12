import cv2
import argparse
import sys
import mediapipe as mp
import pyttsx3
import threading
from utils import *
from body_part_angle import BodyPartAngle
from types_of_exercise import TypeOfExercise

# 🔈 Initialize TTS
engine = pyttsx3.init()
engine.setProperty('rate', 150)

# 🧵 Asynchronous speech
def speak(text):
    def _speak():
        engine.say(text)
        engine.runAndWait()
    threading.Thread(target=_speak, daemon=True).start()

# 👇 Auto CLI for VS Code
if len(sys.argv) == 1:
    sys.argv += ["--exercise_type", "pushup", "--video_source", "videos/push-up.mp4"]

# 🎯 Argparse
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--exercise_type", type=str, required=True, help="Exercise type")
ap.add_argument("-vs", "--video_source", type=str, required=False, help="Video source")
args = vars(ap.parse_args())

# 🎥 Video input
cap = cv2.VideoCapture(args["video_source"]) if args["video_source"] else cv2.VideoCapture(0)
cap.set(3, 800)
cap.set(4, 480)

# 🏋️‍♀️ MediaPipe setup
mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose

exercise_type = args["exercise_type"].lower().replace("-", "").replace("_", "")
counter = 0
status = True

with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
    while cap.isOpened():
        try:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, (800, 480))
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb.flags.writeable = False
            results = pose.process(frame_rgb)
            frame_rgb.flags.writeable = True
            frame = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                landmarks = results.pose_landmarks.landmark
                new_counter, new_status = TypeOfExercise(landmarks).calculate_exercise(exercise_type, counter, status)

                if new_counter > counter:
                    speak(f"Number of {exercise_type} is {new_counter}")

                counter, status = new_counter, new_status

                # ✏️ Draw table overlay
                cv2.rectangle(frame, (0, 0), (300, 80), (0, 0, 0), -1)
                cv2.putText(frame, f'Exercise: {exercise_type.upper()}', (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(frame, f'Reps: {counter}', (10, 65),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

                # ✨ Draw body landmarks
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(174, 139, 45), thickness=2, circle_radius=2)
                )

            # Show video
            cv2.imshow('Exercise Tracker', frame)

            key = cv2.waitKey(10) & 0xFF
            if key == ord('q'):
                break

        except Exception as e:
            print("Error:", e)
            break

# 🎉 On exit
speak(f"{exercise_type.capitalize()} session completed with {counter} repetitions.")
cap.release()
cv2.destroyAllWindows()
