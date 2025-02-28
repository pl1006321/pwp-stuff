import cv2
import numpy as np

def get_points(time):
    set1 = [[200, 525], [475, 375], [615, 375], [800, 525]]
    set2 = [[250, 525], [500, 375], [650, 375], [850, 525]]
    set3 = [[200, 525], [425, 400], [590, 400], [790, 525]]
    set4 = [[200, 525], [450, 390], [600, 390], [850, 525]]

    if 0.03 <= time <= 1.80:
        return set1
    elif 1.83 <= time <= 6.60:
        return set2
    elif 6.63 <= time <= 9.33:
        return set3
    elif 9.33 <= time <= 14.40:
        return set4

def pers_trans(frame, points):
    src_pts = np.float32(points)
    dst_pts = np.float32([[0, 500], [0, 0], [500, 0], [500, 500]])

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(frame, matrix, (500, 500))

    # for i in range(4):
    #     cv2.line(frame, points[i % 4], points[(i + 1) % 4], (255, 0, 0), 3)

    return frame, warped

def unwarp(warped, points):
    src_pts = np.float32([[0, 500], [0, 0], [500, 0], [500, 500]])
    dst_pts = np.float32(points)

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    unwarped = cv2.warpPerspective(warped, matrix, (960, 540))

    return unwarped

def filters(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    masked = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 71, -30)

    return masked

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
    cv2.imshow('frame', frame)
    cv2.waitKey(1)

    if 6.50 <= time <= 6.53:
        image = frame
        break

"""
Point selected: (290, 504)
Point selected: (468, 388)
Point selected: (623, 385)
Point selected: (823, 518)
"""

# List to store points
points = []

def get_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        print(f"Point selected: {x, y}")
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # Visual feedback
        cv2.imshow("Image", image)
        if len(points) == 4:
            print("All points selected.")
            cv2.destroyAllWindows()

# Load and display the image
cv2.imshow("Image", image)
cv2.setMouseCallback("Image", get_points)
cv2.waitKey(0)
