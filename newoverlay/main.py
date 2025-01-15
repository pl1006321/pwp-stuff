import cv2
import numpy as np

def calc_angle(x1, y1, x2, y2): 
    angle = np.degrees(np.arctan2(y2-y1, x2-x1))
    return angle

def calc_midpoint(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return (int((x1 + x2) / 2), int((y1 + y2) / 2))

def calc_distance(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return np.sqrt(np.square(y2-y1) + np.square(x2-x1))

# def calc_intersection(p1, p2, p3, p4):
#     x1, y1 = p1
#     x2, y2 = p2
#     x3, y3 = p3
#     x4, y4 = p4

#     denom = (x1-x2) * (y3-y4) - (y1-y2) * (x3-x4)
#     if not denom:
#         return
    
#     px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
#     py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom

#     return int(px), int(py)

image = cv2.imread('images/path2.png')
image = cv2.resize(image, (1280, 960))
final = image.copy()

# cv2.rectangle(image, (0, 375), (1280, 960), (255, 0, 0), 2)
cropped = final[100:960, 0:1280]

hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

lower_blue = np.array([0, 80, 0])
upper_blue = np.array([140, 255, 200])

mask = cv2.inRange(hsv, lower_blue, upper_blue)
dilated = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
final_mask = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))

masked = cv2.bitwise_and(cropped, cropped, mask=final_mask)

gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
gaussian = cv2.GaussianBlur(gray, (7, 7), 0)
edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)
dilated = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)
eroded = cv2.erode(dilated, np.ones((3, 3), np.uint8))

lines = cv2.HoughLinesP(eroded, rho=1, theta=np.pi/180, threshold=10, minLineLength=30)
points1 = []
points2 = []
if lines is not None:
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = calc_angle(x1, y1, x2, y2)

        if abs(angle) < 20:
            continue

        print(angle)
        # cv2.line(cropped, (x1, y1), (x2, y2), (255, 0, 0), 1)
        if angle > 0:
            points1.append([x1, y1, x2, y2])
        else:
            points2.append([x1, y1, x2, y2])

points1 = np.array(points1)
points2 = np.array(points2)

p1 = p2 = p3 = p4 = None

try:
    slope, intercept = np.polyfit(points1[:, 0], points1[:, 1], 1)
    x1, x2 = min(points1[:, 0]), max(points1[:, 0])
    y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

    p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
    cv2.line(cropped, p1, p2, (0, 255, 0), 3)
except:
    print('error with line of best fits with points1')

try:
    slope, intercept = np.polyfit(points2[:, 0], points2[:, 1], 1)
    x1, x2 = min(points2[:, 0]), max(points2[:, 0])
    y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

    p3, p4 = (int(x1), int(y1)), (int(x2), int(y2))
    cv2.line(cropped, p3, p4, (0, 255, 0), 3)
except:
    print('error with line of best fit with points2')

if p1 and p2 and p3 and p4:
    midpoint1 = calc_midpoint(p1, p2)
    midpoint2 = calc_midpoint(p3, p4)

    p1_p3 = calc_distance(p1, p3)
    p1_p4 = calc_distance(p1, p4)
    shorter1 = p3 if p1_p3 < p1_p4 else p4
    center1 = calc_midpoint(p1, shorter1)

    shorter2 = p4 if shorter1 == p3 else p3 
    center2 = calc_midpoint(p2, shorter2)

    # center3 = calc_intersection(shorter1, midpoint1, p1, shorter2)
    # center4 = calc_intersection(midpoint1, shorter2, midpoint2, p2)

    # cv2.circle(cropped, center1, 10, (0, 0, 255), -1)
    # cv2.circle(cropped, center2, 10, (0, 0, 255), -1)
    # cv2.circle(cropped, center3, 10, (0, 0, 255), -1)
    # cv2.circle(cropped, center4, 10, (0, 0, 255), -1)
    # print(f'center: {center1, center2, center3, center4}')
    
    # centerline = np.array([center1, center2, center3, center4])
    # slope, intercept = np.polyfit(centerline[:, 0], centerline[:, 1], 1)
    # x1, x2 = min(centerline[:, 0]), max(centerline[:, 0])
    # y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

    # c1, c2 = (int(x1), int(y1)), (int(x2), int(y2))
    # cv2.line(cropped, c1, c2, (255, 0, 255), 2)
    cv2.line(cropped, center1, center2, (255, 0, 255), 3)


final[100:960, 0:1280] = cropped

cv2.imshow('image', image)
cv2.imshow('masked', masked)
cv2.imshow('edges', eroded)
cv2.imshow('cropped', cropped)
cv2.imshow('final', final)

cv2.waitKey(0)
cv2.destroyAllWindows()
