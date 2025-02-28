import cv2
import numpy as np

def get_points(time):
    set1 = [[200, 525], [475, 375], [615, 375], [800, 525]]
    set2 = [[250, 525], [500, 375], [650, 375], [850, 525]]
    set3 = [[250, 525], [490, 375], [600, 375], [850, 525]]
    set4 = [[200, 525], [425, 400], [590, 400], [790, 525]]
    set5 = [[200, 525], [450, 390], [600, 390], [850, 525]]

    if 0.03 <= time <= 1.80:
        return set1
    elif 1.83 <= time <= 6.33:
        return set2
    elif 6.33 <= time <= 8.26:
        return set3
    elif 8.26 <= time <= 9.33:
        return set4
    elif 9.33 <= time <= 14.40:
        return set5

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
    height, width, _ = template.shape

    result = cv2.matchTemplate(warped, template, cv2.TM_CCOEFF_NORMED)
    threshold = 0.45

    loc = np.where(result >= threshold)
    x_coords = []; y_coords = []
    for point in zip(*loc[::-1]):
        x1, y1 = point
        cv2.rectangle(warped, (x1, y1), (x1+width, y1+height), (255, 0, 255), 1)
        x_coords.append(x1); y_coords.append(y1)

    avg_x = np.average(x_coords) if len(x_coords) > 0 else None
    avg_y = np.average(y_coords) if len(y_coords) > 0 else None

    if avg_x is None or avg_y is None:
        return None, None
    else:
        return (avg_x, avg_y), (avg_x + width, avg_y + height)


def detect_lines(frame, final, p1 = None, p2 = None):
    thinned = cv2.ximgproc.thinning(frame)
    roi_x1, roi_y1 = p1 if p1 is not None else [None, None]
    roi_x2, roi_y2 = p2 if p2 is not None else [None, None]

    dilated = cv2.dilate(thinned, np.ones((5, 5), np.uint8), iterations=1)
    
    lines = cv2.HoughLinesP(dilated, 1, np.pi/180, 10, minLineLength=40, maxLineGap=10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if p1 is None and p2 is None:
                cv2.line(final, (x1, y1), (x2, y2), (0, 255, 0), 6)
            else:
                if not (roi_x1 <= x1 <= roi_x2 and roi_x1 <= x2 <= roi_x2 and roi_y1 <= y1 <= roi_y2):
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
    temp_p1, temp_p2 = template_match(warped, cv2.imread('rightturn_temp.png'))
    lines = detect_lines(filtered, warped.copy(), temp_p1, temp_p2)

    unwarped = unwarp(lines, points)
    final = cv2.addWeighted(frame, 0.5, unwarped, 0.8, 0)

    cv2.imshow('frame', original)
    cv2.imshow('warp perspective', warped)
    cv2.imshow('filtered', filtered)
    cv2.imshow('final', final)


    if cv2.waitKey(1) != -1:
        break
