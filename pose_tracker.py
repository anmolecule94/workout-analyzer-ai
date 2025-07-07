import numpy as np

def calculate_angle(a, b, c):
    a = np.array(a[:2])  # Only x and y
    b = np.array(b[:2])
    c = np.array(c[:2])

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-6)
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


class RepetitionCounter:
    def __init__(self, joint_triplet, angle_range=(60, 160), min_reps_for_score=3):
        self.joint_triplet = joint_triplet
        self.angle_range = angle_range
        self.stage = None
        self.reps = 0
        self.angles = []

        # New attribute for real-time feedback
        self.rep_just_counted = False

        # For reporting
        self.min_angles = []
        self.max_angles = []
        self.min_reps_for_score = min_reps_for_score

    def update(self, keypoints):
        try:
            a = keypoints[self.joint_triplet[0]]
            b = keypoints[self.joint_triplet[1]]
            c = keypoints[self.joint_triplet[2]]

            angle = calculate_angle(a, b, c)
            self.angles.append(angle)

            self.rep_just_counted = False  # Reset flag

            # Rep counting logic
            if angle <= self.angle_range[0]:
                if self.stage != 'down':
                    self.stage = 'down'
                    self.min_angles.append(angle)

            elif angle >= self.angle_range[1]:
                if self.stage == 'down':
                    self.stage = 'up'
                    self.reps += 1
                    self.max_angles.append(angle)
                    self.rep_just_counted = True  # Set flag
                    print(f"✅ Rep counted: {self.reps}, Angle: {angle}")
            
            return self.reps, angle, True

        except Exception as e:
            print("RepetitionCounter update error:", e)
            return self.reps, None, False

    def get_summary(self):
        total = self.reps
        avg_min = round(sum(self.min_angles) / len(self.min_angles), 2) if self.min_angles else 0
        avg_max = round(sum(self.max_angles) / len(self.max_angles), 2) if self.max_angles else 0
        form_score = int((avg_max - avg_min) / (self.angle_range[1] - self.angle_range[0]) * 100) if total >= self.min_reps_for_score else 0

        correct_reps = len([
            1 for min_a, max_a in zip(self.min_angles, self.max_angles)
            if (max_a - min_a) >= (self.angle_range[1] - self.angle_range[0]) * 0.8
        ])
        incorrect_reps = total - correct_reps

        rep_logs = []
        for i in range(total):
            min_angle = self.min_angles[i] if i < len(self.min_angles) else "-"
            max_angle = self.max_angles[i] if i < len(self.max_angles) else "-"
            rep_logs.append({
                "rep": i + 1,
                "min_angle": min_angle,
                "max_angle": max_angle,
                "correct": (max_angle - min_angle) >= (self.angle_range[1] - self.angle_range[0]) * 0.8
            })

        return {
            "total_reps": total,
            "correct_reps": correct_reps,
            "incorrect_reps": incorrect_reps,
            "avg_min_angle": avg_min,
            "avg_max_angle": avg_max,
            "form_score": form_score,
            "rep_logs": rep_logs
        }


class MultiExerciseClassifier:
    def __init__(self, exercise_configs):
        self.configs = exercise_configs
        self.angle_buffers = {name: [] for name in exercise_configs}
        self.repetition_counters = {
            name: RepetitionCounter(cfg["joint_triplet"], angle_range=cfg["angle_range"])
            for name, cfg in exercise_configs.items()
        }

    def update(self, keypoints):
        best_exercise = None
        best_score = -1
        angles = {}

        for name, counter in self.repetition_counters.items():
            try:
                a = keypoints[counter.joint_triplet[0]]
                b = keypoints[counter.joint_triplet[1]]
                c = keypoints[counter.joint_triplet[2]]

                angle = calculate_angle(a, b, c)
                self.angle_buffers[name].append(angle)

                if counter.angle_range[0] <= angle <= counter.angle_range[1]:
                    count, angle, _ = counter.update(keypoints)
                    angles[name] = angle

                    score = count + len(self.angle_buffers[name])
                    if score > best_score:
                        best_score = score
                        best_exercise = name

            except Exception:
                continue  # Skip invalid joints

        return best_exercise, angles.get(best_exercise, None), self.repetition_counters[best_exercise].reps if best_exercise else 0
