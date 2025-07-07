import cv2
import mediapipe as mp
import joblib
import numpy as np
import pyttsx3
import os
import uuid
import subprocess
from pydub import AudioSegment
from pose_tracker import RepetitionCounter
from report_writer import write_report


def process_video(input_path, output_dir="outputs"):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs("audio_clips", exist_ok=True)

    # Load classifier
    classifier = joblib.load("exercise_classifier.pkl")

    # Supported exercises
    exercise_configs = {
        "bicep_curl": {"joint_triplet": ["left_shoulder", "left_elbow", "left_wrist"], "angle_range": (50, 160)},
        "pull_up": {"joint_triplet": ["left_shoulder", "left_elbow", "left_wrist"], "angle_range": (15, 165)},
        "squat": {"joint_triplet": ["left_hip", "left_knee", "left_ankle"], "angle_range": (60, 160)},
        "shoulder_press": {"joint_triplet": ["left_elbow", "left_shoulder", "left_hip"], "angle_range": (70, 170)},
        "trx_row": {"joint_triplet": ["left_shoulder", "left_elbow", "left_hip"], "angle_range": (60, 160)}
    }

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False, model_complexity=1)

    file_id = uuid.uuid4().hex
    output_video = os.path.join(output_dir, f"{file_id}_output.mp4")
    output_with_audio = os.path.join(output_dir, f"{file_id}_output_with_audio.mp4")
    report_file = os.path.join(output_dir, f"{file_id}_report.txt")

    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or 24  # fallback if fps = 0
    out = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))

    frame_count = 0
    frames_to_check = 30
    angle_data = []
    rep_audio_cues = []
    detected_exercise = None
    counter = None

    # TTS setup
    tts = pyttsx3.init()
    tts.setProperty('rate', 160)

    def speak_to_wav(text, filename):
        tts.save_to_file(text, filename)
        tts.runAndWait()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb)

        if results.pose_landmarks:
            h, w, _ = frame.shape
            landmarks = results.pose_landmarks.landmark

            def get_point(name):
                lm = getattr(mp_pose.PoseLandmark, name.upper())
                return (int(landmarks[lm].x * w), int(landmarks[lm].y * h))

            try:
                if detected_exercise is None and frame_count < frames_to_check:
                    def angle(a, b, c):
                        a = np.array(get_point(a))
                        b = np.array(get_point(b))
                        c = np.array(get_point(c))
                        ba = a - b
                        bc = c - b
                        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
                        return np.degrees(np.arccos(np.clip(cosine_angle, -1.0, 1.0)))

                    elbow = angle("left_shoulder", "left_elbow", "left_wrist")
                    knee = angle("left_hip", "left_knee", "left_ankle")
                    shoulder = angle("left_elbow", "left_shoulder", "left_hip")
                    angle_data.append([elbow, knee, shoulder])
                    frame_count += 1

                    if frame_count == frames_to_check:
                        avg_angles = np.mean(angle_data, axis=0).reshape(1, -1)
                        detected_exercise = classifier.predict(avg_angles)[0]
                        config = exercise_configs[detected_exercise]
                        counter = RepetitionCounter(config["joint_triplet"], config["angle_range"])
                        print(f"✅ Detected Exercise: {detected_exercise}")

                if detected_exercise and counter:
                    keypoints = {joint: get_point(joint) for joint in counter.joint_triplet}
                    count, angle_val, form_ok = counter.update(keypoints)

                    if angle_val:
                        cv2.putText(frame, f"Angle: {angle_val:.2f}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                    cv2.putText(frame, f"Reps: {count}", (10, 60),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    cv2.putText(frame, f"Exercise: {detected_exercise}", (10, 100),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

                    if getattr(counter, "rep_just_counted", False):
                        rep_audio_cues.append((frame_count, count))
                        counter.rep_just_counted = False

            except Exception as e:
                print("❌ Error:", e)

        out.write(frame)
        frame_count += 1

    cap.release()
    out.release()
    pose.close()

    # Generate Audio Overlay
    if rep_audio_cues:
        duration_sec = frame_count / fps
        base_audio = AudioSegment.silent(duration=int(duration_sec * 1000))

        for frame_idx, rep_num in rep_audio_cues:
            audio_file = f"audio_clips/rep_{uuid.uuid4().hex[:6]}.wav"
            speak_to_wav(f"Good job! Rep {rep_num}", audio_file)
            rep_audio = AudioSegment.from_wav(audio_file)
            start_ms = int((frame_idx / fps) * 1000)
            base_audio = base_audio.overlay(rep_audio, position=start_ms)

        combined_audio = os.path.join(output_dir, f"{file_id}_combined.mp3")
        base_audio.export(combined_audio, format="mp3")

        subprocess.call([
            "ffmpeg", "-y", "-i", output_video, "-i", combined_audio,
            "-c:v", "copy", "-c:a", "aac", "-strict", "experimental",
            "-shortest", output_with_audio
        ])
        print(f"✅ Final video with audio saved: {output_with_audio}")
    else:
        print("⚠️ No reps detected to overlay audio.")

    # Generate report
    if counter:
        summary = counter.get_summary()
        write_report(summary, exercise_name=detected_exercise,
                     video_name=os.path.basename(input_path), report_path=report_file)
    else:
        summary = {"total_reps": 0, "form_score": 0}

    return {
        "exercise": detected_exercise,
        "reps": summary["total_reps"],
        "score": summary["form_score"],
        "video_path": output_with_audio if rep_audio_cues else output_video,
        "report_path": report_file
    }


# For standalone run
if __name__ == "__main__":
    result = process_video("pull_up.mp4", output_dir="output")
    print("\n--- Summary ---")
    print(result)
