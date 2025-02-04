import cv2
import numpy as np


def calc_angle(x1, y1, x2, y2):
    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    return angle


def calc_midpoint(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))


# def calc_intersection(p1, p2, p3, p4):
#     x1, y1 = p1
#     x2, y2 = p2
#     x3, y3 = p3
#     x4, y4 = p4

#     denom = (x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)
#     if denom == 0:
#         return None

#     px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
#     py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

#     return int(px), int(py)

def apply_overlay(frame):
    img = frame.copy()
    height, width, _ = img.shape

    cropped = img[50:height - 50, 100:width - 100]  # makes a cropped roi

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)  # make grayscale
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)  # apply gaussian blur
    edges = cv2.Canny(blurred, 50, 100, apertureSize=3)  # detect edges

    # use morphological closing to close in gaps 
    kernel = np.ones((21, 21), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    copy = closed.copy()

    # lines = cv2.HoughLinesP(closed, rho=1, theta=np.pi/180, threshold=50, minLineLength=30)
    # if lines is not None:
    #     x1, y1, x2, y2 = lines[0][0]
    #     cv2.line(cropped, (x1, y1), (x2, y2), (255, 0, 0), 3)

    contours, _ = cv2.findContours(copy, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours_list = list(contours)
    contours_list.sort(key=cv2.contourArea)

    middle_pts = []

    if len(contours_list) >= 2:
        con1 = contours_list[-1]
        con2 = contours_list[-2]

        line1 = cv2.approxPolyDP(con1, 8, True)
        line1 = line1[:int(len(line1)/1.3)]
        cv2.drawContours(cropped, [line1], -1, (255, 0, 0), 3)

        line2 = cv2.approxPolyDP(con2, 8, True)
        line2 = line2[:int(len(line1)/1.3)]
        cv2.drawContours(cropped, [line2], -1, (255, 0, 0), 3)

        for coords1, coords2 in zip(line1, line2):
            x1, y1 = coords1[0]
            x2, y2 = coords2[0]

            midx = int((x1 + x2) / 2)
            midy = int((y1 + y2) / 2)
            middle_pts.append([midx, midy])

            # middle_pts = [[x1, y1], [x2, y2]...]

    middle_pts = np.array(middle_pts, dtype=np.int32)

    if len(middle_pts) > 0:
        cv2.polylines(cropped, [middle_pts], False, (255, 0, 255), 4)

    img[50:height - 50, 100:width - 100] = cropped
    cv2.rectangle(img, (100, 50), (width - 100, height - 50), (255, 0, 0), 2)

    cv2.imshow('canny', edges)
    cv2.imshow('closed', closed)
    cv2.imshow('contours', copy)

    return img


camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("failed to connect to camera")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print("failed to get frame")
        break

    frame = cv2.flip(frame, 1)  # flip horizontally for better navigation
    overlay = apply_overlay(frame)  # apply the overlay onto the video stream

    cv2.imshow('vid stream', frame)
    cv2.imshow('vid overlay', overlay)

    if cv2.waitKey(1) != -1:
        break

camera.release()
cv2.destroyAllWindows()
