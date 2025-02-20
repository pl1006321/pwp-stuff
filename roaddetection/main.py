import cv2
import numpy as np

# top left: (0, int(height*3/5))
# top right: (width, int(height*3/5))
# bottom right: (width, height)
# bottom left: (0, height)

def draw_lines(frame):
    copy = frame.copy()
    height, width, _ = copy.shape
    cv2.line(copy, (0, height), (0, int(height*3/5)), (255, 0, 255), 10)
    cv2.line(copy, (0, int(height*3/5)), (width, int(height*3/5)), (0, 0, 255), 10)
    cv2.line(copy, (width, int(height*3/5)), (width, height), (0, 255, 0), 10)
    cv2.line(copy, (width, height), (0, height), (255, 0, 0), 10)
    return copy

def pers_trans(frame):
    copy = frame.copy()
    height, width, _ = copy.shape

    og_pts = np.float32([[0, int(height*3/5)], [width, int(height*3/5)], [width, height], [0, height]])
    dst_pts = np.float32([[0, 0], [500, 0], [500, 500], [0, 500]])

    matrix = cv2.getPerspectiveTransform(og_pts, dst_pts)
    warped = cv2.warpPerspective(copy, matrix, (500, 500))

    return warped

def filters(frame):
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    edges = cv2.Canny(blurred, 30, 80, apertureSize=3)

    # cv2.imshow('gray', gray)
    cv2.imshow('blurred', blurred)
    cv2.imshow('edged', edges)

def overlay_arrow(frame, arrow):
    height, width, _ = arrow.shape
    height = int(height*0.2); width = int(width*0.2)
    arrow = cv2.resize(arrow, (height, width))

    arrow_bgr = arrow[:, :, :3]
    arrow_alpha = arrow[:, :, 3]

    roi = frame[10:10+height, 850:850+width]
    mask = arrow_alpha.astype(float) / 255.0

    for x in range(3):
        roi[:, :, x] = (mask * arrow_bgr[:, :, x] + (1 - mask) * roi[:, :, x])

    return frame

camera = cv2.VideoCapture('video.mov')

if not camera.isOpened():
    print('failed to connect')
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print('failed to get frame')
        break

    frame = cv2.resize(frame, (960, 540))
    up_arrow = cv2.imread('uparrow.png', cv2.IMREAD_UNCHANGED)

    final = overlay_arrow(frame.copy(), up_arrow)

    # mask = draw_lines(frame)
    # warped = pers_trans(frame)
    # filters(warped)

    cv2.imshow("og video", final)
    # cv2.imshow('mask', mask)
    # cv2.imshow('test', warped)

    if cv2.waitKey(1) != -1:
        break

"""
idea: use cv2 approx poly dp so get an approximate outline (works for both curved and uncurved lines)
using those points, make an roi 
then after getting an roi you can perspective transform and use contour detection again
so use cv2 approx poly dp again except with more specificity if ykwim 
then either use houghlines or contours from this point to detect lines then make a centerline and unwarp
"""
