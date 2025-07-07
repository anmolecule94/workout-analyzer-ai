import math

def dummy_keypoints(frame, frame_idx):
    """
    Simulate elbow bending using sinusoidal angle.
    """
    h, w, _ = frame.shape

    # Angle swings from 60° to 160°
    angle_deg = 110 + 50 * math.sin(frame_idx / 15)

    # Fixed shoulder
    shoulder = (int(w * 0.5), int(h * 0.3))

    # Elbow position
    upper_arm = 100
    angle_rad = math.radians(angle_deg)
    elbow = (
        int(shoulder[0] + upper_arm * math.cos(angle_rad)),
        int(shoulder[1] + upper_arm * math.sin(angle_rad))
    )

    # Wrist position
    forearm = 100
    wrist = (
        int(elbow[0] + forearm * math.cos(angle_rad)),
        int(elbow[1] + forearm * math.sin(angle_rad))
    )

    return {
        "left_shoulder": shoulder,
        "left_elbow": elbow,
        "left_wrist": wrist
    }
