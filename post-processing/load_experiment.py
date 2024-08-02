import os
import os
import json
import cv2
import numpy as np


def load_experiment_data(
    experiment_id, start_frame, end_frame, base_path="path_to_experiments"
):
    experiment_path = os.path.join(base_path, experiment_id)
    task_path = os.path.join(experiment_path, "task")

    # Paths to video directories
    bottom_video_path = os.path.join(task_path, "Bottom_Video")
    normal_video_path = os.path.join(task_path, "Video")

    # Path to final image and states.json
    states_path = os.path.join(task_path, "states.json")
    actions_path = os.path.join(task_path, "actions.json")

    # Load states.json
    with open(states_path, "r") as f:
        states = json.load(f)

    # Load actions.json
    with open(actions, "r") as f:
        actions = json.load(f)

    # Get relevant states and actions
    relevant_states = states[start_frame : end_frame + 1]
    relevant_actions = actions[start_frame : end_frame + 1]

    # Function to load frames from videos
    def load_frames_from_videos(video_path, start_frame, end_frame):
        frames = []
        video_files = sorted(
            [
                f
                for f in os.listdir(video_path)
                if f.startswith("video_") and f.endswith(".mp4")
            ]
        )
        frame_count = 0
        cap = None
        for video_file in video_files:
            video_file_path = os.path.join(video_path, video_file)
            cap = cv2.VideoCapture(video_file_path)
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                if start_frame <= frame_count <= end_frame:
                    frames.append(frame)
                frame_count += 1
                if frame_count > end_frame:
                    break
            if frame_count > end_frame:
                break
        if cap:
            cap.release()
        return frames

    # Load frames from Bottom_Video
    bottom_frames = load_frames_from_videos(bottom_video_path, start_frame, end_frame)

    # Load frames from Video
    normal_frames = load_frames_from_videos(normal_video_path, start_frame, end_frame)

    return {
        "bottom_frames": bottom_frames,
        "normal_frames": normal_frames,
        "states": relevant_states,
        "actions": relevant_actions,
    }


"""
# Example usage
experiment_id = "1"
start_frame = 25
end_frame = 35
data = load_experiment_data(
    experiment_id,
    start_frame,
    end_frame,
    base_path="stack_from_scratch/recorded_data",
)

from PIL import Image as im

test_image = data["bottom_frames"][0]
test_image = im.fromarray(test_image)
test_image.save('test_image.png')
"""
