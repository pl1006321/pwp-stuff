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

    cropped = img[100:height - 100, 100:width - 100] # makes a cropped roi 

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY) # make grayscale 
    blurred = cv2.GaussianBlur(gray, (5, 5), 0) # apply gaussian blur 
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3) # detect edges 

    # use morphological closing to close in gaps 
    kernel = np.ones((15, 15), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # detects hough lines
    lines = cv2.HoughLinesP(closed, rho=1, theta=np.pi / 180, threshold=50, minLineLength=30)
    points1 = []
    points2 = []
    if lines is not None:
        x1, y1, x2, y2 = lines[0][0]
        start_angle = calc_angle(x1, y1, x2, y2) # create an initial angle for comparison
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = calc_angle(x1, y1, x2, y2)
            # sort lines by angle 
            if abs(start_angle - angle) < 25:
                points1.append([x1, y1, x2, y2])
            else:
                points2.append([x1, y1, x2, y2])

    points1 = np.array(points1)
    points2 = np.array(points2)

    if len(points1) < 1 or len(points2) < 1:
        return img

    # create a line of best fit for both lines 
    red = green = blue = yellow = None
    try:
        slope, intercept = np.polyfit(points1[:, 0], points1[:, 1], 1)
        x1, x2 = min(points1[:, 0]), max(points1[:, 0])
        y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

        red, yellow = (int(x1), int(y1)), (int(x2), int(y2))
        # cv2.circle(cropped, red, 10, (0, 0, 255), -1)
        # cv2.circle(cropped, yellow, 10, (0, 255, 255), -1)

        degree = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        length = np.linalg.norm(np.array(red) - np.array(yellow))

        # if length <= 650 and not (60 < abs(degree) < 125):
        #     yellow = (int(x1+650), int((slope*(x1+650))+intercept))

        cv2.line(cropped, red, yellow, (0, 255, 0), 2)
        cv2.circle(cropped, red, 10, (0, 0, 255), -1)
        cv2.circle(cropped, yellow, 10, (0, 255, 255), -1)
    except:
        print('error with line of best fit with points1')

    try:
        slope, intercept = np.polyfit(points2[:, 0], points2[:, 1], 1)
        x3, x4 = min(points2[:, 0]), max(points2[:, 0])
        y3, y4 = (slope * x3 + intercept), (slope * x4 + intercept)

        green, blue = (int(x3), int(y3)), (int(x4), int(y4))
        # cv2.circle(cropped, green, 10, (0, 255, 0), -1)
        # cv2.circle(cropped, blue, 10, (255, 0, 0), -1)

        degree = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        length = np.linalg.norm(np.array(green) - np.array(blue))

        # if length <= 650 and not (60 < abs(degree) < 125):
        #     blue = (int(x1+650), int((slope*(x1+650))+intercept))

        cv2.line(cropped, green, blue, (0, 255, 0), 2)
        cv2.circle(cropped, green, 10, (0, 255, 0), -1)
        cv2.circle(cropped, blue, 10, (255, 0, 0), -1)
    except:
        print('error with line of best fit with points2')

    # calculate distance to find the shorter lines, then find the midpoints of each shorter line 
    if red and green and blue and yellow:
        red2green = np.linalg.norm(np.array(red) - np.array(green))
        red2blue = np.linalg.norm(np.array(red) - np.array(blue))
        shorter1 = green if red2green < red2blue else blue
        longer1 = blue if shorter1 == green else green
        midpoint1 = calc_midpoint(red, shorter1)

        yellow2green = np.linalg.norm(np.array(yellow) - np.array(green))
        yellow2blue = np.linalg.norm(np.array(yellow) - np.array(blue))
        shorter2 = green if yellow2green < yellow2blue else blue
        longer2 = blue if shorter2 == green else blue
        midpoint2 = calc_midpoint(yellow, shorter2)

        # ix, iy = calc_intersection(red, longer1, yellow, longer2)
        # if ix and iy:
        #     points = np.array([midpoint1, midpoint2, (ix, iy)])
        #     slope, intercept = np.polyfit(points[:, 0], points[:, 1], 1)
        #     x1 = int(min(points[:, 0]))
        #     x2 = int(max(points[:, 0]))
        #     y1 = int(slope*x1 + intercept)
        #     y2 = int(slope*x2 + intercept)
        #     cv2.line(cropped, (x1, y1), (x2, y2), (0, 0, 0), 2)
        
        # use the two midpoints to draw a centerline 
        cv2.line(cropped, midpoint1, midpoint2, (255, 0, 255), 2)

    # paste the cropped image back into the larger original image 
    img[100:height - 100, 100:width - 100] = cropped
    cv2.rectangle(img, (100, 100), (width - 100, height - 100), (255, 0, 0), 2)

    cv2.imshow('edges', edges)
    cv2.imshow('closed', closed)

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

    frame = cv2.flip(frame, 1) # flip horizontally for better navigation 
    overlay = apply_overlay(frame) # apply the overlay onto the video stream 

    cv2.imshow('vid stream', frame)
    cv2.imshow('vid overlay', overlay)

    if cv2.waitKey(1) != -1:
        break

camera.release()
cv2.destroyAllWindows()
