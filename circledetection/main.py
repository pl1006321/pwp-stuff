import cv2
import numpy as np

img = cv2.imread('image3.png')

height, width, _ = img.shape
img = cv2.resize(img, (600, int(height*600/width)))
final = img.copy()

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blurred = cv2.medianBlur(gray, 9)
gaussian = cv2.GaussianBlur(gray, (9, 9), 0)

# edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)

# kernel = np.ones((5, 5), np.uint8)
# dilated = cv2.dilate(edges, kernel, iterations=1)

circles = cv2.HoughCircles(gaussian, cv2.HOUGH_GRADIENT, 1, 100, param1=50, param2=100)

count = 0
if circles is not None:
    circles = np.round(circles[0, :]).astype("int")
    for (h, k, r) in circles:
        cv2.circle(final, (h, k), r, (255, 0, 255), 4)
        cv2.circle(final, (h, k), 1, (0, 0, 255), -1)
        count += 1

print(f'{count} circle(s) detected')
print(final.shape)
cv2.imshow('og', img)
cv2.imshow('gray', gray)
cv2.imshow('gaussian', gaussian)
cv2.imshow('blur', blurred)
# cv2.imshow('edges', edges)
# cv2.imshow('dilation', dilated)
cv2.imshow('overlay', final)
cv2.waitKey(0)
cv2.destroyAllWindows()
