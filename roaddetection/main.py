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
    cv2.circle(copy, (1400, 1000), 10, (255, 0, 0), -1)
    cv2.circle(copy, (2000, 1000), 10, (255, 0, 0), -1)
    cv2.circle(copy, (2500, 1400), 10, (255, 0, 0), -1)
    cv2.circle(copy, (700, 1400), 10, (255, 0, 0), -1)
    return copy

def pers_trans(frame):
    copy = frame.copy()
    
    og_pts = np.float32([[]])

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

    cv2.imshow("og video", frame)
    print(frame.shape)
    cv2.imshow('test', mask)

    if cv2.waitKey(1) != -1:
        break

"""
top left: (800, 550)
top right: (1100, 550)
bottom right: (1600, 750)
bottom left: (300, 750)
"""
