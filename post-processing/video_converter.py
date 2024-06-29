import cv2
import h5py
import numpy as np


def mp4_to_hdf5(mp4_file_path, hdf5_file_path):
    # Open the video file
    video_capture = cv2.VideoCapture(mp4_file_path)
    if not video_capture.isOpened():
        raise Exception("Could not open video file: {}".format(mp4_file_path))

    # Get video properties
    frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_width = int(video_capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video_capture.get(cv2.CAP_PROP_FPS)

    # Create HDF5 file
    with h5py.File(hdf5_file_path, "w") as hdf5_file:
        # Create datasets for frames and metadata
        frames_dataset = hdf5_file.create_dataset(
            "frames", (frame_count, frame_height, frame_width, 3), dtype=np.uint8
        )
        metadata = hdf5_file.create_group("metadata")
        metadata.attrs["fps"] = fps
        metadata.attrs["frame_width"] = frame_width
        metadata.attrs["frame_height"] = frame_height

        # Read and store frames
        frame_index = 0
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break
            frames_dataset[frame_index] = frame
            frame_index += 1

    # Release the video capture
    video_capture.release()


if __name__ == "__main__":
    # Example usage
    mp4_file_path = "video_0.mp4"
    hdf5_file_path = "output_video.hdf5"
    mp4_to_hdf5(mp4_file_path, hdf5_file_path)
    print("Conversion complete. HDF5 file saved as:", hdf5_file_path)
