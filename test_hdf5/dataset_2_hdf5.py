import h5py
import os
import json
import cv2
import numpy as np
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Define the root directory and the output HDF5 file
root_dir = "./"
output_dir = "output"
hdf5_file_path = os.path.join(output_dir, "dataset.hdf5")

# Create the output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)


# Function to add JSON data to HDF5
def add_json_to_hdf5(group, item_path, item_name):
    with open(item_path, "r") as json_file:
        data = json.load(json_file)
        json_data = json.dumps(data)
        group.create_dataset(item_name, data=json_data)


# Function to add text data to HDF5
def add_txt_to_hdf5(group, item_path, item_name):
    with open(item_path, "r") as txt_file:
        data = txt_file.read()
        group.create_dataset(item_name, data=data)


# Function to add video data to HDF5 in chunks
def add_video_to_hdf5(group, item_path, item_name):
    cap = cv2.VideoCapture(item_path)
    chunk_size = 100  # Adjust chunk size based on memory constraints
    frame_count = 0

    pbar = tqdm(desc=f"Processing video: {item_name}", unit="frame")
    while True:
        frames = []
        for _ in range(chunk_size):
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            frame_count += 1

        if frames:
            group.create_dataset(
                f"{item_name}_chunk_{frame_count // chunk_size}",
                data=np.array(frames),
                compression="gzip",
            )
        else:
            break

        pbar.update(len(frames))

    pbar.close()
    cap.release()


# Function to list files and directories using a generator
def list_items(current_path):
    return [os.path.join(current_path, item) for item in os.listdir(current_path)]


# Open an HDF5 file
with h5py.File(hdf5_file_path, "w") as hdf5_file:
    # Function to recursively add data to HDF5
    def add_to_hdf5(group, items):
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = []
            for item_path in items:
                if os.path.isdir(item_path):
                    subgroup = group.create_group(os.path.basename(item_path))
                    futures.append(
                        executor.submit(add_to_hdf5, subgroup, list_items(item_path))
                    )
                else:
                    item_name = os.path.basename(item_path)
                    if item_name.endswith(".json"):
                        futures.append(
                            executor.submit(
                                add_json_to_hdf5, group, item_path, item_name
                            )
                        )
                    elif item_name.endswith(".mp4"):
                        futures.append(
                            executor.submit(
                                add_video_to_hdf5, group, item_path, item_name
                            )
                        )
                    elif item_name.endswith(".txt"):
                        futures.append(
                            executor.submit(
                                add_txt_to_hdf5, group, item_path, item_name
                            )
                        )

            for future in as_completed(futures):
                future.result()  # Ensure all tasks are completed

    # Use ThreadPoolExecutor to handle directories concurrently
    with ThreadPoolExecutor(2) as executor:
        futures = []
        root_items = list_items(root_dir)
        for item_path in root_items:
            if os.path.isdir(item_path):
                futures.append(
                    executor.submit(
                        add_to_hdf5,
                        hdf5_file.create_group(os.path.basename(item_path)),
                        list_items(item_path),
                    )
                )
            else:
                item_name = os.path.basename(item_path)
                if item_name.endswith(".json"):
                    futures.append(
                        executor.submit(
                            add_json_to_hdf5, hdf5_file, item_path, item_name
                        )
                    )
                elif item_name.endswith(".mp4"):
                    futures.append(
                        executor.submit(
                            add_video_to_hdf5, hdf5_file, item_path, item_name
                        )
                    )
                elif item_name.endswith(".txt"):
                    futures.append(
                        executor.submit(
                            add_txt_to_hdf5, hdf5_file, item_path, item_name
                        )
                    )

        for future in as_completed(futures):
            future.result()  # Ensure all tasks are completed
