# 🏋️ AI Fitness Coach

AI Fitness Coach is a smart video-based workout analyzer that:
- Detects the type of exercise (e.g., Bicep Curl, Pull-Up, Squat, Shoulder Press)
- Counts repetitions accurately using pose estimation
- Provides audio feedback like “Good job! Rep 3”
- Generates a personalized performance report
- Includes a web interface using Streamlit

---

## 🚀 Features
- 🎥 Exercise classification from short workout videos
- 🔁 Rep counting with form evaluation
- 🔊 Real-time audio encouragement using TTS
- 📄 Report generation with rep count and form score
- 🌐 Simple web UI (Streamlit) with file upload and download support

---

## ✅ Supported Exercises (currently)
- Bicep Curl
- Pull-Up
- Squat
- Shoulder Press

> You can expand it to 10+ exercises with more data and model retraining.

---

## 📁 Project Structure

```bash
├── audio_clips/           # Temporary audio files for each rep
├── exercise_dataset/      # Dataset videos (organized per exercise)
├── outputs/               # Generated video, report, and audio files
├── uploads/               # Uploaded workout videos
├── main.py                # Core logic (detection, TTS, processing)
├── pose_tracker.py        # Repetition counter logic
├── report_writer.py       # Report generation
├── streamlit_app.py       # Streamlit web UI
├── generate_dataset.py    # Extract angles for dataset
├── train_classifier.py    # Train ML model for exercise classification
├── exercise_classifier.pkl# Trained model
├── requirements.txt       # Dependencies
└── README.md              # You're reading this
