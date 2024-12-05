import os
import cv2
from PIL import Image
import numpy as np
from pynput import keyboard
import glob

# Set the root directory
root_dir = "autograsper/recorded_data"

# Collect all successful tasks
tasks = []
for x_dir in os.listdir(root_dir):
    x_path = os.path.join(root_dir, x_dir)
    status_file = os.path.join(x_path, "status.txt")
    image_pattern = os.path.join(x_path, "task/Final_Image/final_image_*.jpg")
    image_files = glob.glob(image_pattern)

    if os.path.isdir(x_path) and os.path.isfile(status_file) and image_files:
        with open(status_file, "r") as file:
            status = file.read().strip()
            if status == "success":
                # Pick the first matching image (or modify as needed to handle multiple)
                tasks.append((x_dir, image_files[0], status_file))

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
    print(f"Key pressed: {key}")

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
