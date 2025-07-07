import cv2
import mediapipe as mp
import os
import csv

# Define the joint angles you want to extract
from angle_utils import calculate_angle

# All videos are stored here
VIDEO_DIR = "exercise_dataset"
LABELS = ["bicep_curl", "squat", "pull_up", "shoulder_press"]

# Output dataset file
OUTPUT_CSV = "exercise_data.csv"

# Mediapipe pose setup
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, model_complexity=1)
mp_drawing = mp.solutions.drawing_utils

def extract_angles(landmarks, w, h):
    def get_point(name):
        lm = getattr(mp_pose.PoseLandmark, name.upper())
        return (int(landmarks[lm].x * w), int(landmarks[lm].y * h))

    try:
        left_elbow_angle = calculate_angle(get_point("left_shoulder"), get_point("left_elbow"), get_point("left_wrist"))
        left_knee_angle = calculate_angle(get_point("left_hip"), get_point("left_knee"), get_point("left_ankle"))
        left_shoulder_angle = calculate_angle(get_point("left_elbow"), get_point("left_shoulder"), get_point("left_hip"))
        return [left_elbow_angle, left_knee_angle, left_shoulder_angle]
    except:
        return None

# Create CSV
with open(OUTPUT_CSV, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(["elbow_angle", "knee_angle", "shoulder_angle", "label"])

    for label in LABELS:
        video_path = os.path.join(VIDEO_DIR, f"{label}.mp4")
        if not os.path.exists(video_path):
            print(f"Missing video: {video_path}")
            continue

        cap = cv2.VideoCapture(video_path)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            if results.pose_landmarks:
                h, w, _ = frame.shape
                landmarks = results.pose_landmarks.landmark
                angles = extract_angles(landmarks, w, h)
                if angles:
                    writer.writerow(angles + [label])

        cap.release()

print(f"✅ Dataset saved as: {OUTPUT_CSV}")
