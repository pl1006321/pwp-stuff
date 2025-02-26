import cv2
import numpy as np

def get_points(time):
    set1 = [[200, 525], [475, 375], [615, 375], [800, 525]]
    set2 = [[250, 525], [500, 375], [650, 375], [850, 525]]
    set3 = [[200, 525], [450, 390], [600, 390], [850, 525]]

    if 0.03 <= time <= 2.00:
        return set1
    elif 2.03 <= time <= 6.60:
        return set2
    elif 6.63 <= time <= 14.10:
        return set3

def pers_trans(frame, points):

    src_pts = np.float32(points)
    dst_pts = np.float32([[0, 500], [0, 0], [500, 0], [500, 500]])

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(frame, matrix, (500, 500))

    for i in range(4):
        cv2.line(frame, points[i % 4], points[(i + 1) % 4], (255, 0, 0), 3)

    return frame, warped

def filtered(frame):
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)

    hsv =  cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 150])
    upper = np.array([255, 255, 255])

    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)

    return result

camera = cv2.VideoCapture('video.mov')
fps = camera.get(cv2.CAP_PROP_FPS)

if not camera.isOpened():
    print('failed to connect')
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print('failed to get frame')
        break

    frame = cv2.resize(frame, (960, 540))

    frame_count = int(camera.get(cv2.CAP_PROP_POS_FRAMES))
    time = frame_count / fps

    print(f'{time:.2f}')

    points = get_points(time)
    original, warped = pers_trans(frame, points)
    final = filtered(warped)

    cv2.imshow('frame', original)
    cv2.imshow('filtered', final)
    cv2.imshow('warp perspective', warped)

    if cv2.waitKey(1) != -1:
        break
