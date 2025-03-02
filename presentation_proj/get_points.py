import cv2
import numpy as np

image = cv2.imread('ihateopencv/images/road.png') # change to file path

# List to store points
points = []

def get_points(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        points.append([x, y])
        print(f"Point selected: {x, y}")
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)  # Visual feedback
        cv2.imshow("Image", image)
        if len(points) == 4:
            print("All points selected.")
            cv2.destroyAllWindows()

# Load and display the image
cv2.imshow("Image", image)
cv2.setMouseCallback("Image", get_points)
cv2.waitKey(0)
