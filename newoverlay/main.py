import cv2
import numpy as np

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

cv2.imshow('image', image)
cv2.imshow('crop', cropped)
cv2.imshow('idk', masked)
print(image.shape)

cv2.waitKey(0)
cv2.destroyAllWindows()
