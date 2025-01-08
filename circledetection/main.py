import cv2
import numpy as np

img = cv2.imread('image.png')
final = img.copy()

height, width, _ = img.shape
min_r = round(width/65)
max_r = round(width/11)
min_dis = round(width/7)

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.blur(gray, (20, 20), cv2.BORDER_DEFAULT)
circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, min_dis, param1=10, param2=40, minRadius=min_r, maxRadius=max_r, )

if circles is not None:
    circles = np.uint16(np.around(circles))
    for circle in circles[0, :]:
        h, k, r = circle[0], circle[1], circle[2]
        cv2.circle(final, (h, k), r, (0, 255, 0), 2)
        cv2.circle(final, (h, k), 1, (0, 0, 255), -1)

cv2.imshow('og', img)
cv2.imshow('gray', gray)
cv2.imshow('blurred', blurred)
cv2.imshow('overlay', final)
cv2.waitKey(0)
cv2.destroyAllWindows()
