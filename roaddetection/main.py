import cv2
import numpy as np

def draw_lines(frame):
    copy = frame.copy()
    cv2.line(copy, (300, 750), (800, 550), (255, 0, 255), 10)
    cv2.line(copy, (800, 550), (1100, 550), (0, 0, 255), 10)
    cv2.line(copy, (1100, 550), (1600, 750), (0, 255, 0), 10)
    cv2.line(copy, (1600, 750), (300, 750), (255, 0, 0), 10)
    return copy

def draw_points(frame):
    copy = frame.copy()
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

camera = cv2.VideoCapture('video.mp4')

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
top left: (800, 550)
top right: (1100, 550)
bottom right: (1600, 750)
bottom left: (300, 750)
"""
