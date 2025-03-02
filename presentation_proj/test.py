import cv2
import numpy as np

og_image = cv2.imread('road2.png')

# og_pts = np.float32([[601, 392], [783, 388], [25, 772], [1115, 769]])
og_pts = np.float32([[411, 227], [952, 217], [34, 688], [1269, 717]])
dst_pts = np.float32([[0, 0], [300, 0], [0, 300], [300, 300]])

matrix = cv2.getPerspectiveTransform(og_pts, dst_pts)
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))  # Adjust kernel size as needed

warped = cv2.warpPerspective(og_image, matrix, (300, 300))

hsv = cv2.cvtColor(warped, cv2.COLOR_BGR2HSV)

lower_blue = np.array([100, 50, 50])
upper_blue = np.array([140, 255, 255])
mask = cv2.inRange(hsv, lower_blue, upper_blue)

masked = cv2.bitwise_and(warped, warped, mask=mask)
dilated_mask = cv2.dilate(mask, kernel, iterations=1)
closed = cv2.morphologyEx(dilated_mask, cv2.MORPH_CLOSE, kernel)
improved_masked = cv2.bitwise_and(warped, warped, mask=closed)

gray = cv2.cvtColor(improved_masked, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

dilated = cv2.dilate(edges, kernel, iterations=1)

# lines = cv2.HoughLines(dilated, rho=1, theta=np.pi/180, threshold=300,)
lines = cv2.HoughLinesP(dilated, rho=1, theta=np.pi/180, threshold=50, minLineLength=30, maxLineGap=50)

warped_copy = warped.copy()
xvals1 = []; yvals1 = []
xvals2 = []; yvals2 = []

if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        slope = (y2 - y1) / (x2 - x1) if x2 != x1 else None
        if slope is None or abs(slope) <= 1:
            continue
        mid_x = int((x1+x2)/2)
        print(f'mid x: {mid_x}')
        print(f'width: {warped_copy.shape[1]}')
        if mid_x < int(warped_copy.shape[1] / 2):
            xvals1.append(mid_x)
            yvals1.append(y1); yvals1.append(y2)
        else:
            xvals2.append(mid_x)
            yvals2.append(y1); yvals2.append(y2)
        print(f'x1: {x1}, y1: {y1}, x2: {x2}, y2: {y2}')
        # cv2.line(warped_copy, (x1, y1), (x2, y2), (0, 0, 255), 1)

print(f'xvals1: {xvals1}')
print(f'xvals2: {xvals2}')
print(f'yvals1: {yvals1}')
print(f'yvals2: {yvals2}')

left_x = int(sum(xvals1) / len(xvals1)) if xvals1 is not None else None
right_x = int(sum(xvals2) / len(xvals2)) if xvals2 is not None else None
y_values = yvals1 + yvals2

if left_x and right_x:
    cv2.line(warped_copy, (left_x, min(yvals1)), (left_x, max(yvals2)), (0, 255, 0), 5)
    cv2.line(warped_copy, (right_x, min(yvals1)), (right_x, max(yvals2)), (0, 255, 0), 5)
    mid_x = int((left_x + right_x)/2)
    cv2.line(warped_copy, (mid_x, min(y_values)), (mid_x, max(y_values)), (255, 0, 0), 15)

# if xvals and yvals:
#     try:
#         mid_x = int((max(xvals) + min(xvals))/2)
#         cv2.line(warped_copy, (mid_x, min(yvals)), (mid_x, max(yvals)), (255, 0, 0), 15)
#     except:
#         pass


# for line in lines:
#     rho, theta = line[0]
#     a = np.cos(theta)
#     b = np.sin(theta)
#     x0 = a * rho
#     y0 = b * rho
#     x1 = int(x0 + 1000 * (-b))
#     y1 = int(y0 + 1000 * (a))
#     x2 = int(x0 - 1000 * (-b))
#     y2 = int(y0 - 1000 * (a))
#     cv2.line(warped_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)

inverse_matrix = cv2.getPerspectiveTransform(dst_pts, og_pts)
overlay_img = cv2.warpPerspective(warped_copy, inverse_matrix, (og_image.shape[1], og_image.shape[0]))

blended = cv2.addWeighted(og_image, 0.8, overlay_img, 0.4, 0)

cv2.imshow('og image', og_image)
cv2.imshow('warped', warped)
cv2.imshow('final mask', improved_masked)
cv2.imshow('blurred', blurred)
cv2.imshow('canny edged', edges)
cv2.imshow('dilated', dilated)
cv2.imshow('overlay', warped_copy)
cv2.imshow('final overlay', blended)
cv2.waitKey(0)
cv2.destroyAllWindows
