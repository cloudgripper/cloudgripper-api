import h5py
import os
import json
import cv2
import numpy as np
from tqdm import tqdm

# Define the output directory for JSON and MP4 files
output_dir = "output_experiment"
os.makedirs(output_dir, exist_ok=True)


# Function to write JSON data to a file
def write_json(data, output_path):
    with open(output_path, "w") as json_file:
        json.dump(data, json_file, indent=4)


# Function to write video frames to an MP4 file
def write_video(frames, output_path, fps=30):
    if len(frames) == 0:
        return
    height, width, layers = frames[0].shape
    size = (width, height)
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, size)
    for frame in tqdm(frames, desc=f"Writing video to {output_path}"):
        out.write(frame)
    out.release()


# Function to process an experiment and save to JSON and MP4
def process_experiment(hdf5_file_path, experiment_id):
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        experiment_group = hdf5_file[str(experiment_id)]

        for task in ["task"]:
            task_group = experiment_group[task]
            # Process JSON files
            for json_file in ["states.json", "actions.json"]:
                json_data = json.loads(task_group[json_file][()])
                output_json_path = os.path.join(
                    output_dir, f"{experiment_id}_{task}_{json_file}"
                )
                write_json(json_data, output_json_path)

            # Process Video files
            for video_type in ["Bottom_Video", "Video"]:
                video_group = task_group[video_type]
                frames = []
                for video_key in sorted(video_group.keys()):
                    frames.extend(video_group[video_key][:])
                output_video_path = os.path.join(
                    output_dir, f"{experiment_id}_{task}_{video_type}.mp4"
                )
                write_video(frames, output_video_path)


if __name__ == "__main__":
    # Example usage
    hdf5_file_path = "output/dataset.hdf5"  # Path to your HDF5 file
    experiment_id = 1  # Replace with the desired experiment ID
    process_experiment(hdf5_file_path, experiment_id)
