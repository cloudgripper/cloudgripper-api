import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_red_area(frame, lower_range1, upper_range1, lower_range2, upper_range2):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv_frame, lower_range1, upper_range1)
    mask2 = cv2.inRange(hsv_frame, lower_range2, upper_range2)
    combined_mask = cv2.bitwise_or(mask1, mask2)
    red_area = np.sum(combined_mask) / 255  # Convert to pixe# #  #
    return red_area

def process_video(video_path, lower_range1, upper_range1, lower_range2, upper_range2):
    cap = cv2.VideoCapture(video_path)
    red_area_list = []

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        red_area = get_red_area(frame, lower_range1, upper_range1, lower_range2, upper_range2)
        red_area_list.append(red_area)
    # print(red_area_list)
    cap.release()
    return red_area_list

def calculate_occlusion_percentage(lst, threshold):
    lst = np.array(lst)
    entire_area = threshold
    # if len(lst[lst > threshold]) == 0:
    #     entire_area = threshold
    # else:
    #     entire_area = np.mean(lst[lst > threshold])
    percent = np.clip(lst/entire_area, 0, 1)
    res = 1 - np.mean(percent)
    return res

def folder_operation(folder_name, lower_range1, upper_range1, lower_range2, upper_range2, threshold, plot=False):
    video_files = [f for f in os.listdir(folder_name) if f.endswith('.mp4')]
    res = []

    for video_file in video_files:
        video_path = os.path.join(folder_name, video_file)
        red_area_list = process_video(video_path, lower_range1, upper_range1, lower_range2, upper_range2)
        occlusion_percent = calculate_occlusion_percentage(red_area_list, threshold)
        res.append(occlusion_percent)
    if plot:
        plt.figure()
        # Create a histogram
        plt.hist(res, bins=10, color='blue', edgecolor='black')
        # Add labels and title
        plt.xlabel('Occlusion Rate')
        plt.ylabel('Frequency')
        plt.title(f'Histogram of Occlusion Rate for {folder_name}')

        # Display the histogram
        plt.show()
    return res


if __name__ == "__main__":
    # HSV range for color red
    lower_range1 = np.array([0, 100, 100])
    upper_range1 = np.array([10, 255, 255])
    lower_range2 = np.array([160, 100, 100])
    upper_range2 = np.array([179, 255, 255])

    # # Use case 1: apply folder operation for a folder to calculate all the occlusion rates in it
    # folder = "/home/olivew/Real_Data/test/ico"
    # a = folder_operation(folder, lower_range1, upper_range1, lower_range2, upper_range2, threshold=5600)
    # print(a)

    # Use case 2: apply folder operation for a set of folder, foam_double in this case
    foam_root = "/proj/berzelius-2023-54/users/x_shuji/OccluManip/Ball/"  # Root directory containing all the data
    save_dir = 'ball_quadruple_dynamic_occu_rate_ruiyu.txt'

    foam_double_res = []
    for root, dirs, files in os.walk(foam_root):
        if "Quadruple_dynamic" in root and "Test" not in root and "Video" in dirs:
            video_folder_path = os.path.join(root, "Video/")
            print(f"Started processing Folder: {video_folder_path}")
            foam_double_res = foam_double_res + folder_operation(video_folder_path, lower_range1, upper_range1, lower_range2, upper_range2, threshold=6800)
            print(f"Finished processing Folder: {video_folder_path}")
    print(foam_double_res)

    if os.path.exists(save_dir):
        os.remove(save_dir)
    with open(save_dir, 'w') as f:
        for item in foam_double_res:
            f.write(str(item) + '\n')
