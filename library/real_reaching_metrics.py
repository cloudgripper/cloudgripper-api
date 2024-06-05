import cv2
import numpy as np
import matplotlib.pyplot as plt
def get_t_mask(img, hsv_ranges=None):
    if hsv_ranges is None:
        hsv_ranges = [
            [110, 255],
            [120, 255],
            [125, 255],
        ]
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    mask = np.ones(img.shape[:2], dtype=bool)
    for c in range(len(hsv_ranges)):
        l, h = hsv_ranges[c]
        mask &= (l <= hsv_img[...,c])
        mask &= (hsv_img[...,c] <= h)
    return mask

def get_mask_metrics(target_mask, mask):
    total = np.sum(target_mask)
    i = np.sum(target_mask & mask)
    u = np.sum(target_mask | mask)
    iou = i / u
    iou_with_label = 2*(iou - 0.5)
    # coverage = i / total
    # result = {
    #     'iou': iou,
    #     'coverage': coverage
    # }
    return iou_with_label

def plot_mask(mask):
    fig, ax = plt.subplots()
    # Display the matrix as an image
    ax.imshow(mask, cmap='binary')

    # Set the ticks and labels
    ax.tick_params(axis='both', which='both', length=0)

    # Add gridlines
    ax.grid(color='gray', linewidth=0.5)

    # Show the figure
    plt.show()

def concat(a, b):
    if a.size == 0:
        return b
    else:
        return np.concatenate((a, b), axis=0)