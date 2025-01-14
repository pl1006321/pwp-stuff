import cv2
import numpy as np

def calc_angle(x1, y1, x2, y2): 
    angle = np.degrees(np.arctan2(y2-y1, x2-x1))
    return angle

kernel = np.ones((5, 5), np.uint8)

image = cv2.imread('path2.png')
image = cv2.resize(image, (1280, 960))
final = image.copy()

# cv2.rectangle(image, (0, 375), (1280, 960), (255, 0, 0), 2)
cropped = final[375:960, 0:1280]

hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

lower_blue = np.array([100, 100, 50])
upper_blue = np.array([140, 255, 200])

mask = cv2.inRange(hsv, lower_blue, upper_blue)
dilated = cv2.dilate(mask, kernel, iterations=1)
final_mask = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, kernel)

masked = cv2.bitwise_and(cropped, cropped, mask=final_mask)

gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
gaussian = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)
dilated = cv2.dilate(edges, kernel, iterations=2)

lines = cv2.HoughLinesP(dilated, rho=1, theta=np.pi/180, threshold=100, minLineLength=50)
points1 = []
points2 = []
if lines is not None:
    index = 0
    while True:
        x1, y1, x2, y2 = lines[0][index]
        start_angle = calc_angle(x1, y1, x2, y2)
        if abs(start_angle) > 10:
            break
        index += 1
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = calc_angle(x1, y1, x2, y2)

        if abs(angle) < 10:
            continue

        if angle > 0:
            points1.append([x1, y1, x2, y2])
        else:
            points2.append([x1, y1, x2, y2])

points1 = np.array(points1)
points2 = np.array(points2)

slope, intercept = np.polyfit(points1[:, 0], points1[:, 1], 1)
x1, x2 = min(points1[:, 0]), max(points1[:, 0])
y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
cv2.line(cropped, p1, p2, (0, 255, 0), 2)

cv2.imshow('image', image)
cv2.imshow('crop', cropped)
cv2.imshow('masked', masked)
cv2.imshow('edges', dilated)
cv2.imshow('final', cropped)

cv2.waitKey(0)
cv2.destroyAllWindows()
