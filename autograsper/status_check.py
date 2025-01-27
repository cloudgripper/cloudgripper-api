import os
import cv2
from PIL import Image
import numpy as np
import glob

# Set the root directory
root_dir = "autograsper/recorded_data"

# Helper function to get the last frame of the last video in the task/Video directory
def get_last_frame(video_dir):
    video_files = glob.glob(os.path.join(video_dir, "video_*.mp4"))
    if not video_files:
        return None

    # Sort videos by numeric x value
    video_files.sort(key=lambda x: int(os.path.basename(x).split("_")[-1].split(".")[0]), reverse=True)

    frame = None
    for video_file in video_files:
        cap = cv2.VideoCapture(video_file)
        if not cap.isOpened():
            print(f"Failed to open video: {video_file}")
            continue  # Try the next video

        while True:
            ret, current_frame = cap.read()
            if not ret:
                break
            frame = current_frame  # Keep updating until the last frame

        cap.release()

        if frame is not None:
            frame_path = os.path.join(video_dir, "last_frame.jpg")
            cv2.imwrite(frame_path, frame)  # Save the frame to a temporary file
            return frame_path

    print(f"No valid videos found in: {video_dir}")
    return None

# Collect all successful tasks
tasks = []
for x_dir in os.listdir(root_dir):
    x_path = os.path.join(root_dir, x_dir)
    status_file = os.path.join(x_path, "status.txt")
    video_dir = os.path.join(x_path, "task/Video")

    if os.path.isdir(x_path) and os.path.isfile(status_file) and os.path.isdir(video_dir):
        with open(status_file, "r") as file:
            status = file.read().strip()
            if status == "success":
                last_frame_path = get_last_frame(video_dir)
                if last_frame_path:
                    tasks.append((x_dir, last_frame_path, status_file))

# Initialize the task index
task_index = 0
num_tasks = len(tasks)

def show_image(task):
    """Displays the image using cv2."""
    image_path = task[1]
    print(f"Displaying image from path: {image_path}")
    pil_image = Image.open(image_path)
    image = np.array(pil_image)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    cv2.imshow("Image Viewer", image)

def mark_as_fail(task):
    """Changes the status to 'fail' in status.txt."""
    with open(task[2], "w") as file:
        file.write("fail")
    print(f"Marked task {task[0]} as fail.")

def mark_as_success(task):
    """Changes the status to 'success' in status.txt."""
    with open(task[2], "w") as file:
        file.write("success")
    print(f"Marked task {task[0]} as success.")

# Main loop to display images and handle key events
while task_index < num_tasks:
    show_image(tasks[task_index])

    key = cv2.waitKey(0)

    if key == ord('n'):  # Press 'n' to move to the next image
        mark_as_success(tasks[task_index])
        task_index += 1
    elif key == ord('f'):  # Press 'f' to mark as fail and move on
        mark_as_fail(tasks[task_index])
        task_index += 1
    elif key == 27:  # ESC key to exit
        print("Exiting program.")
        break
    else:
        print("Unrecognized key. Press 'n' for next, 'f' to fail, or 'Esc' to exit.")

    cv2.destroyAllWindows()

    if task_index >= num_tasks:
        print("End of successful tasks.")
        break

cv2.destroyAllWindows()
