import cv2
import numpy as np

image = cv2.imread('image.png') # change to file path

# List to store points
points = []

cv2.circle(image, (868, 1384), 5, (255, 0, 0), -1)
cv2.circle(image, (1484, 980), 5, (255, 0, 0), -1)
cv2.circle(image, (1887, 980), 5, (255, 0, 0), -1)
cv2.circle(image, (2437, 1384), 5, (255, 0, 0), -1)

# Load and display the image
cv2.imshow("Image", image)
cv2.waitKey(0)

# (868, 1384)
# (1484, 970)
# 1887, 980
# 2437, 1383
