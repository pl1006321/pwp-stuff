import cv2
import numpy as np

img = cv2.imread('image6.png')
final = img.copy()

height, width, _ = img.shape
# cv2.resize()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# blurred = cv2.medianBlur(gray, 7)
gaussian = cv2.GaussianBlur(gray, (15, 15), 0)
edges = cv2.Canny(gray, 50, 150, apertureSize=3)
circles = cv2.HoughCircles(gaussian, cv2.HOUGH_GRADIENT, 1, 20, param1=50, param2=100)

if circles is not None:
    circles = np.uint16(np.around(circles))

    for circle in circles[0, :]:
        h, k, r = circle[0], circle[1], circle[2]
        cv2.circle(final, (h, k), r, (255, 0, 255), 2)
        cv2.circle(final, (h, k), 1, (0, 0, 255), -1)


cv2.imshow('og', img)
cv2.imshow('gray', gray)
cv2.imshow('edges', gaussian)
cv2.imshow('overlay', final)
cv2.waitKey(0)
cv2.destroyAllWindows()
