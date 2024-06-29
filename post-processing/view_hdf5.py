import h5py
import numpy as np
import matplotlib.pyplot as plt


def view_hdf5_file(hdf5_file_path):
    with h5py.File(hdf5_file_path, "r") as hdf5_file:
        # List all groups
        print("Keys: %s" % hdf5_file.keys())

        # Get the frames dataset
        frames = hdf5_file["frames"]
        print(f"Frames shape: {frames.shape}")
        print(f"Frames dtype: {frames.dtype}")

        # Display metadata
        metadata = hdf5_file["metadata"]
        for key, value in metadata.attrs.items():
            print(f"{key}: {value}")

        # Display the first frame
        first_frame = frames[0]
        plt.imshow(first_frame)
        plt.title("First Frame")
        plt.show()


if __name__ == "__main__":
    hdf5_file_path = "output_video.hdf5"
    view_hdf5_file(hdf5_file_path)
