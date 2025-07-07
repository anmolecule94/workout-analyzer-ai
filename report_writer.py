# report_writer.py

import os

def write_report(
    summary: dict,
    exercise_name: str = "Bicep Curls",
    video_name: str = "input_video.mp4",
    report_path: str = None
):
    # Create default output path if not provided
    if report_path is None:
        os.makedirs("output", exist_ok=True)
        report_path = os.path.join("output", "report.txt")
    else:
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("AI Fitness Report\n")
        f.write("-" * 35 + "\n")
        f.write(f"Exercise: {exercise_name}\n")
        f.write(f"Video: {video_name}\n\n")

        f.write(f"Total Repetitions: {summary['total_reps']}\n")
        f.write(f"Correct Repetitions: {summary['correct_reps']}\n")
        f.write(f"Incorrect Repetitions: {summary['incorrect_reps']}\n\n")

        f.write(f"Form Accuracy: {summary['form_score']}%\n\n")

        f.write(f"Average Min Angle: {summary['avg_min_angle']}°\n")
        f.write(f"Average Max Angle: {summary['avg_max_angle']}°\n\n")

        f.write("Repetition Breakdown:\n")
        for rep in summary["rep_logs"]:
            symbol = "-"  # Placeholder for correctness
            f.write(f"  Rep {rep['rep']}: Min Angle = {rep['min_angle']}, Max Angle = {rep['max_angle']}, Status = {symbol}\n")

    print(f"\n✅ Report saved at: {report_path}")
