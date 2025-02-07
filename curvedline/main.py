import cv2
import numpy as np

# processes the image by applying filters like 
# grayscale, blurring, and canny edge in order 
# to clean up image for further processing 
def process_img(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # converts image to grayscale 
    blurred = cv2.GaussianBlur(gray, (21, 21), 0)  # apply gaussian blur
    edges = cv2.Canny(blurred, 30, 80, apertureSize=3)  # detect edges

    # use morphological closing to close in gaps
    kernel = np.ones((41, 41), np.uint8)
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    return closed # returns final processed img to be used for contour detection 

# takes each frame of a live video stream, then
# uses basic filtering and processing to clean
# image. then, uses advanced contour detection algs
# and other math algs to detect a curved centerline
def apply_overlay(frame):
    img = frame.copy()
    height, width, _ = img.shape

    cropped = img[100:height - 100, 200:width - 200]  # makes a cropped roi

    processed = process_img(cropped) # process the image 

    # find the contours of the image 
    contours, _ = cv2.findContours(processed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) 
    contours_list = list(contours)
    contours_list.sort(key=cv2.contourArea) # sort contours by area 

    middle_pts = []

    # makes sure at least two contours r found
    if len(contours_list) >= 2:
        # two largest contours will always be the two lines 
        con1 = contours_list[-1]
        con2 = contours_list[-2]

        # uses cv2's approximate polynomial func to detect a polynomial 
        line1 = cv2.approxPolyDP(con1, 6, True)
        # divides by 2 so instead of detecting a full outline, it detects half 
        # of the outline -> a singular line representative of the path 
        line1 = line1[:int(len(line1)/1.68)] 
        # draw the polyline defined by the points which defines the longer path in blue 
        cv2.polylines(cropped, [line1], False, (255, 0, 0), 3, lineType=cv2.LINE_AA) 

        # repeats the same process for the shorter line 
        line2 = cv2.approxPolyDP(con2, 6, True)
        line2 = line2[:int(len(line2)/1.65)]
        cv2.polylines(cropped, [line2], False, (255, 0, 0), 3, lineType=cv2.LINE_AA)

        # sort through corresponding points of each line and calculate the
        # midpoint. these midpoints will define the centerline 
        for coords1, coords2 in zip(line1, line2):
            x1, y1 = coords1[0]
            x2, y2 = coords2[0]

            midx = int((x1 + x2) / 2)
            midy = int((y1 + y2) / 2)
            middle_pts.append([midx, midy])

        # manually add the last point of the centerline to ensure its 
        # length corresponds with the longer line's length 
        if len(line1) > 1 and len(line2) > 1: # in case lists are empty 
            x1, y1 = line1[-1][0]
            x2, y2 = line2[-1][0]

            mid_x = int((x1+x2) / 2)
            mid_y = int((y1+y2) / 2)
            middle_pts.append([mid_x, mid_y])

        middle_pts = np.array(middle_pts, dtype=np.int32)

    # draw the centerline in pink 
    if len(middle_pts) > 0:
        cv2.polylines(cropped, [middle_pts], False, (255, 0, 255), 4, lineType=cv2.LINE_AA)

    # pastes cropped image back into the original full image
    img[100:height - 100, 200:width - 200] = cropped
    # draw a rectangle around the mask 
    cv2.rectangle(img, (200, 100), (width - 200, height - 100), (255, 0, 0), 2)

    return img # return fully processed image with centerline overlay 

camera = cv2.VideoCapture(0) # initializes camera for capturing vid stream 

if not camera.isOpened(): # check if opened correctly 
    print("failed to connect to camera") # error handling and debugging 
    exit()

# loop to continously read and display each frame of the video stream 
while True:
    ret, frame = camera.read() # read a frame from camera 

    if not ret:
        print("failed to get frame") # if frame reading failed 
        break

    frame = cv2.flip(frame, 1)  # flip horizontally for better navigation
    overlay = apply_overlay(frame)  # apply the overlay onto the video stream

    # shows video stream and overlay for reference 
    cv2.imshow('vid stream', frame)
    cv2.imshow('vid overlay', overlay)

    # breaks loop once any key is pressed
    if cv2.waitKey(1) != -1:
        break

# release camera and close all opencv windows
camera.release()
cv2.destroyAllWindows()
