# this is for video of can rolling

import cv2
import numpy as np

def detect_circle(frame):
    img = frame.copy()

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # experimented with different types of blurring; found gaussian to be the most effective
    blurred = cv2.medianBlur(gray, 21)
    gaussian = cv2.GaussianBlur(gray, (23, 23), 0)
    bilateral = cv2.bilateralFilter(gray, 15, 200, 200)

    # edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)

    # kernel = np.ones((5, 5), np.uint8)
    # dilated = cv2.dilate(edges, kernel, iterations=1)

    circles = cv2.HoughCircles(gaussian, cv2.HOUGH_GRADIENT, 1, 200, param1=50, param2=50)

    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")
        for (h, k, r) in circles:
            # draw the circles
            cv2.circle(img, (h, k), r, (255, 0, 255), 5)
            cv2.circle(img, (h, k), 1, (0, 0, 255), -1)

    return img


cam = cv2.VideoCapture('video10.mov')

while cam.isOpened():
    # read each frame
    ret, frame = cam.read()

    if ret:
        # resize the image while maintaining the aspect ratio
        height, width, _ = frame.shape
        frame = cv2.resize(frame, (600, int(height * 600 / width)))

        # apply overlay function onto the frame
        overlay = detect_circle(frame)

        # show the original video
        cv2.imshow('og', frame)
        # show video with overlay
        cv2.imshow('overlay', overlay)

        # press q to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    # break the loop once no more frames are left (video has ended)
    else:
        break

cam.release()

# close all windows once video has ended 
cv2.destroyAllWindows()
