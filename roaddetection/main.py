import cv2
import numpy as np

"""
overlay_arrow takes in the frame of each video (frame)
and the arrow overlay, regardless of direction. then, 
the function creates a smooth overlay of the transparent 
arrow png over the video. it returns the original video
frame with the arrow overlay applied
"""

def detect_lines(frame, cropped):
    contours, _ = cv2.findContours(frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_list = list(contours)
    contours_list.sort(key=cv2.contourArea)

    final = []

    if len(contours_list) >= 2:
        con1 = contours_list[-1]
        con2 = contours_list[-2]
        final.append(con1)
        final.append(con2)

    cv2.drawContours(cropped, final, -1, (255, 0, 0), 3)

    return cropped


def filters(frame):
    height, width, _ = frame.shape
    cropped = frame[350:height-2].copy()

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, 150, 300)

    processed = detect_lines(edges, cropped)

    frame[350:height-2] = processed

    cv2.imshow('blurred', blurred)
    cv2.imshow('edges', edges)

    return frame


def overlay_arrow(frame, arrow):
    height, width, _ = arrow.shape  # takes shape of arrow png

    # resize arrow to 20% of its original size
    height = int(height * 0.2);
    width = int(width * 0.2)
    arrow = cv2.resize(arrow, (height, width))

    arrow_bgr = arrow[:, :, :3]  # extract bgr channels of the arrow
    arrow_alpha = arrow[:, :, 3]  # extract the alpha (transparency) channel

    # create a designated region in the video for the arrow overlay
    # the arrow will be overlayed in the top right corner (850, 10)
    roi = frame[10:10 + height, 850:850 + width]

    # alpha channel is normalized to range from 0.0 to 1.0
    mask = arrow_alpha.astype(float) / 255.0

    # iterates through each color channel of the roi, then blends
    # it with the arrow image
    for x in range(3):
        roi[:, :, x] = (mask * arrow_bgr[:, :, x] + (1 - mask) * roi[:, :, x])
        # multiplies arrow's color channel by the alpha value, then the roi's
        # color channel by 1 - alpha value to correctly overlay the arrow

    # return final video frame with arrow overlay
    return frame


camera = cv2.VideoCapture('video.mov')  # read fro the video file

# checks to see if camera is reading from the file correctly
if not camera.isOpened():
    print('failed to connect')  # debugging message
    exit()

while True:
    ret, frame = camera.read()  # read each frame of the video

    if not ret:
        print('failed to get frame')  # debugging message
        break

    frame = cv2.resize(frame, (960, 540))  # resizes frame to around half its size
    # read arrow png, uses imread_unchanged to preserve alpha channels
    up_arrow = cv2.imread('uparrow.png', cv2.IMREAD_UNCHANGED)

    filtered = filters(frame)
    # overlay the arrow transparent png onto the video frame
    # final = overlay_arrow(filtered.copy(), up_arrow)

    # show each frame with the overlay attached
    cv2.imshow('filter', filtered)
    # cv2.imshow("og video", final)

    # exits video if any other key is pressed
    if cv2.waitKey(1) != -1:
        break
