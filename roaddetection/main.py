import cv2
import numpy as np

def draw_lines(frame):
    copy = frame.copy()
    height, width, _ = copy.shape
    cv2.line(copy, (0, height-100), (0, int(height*3/5)), (255, 0, 255), 10)
    cv2.line(copy, (0, int(height*3/5)), (width, int(height*3/5)), (0, 0, 255), 10)
    cv2.line(copy, (width, int(height*3/5)), (width, height-100), (0, 255, 0), 10)
    cv2.line(copy, (width, height-100), (0, height-100), (255, 0, 0), 10)
    return copy

def draw_points(frame):
    copy = frame.copy()
    height, width, _ = copy.shape
    cv2.circle(copy, (300, 750), 10, (255, 0, 0), -1)
    cv2.circle(copy, (800, 550), 10, (0, 255, 0), -1)
    cv2.circle(copy, (1100, 550), 10, (0, 0, 255), -1)
    cv2.circle(copy, (1600, 750), 10, (255, 0, 255), -1)
    return copy

def pers_trans(frame):
    copy = frame.copy()

    og_pts = np.float32([[800, 550], [1100, 550], [1600, 750], [300, 750]])
    dst_pts = np.float32([[0, 0], [300, 0], [300, 300], [0, 300]])

    matrix = cv2.getPerspectiveTransform(og_pts, dst_pts)
    warped = cv2.warpPerspective(copy, matrix, (300, 300))

    return warped

camera = cv2.VideoCapture('video2.mov')

if not camera.isOpened():
    print('failed to connect')
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print('failed to get frame')
        break

    mask = draw_lines(frame)
    warped = pers_trans(frame)

    cv2.imshow("og video", frame)
    cv2.imshow('mask', mask)
    cv2.imshow('test', warped)

    if cv2.waitKey(1) != -1:
        break

"""
idea: use cv2 approx poly dp so get an approximate outline (works for both curved and uncurved lines)
using those points, make an roi 
then after getting an roi you can perspective transform and use contour detection again
so use cv2 approx poly dp again except with more specificity if ykwim 
then either use houghlines or contours from this point to detect lines then make a centerline and unwarp
"""
