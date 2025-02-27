import cv2
import numpy as np

def get_points(time):
    set1 = [[200, 525], [475, 375], [615, 375], [800, 525]]
    set2 = [[250, 525], [500, 375], [650, 375], [850, 525]]
    set3 = [[200, 525], [425, 400], [590, 400], [790, 525]]
    set4 = [[200, 525], [450, 390], [600, 390], [850, 525]]

    if 0.03 <= time <= 1.80:
        return set1
    elif 1.83 <= time <= 6.60:
        return set2
    elif 6.63 <= time <= 9.33:
        return set3
    elif 9.33 <= time <= 14.40:
        return set4

def pers_trans(frame, points):
    src_pts = np.float32(points)
    dst_pts = np.float32([[0, 500], [0, 0], [500, 0], [500, 500]])

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(frame, matrix, (500, 500))

    # for i in range(4):
    #     cv2.line(frame, points[i % 4], points[(i + 1) % 4], (255, 0, 0), 3)

    return frame, warped

def unwarp(warped, points):
    src_pts = np.float32([[0, 500], [0, 0], [500, 0], [500, 500]])
    dst_pts = np.float32(points)

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    unwarped = cv2.warpPerspective(warped, matrix, (960, 540))

    return unwarped

def filters(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (9, 9), 0)

    masked = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 71, -30)

    return masked

def template_match(warped, template):
    final = warped.copy()
    print(template.shape)

    result = cv2.matchTemplate(warped, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.5

    loc = np.where(result >= threshold)
    x_coords = []; y_coords = []
    for point in zip(*loc[::-1]):
        x1, y1 = point
        x_coords.append(x1); y_coords.append(y1)

    avg_x = int(sum(x_coords)/len(x_coords))
    avg_y = int(sum(y_coords)/len(y_coords))

    return avg_x, avg_y


def detect_lines(frame, final):
    thinned = cv2.ximgproc.thinning(frame)

    dilated = cv2.dilate(thinned, np.ones((5, 5), np.uint8), iterations=1)
    
    lines = cv2.HoughLinesP(dilated, 1, np.pi/180, 10, minLineLength=40, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(final, (x1, y1), (x2, y2), (0, 255, 0), 6)
    
    return final

camera = cv2.VideoCapture('video.mov')
fps = camera.get(cv2.CAP_PROP_FPS)

if not camera.isOpened():
    print('failed to connect')
    exit()

while True:
    ret, frame = camera.read()

    if not ret:
        print('failed to get frame')
        break

    frame = cv2.resize(frame, (960, 540))

    frame_count = int(camera.get(cv2.CAP_PROP_POS_FRAMES))
    time = frame_count / fps

    print(f'{time:.2f}')

    points = get_points(time)
    original, warped = pers_trans(frame, points)
    filtered = filters(warped.copy())
    matched_x, matched_y = template_match(warped, cv2.imread('rightturn_temp.png'))
    lines = detect_lines(filtered, warped.copy())

    unwarped = unwarp(lines, points)
    # cv2.rectangle(frame, (matched_x, matched_y,), )
    final = cv2.addWeighted(frame, 0.5, unwarped, 0.8, 0)

    cv2.imshow('frame', original)
    cv2.imshow('warp perspective', warped)
    cv2.imshow('filtered', filtered)
    cv2.imshow('final', final)


    if cv2.waitKey(1) != -1:
        break
