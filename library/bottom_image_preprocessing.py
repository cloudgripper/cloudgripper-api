import cv2
import numpy as np

# rotate all the frame in the video, reverse clock-wise for 90 degree
# def rotate(image, angle, center=None, scale=1.0):
#     (h, w) = image.shape[:2]
#     if center is None:
#         center = (w/2, h/2)
#     M = cv2.getRotationMatrix2D(center, angle, scale)
#     rotated = cv2.warpAffine(image, M, (w,h))
#     return rotated


def rotate(image, angle):
    # grab the dimensions of the image and calculate the center
    (h, w) = image.shape[:2]
    (cX, cY) = (w / 2, h / 2)

    # grab the rotation matrix (applying the negative of the
    # angle to rotate clockwise), then grab the sine and cosine
    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    # compute the new bounding dimensions of the image
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    # adjust the rotation matrix to take into account translation
    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    # perform the actual rotation and return the image
    return cv2.warpAffine(image, M, (nW, nH))


# mirror the image
def mirror(image):
    return cv2.flip(image, 1)
