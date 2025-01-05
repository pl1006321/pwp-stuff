import cv2
import numpy as np

def calc_angle(x1, y1, x2, y2):
    angle = np.degrees(np.arctan2(y2-y1, x2-x1))
    return angle

def calc_midpoint(point1, point2):
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))

def apply_overlay(frame):
    img = frame.copy() 
    cropped = img[220:920, 500:1450]
    # (500, 220), (1450, 920)

    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

    kernel = np.ones((7, 7), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    lines = cv2.HoughLinesP(closed, rho=1, theta=np.pi/180, threshold=50, minLineLength=30)
    points1 = []
    points2 = []
    if lines is not None:
            x1, y1, x2, y2 = lines[0][0]
            start_angle = calc_angle(x1, y1, x2, y2)
            for line in lines: 
                x1, y1, x2, y2 = line[0]
                angle = calc_angle(x1, y1, x2, y2)
                if abs(start_angle - angle) < 25:
                    points1.append([x1, y1, x2, y2])
                else:
                    points2.append([x1, y1, x2, y2])

    points1 = np.array(points1)
    points2 = np.array(points2)

    if len(points1) < 1 or len(points2) < 1:
        return img

    red = green = blue = yellow = None
    try:
        slope, intercept = np.polyfit(points1[:, 0], points1[:, 1], 1)
        x1, x2 = min(points1[:, 0]), max(points1[:, 0])
        y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

        red, yellow = (int(x1), int(y1)), (int(x2), int(y2))
        # cv2.circle(cropped, red, 10, (0, 0, 255), -1)
        # cv2.circle(cropped, yellow, 10, (0, 255, 255), -1)

        degree = np.degrees(np.arctan2(y2-y1, x2-x1))
        length = np.linalg.norm(np.array(red) - np.array(yellow))

        if length <= 650 and not (60 < abs(degree) < 125):
            yellow = (int(x1+650), int((slope*(x1+650))+intercept))    

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

        degree = np.degrees(np.arctan2(y2-y1, x2-x1))
        length = np.linalg.norm(np.array(green) - np.array(blue))

        if length <= 650 and not (60 < abs(degree) < 125):
            blue = (int(x1+650), int((slope*(x1+650))+intercept))

        cv2.line(cropped, green, blue, (0, 255, 0), 2)
        cv2.circle(cropped, green, 10, (0, 255, 0), -1)
        cv2.circle(cropped, blue, 10, (255, 0, 0), -1)
    except:
        print('error with line of best fit with points2')

    if red and green and blue and yellow: 
        red2green = np.linalg.norm(np.array(red) - np.array(green))
        red2blue = np.linalg.norm(np.array(red)-np.array(blue))
        shorter1 = green if red2green < red2blue else blue 
        midpoint1 = calc_midpoint(red, shorter1)

        yellow2green = np.linalg.norm(np.array(yellow) - np.array(green))
        yellow2blue = np.linalg.norm(np.array(yellow) - np.array(blue))
        shorter2 = green if yellow2green < yellow2blue else blue 
        midpoint2 = calc_midpoint(yellow, shorter2)

        cv2.line(cropped, midpoint1, midpoint2, (255, 0, 255), 2)
    
    img[220:920, 500:1450] = cropped
    cv2.rectangle(img, (500, 220), (1450, 920), (255, 0, 0), 2)

    cv2.imshow('edges', edges)
    cv2.imshow('closed', closed)

    return img

camera = cv2.VideoCapture(1)

if not camera.isOpened():
    print("Error: Could not open the camera.")
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print("Failed to grab frame")
        break

    frame = cv2.flip(frame, 1)
    overlay = apply_overlay(frame)

    cv2.imshow('vid stream', frame)
    cv2.imshow('vid overlay', overlay)

    if cv2.waitKey(1) != -1:
        break

camera.release()
cv2.destroyAllWindows()
