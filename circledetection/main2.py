import cv2
import numpy as np

def detect_circle(frame):
    img = frame.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    blurred = cv2.medianBlur(gray, 21)
    gaussian = cv2.GaussianBlur(gray, (23, 23), 0)
    bilateral = cv2.bilateralFilter(gray, 15, 200, 200)

    # edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)

    # kernel = np.ones((5, 5), np.uint8)
    # dilated = cv2.dilate(edges, kernel, iterations=1)

    circles = cv2.HoughCircles(gaussian, cv2.HOUGH_GRADIENT, 1, 250, param1=50, param2=120)

    count = 0
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (h, k, r) in circles:
            print(r)
            cv2.circle(img, (h, k), r, (255, 0, 255), 5)
            cv2.circle(img, (h, k), 1, (0, 0, 255), -1)
            count += 1

    if 
        r = None
    return img, r


cap = cv2.VideoCapture('video6.mov')

# Check if camera opened successfully
if (cap.isOpened() == False):
    print("Error opening video file")

# Read until video is completed
while (cap.isOpened()):

    # Capture frame-by-frame
    ret, frame = cap.read()
    height, width, _ = frame.shape
    frame = cv2.resize(frame, (600, int(height * 600 / width)))

    avg = 0
    frames = 0
    overlay, r = detect_circle(frame)

    if r is not None:
        avg += r
    frames += 1
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
print(f'average: {avg/frames}')
