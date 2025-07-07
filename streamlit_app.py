import streamlit as st
import uuid
import os
from main import process_video

st.set_page_config(page_title="🏋️ AI Fitness Coach", layout="centered")

st.title("🏋️ AI Fitness Coach")
st.write("Upload a workout video or record using your camera to detect the exercise, count reps, and get feedback.")
st.markdown("**Supported Exercises:**")
st.markdown("- Bicep Curl\n- Pull-Up\n- Squat\n- Shoulder Press")

input_method = st.radio("Choose Input Method", ["📤 Upload Video", "📷 Use Camera"])

video_path = None
file_id = uuid.uuid4().hex
os.makedirs("uploads", exist_ok=True)

if input_method == "📤 Upload Video":
    uploaded_file = st.file_uploader("Upload a short MP4 workout video", type=["mp4"])
    if uploaded_file:
        video_path = f"uploads/{file_id}.mp4"
        with open(video_path, "wb") as f:
            f.write(uploaded_file.read())
        st.video(video_path)

elif input_method == "📷 Use Camera":
    camera_file = st.camera_input("Record your exercise (10–20s recommended)")
    if camera_file:
        video_path = f"uploads/{file_id}_cam.mp4"
        with open(video_path, "wb") as f:
            f.write(camera_file.read())
        st.video(video_path)

if video_path:
    st.info("⏳ Processing video... please wait.")
    result = process_video(video_path, output_dir="outputs")

    if result and result["exercise"]:
        st.success("✅ Processing complete!")
        st.markdown(f"**🏋️ Detected Exercise:** {result['exercise'].title()}")
        st.markdown(f"**🔢 Reps Counted:** {result['reps']}")
        st.markdown(f"**💯 Form Score:** {result['score']}%")

        st.markdown("### 📥 Download Your Results")
        with open(result["video_path"], "rb") as f:
            st.download_button("🎬 Download Video with Audio", f, file_name="output_with_audio.mp4")

        with open(result["report_path"], "rb") as f:
            st.download_button("📄 Download Report", f, file_name="report.txt")

    else:
        st.error("⚠️ Could not detect valid exercise or no reps performed. Try again with clearer footage.")
