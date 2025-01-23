import cv2
import numpy as np

def detect_circle(frame):
    img = frame.copy()
    height, width, _ = img.shape
    img = cv2.resize(img, (600, int(height * 600 / width)))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.medianBlur(gray, 13)
    gaussian = cv2.GaussianBlur(gray, (15, 15), 0)

    # edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)

    # kernel = np.ones((5, 5), np.uint8)
    # dilated = cv2.dilate(edges, kernel, iterations=1)

    circles = cv2.HoughCircles(blurred, cv2.HOUGH_GRADIENT, 1, 200, param1=50, param2=100)

    count = 0
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (h, k, r) in circles:
            cv2.circle(img, (h, k), r, (255, 0, 255), 4)
            cv2.circle(img, (h, k), 1, (0, 0, 255), -1)
            count += 1

    return img


cap = cv2.VideoCapture('video2.mov')

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video file")

# Read until video is completed
while (cap.isOpened()):

    # Capture frame-by-frame
    ret, frame = cap.read()
    overlay = detect_circle(frame)
    if ret == True:
        # Display the resulting frame
        cv2.imshow('og', frame)
        cv2.imshow('overlay', overlay)
        # Press Q on keyboard to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # Break the loop
    else:
        break

# When everything done, release
# the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
