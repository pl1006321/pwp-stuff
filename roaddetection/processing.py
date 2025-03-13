import cv2
import numpy as np

leftline = rightline = None
current_dir = 'forward'

def set_current_dir(value):
    global current_dir
    current_dir = value

def get_current_dir():
    global current_dir
    return current_dir

def pers_trans(frame, points):
    src_pts = np.float32(points)
    dst_pts = np.float32([[0, 500], [0, 0], [500, 0], [500, 500]])

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(frame, matrix, (500, 500))

    # for i in range(4):
    #     cv2.line(frame, points[i % 4], points[(i + 1) % 4], (255, 0, 0), 3)

    return warped

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
    threshold = 0.7

    loc = np.where(result >= threshold)
    x_coords = []; y_coords = []
    for point in zip(*loc[::-1]):
        x1, y1 = point
        # cv2.rectangle(warped, (x1, y1), (x1+width, y1+height), (255, 0, 255), 1)
        x_coords.append(x1); y_coords.append(y1)

    avg_x = np.average(x_coords) if len(x_coords) > 0 else None
    avg_y = np.average(y_coords) if len(y_coords) > 0 else None

    if avg_x is None or avg_y is None:
        return None, None
    else:
        return (avg_x, avg_y), (avg_x + width, avg_y + height)
    
def polyfit_line(points):
    try: 
        slope, intercept = np.polyfit(points[:, 0], points[:, 1], 1)
        if abs(slope) >= 5:
            x1, x2 = int(min(points[:, 0])), int(max(points[:, 0]))
            y1, y2 = int((slope * x1 + intercept)), int((slope * x2 + intercept))
            # print('yay line!')
            if get_length(x1, y1, x2, y2) > 250:
                return [x1, y1, x2, y2]
            else:
                return None
    except Exception as e:
        return None
    
def get_length(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def detect_lines(frame, warped, arrow_temps, only_temps):
    global leftline, rightline, current_dir
    black = np.zeros_like(warped.copy(), dtype=np.uint8)
    thinned = cv2.ximgproc.thinning(frame)

    h, w, _ = black.shape

    dilated = cv2.dilate(thinned, np.ones((5, 5), np.uint8), iterations=1)

    template_pts = []
    for direction, template in arrow_temps.items():
        p1, p2 = template_match(warped, template)
        if p1 and p2:
            current_dir = direction
            template_pts.append((p1, p2))

    left_pts = []; right_pts = []

    lines = cv2.HoughLinesP(dilated, 1, np.pi/180, 10)
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            template_flag = False

            for p1, p2 in template_pts:
                p_x1, p_y1 = p1
                p_x2, p_y2 = p2

                if (p_x1 <= x1 <= p_x2 and p_y1 <= y1 <= p_y2) or (p_x1 <= x2 <= p_x2 and p_y1 <= y2 <= p_y2):
                    template_flag = True
                    break

            slope = (y2-y1)/(x2-x1) if x2-x1 != 0 else 300
            if (not template_flag) and abs(slope) > 5:
                if x1 < w/2 and x2 < w/2:
                    left_pts.append([x1, y1, x2, y2])
                elif x1 > w/2 and x2 > w/2 and get_length(x1, y1, x2, y2) > 40:
                    right_pts.append([x1, y1, x2, y2])
                # cv2.line(black, (x1, y1), (x2, y2), (255, 0, 255), 6)
    
    # cv2.imshow('dilated', dilated)            

    left_pts = np.array(left_pts); right_pts = np.array(right_pts)

    res = polyfit_line(left_pts)
    if res is not None:
        leftline = res

    res = polyfit_line(right_pts)
    if res is not None:
        rightline = res 

    if leftline is not None:
        cv2.line(black, (leftline[0], leftline[1]), (leftline[2], leftline[3]), (0, 255, 0), 12)
    
    if rightline is not None:
        cv2.line(black, (rightline[0], rightline[1]), (rightline[2], rightline[3]), (0, 255, 0), 12)

    if leftline is not None and rightline is not None:
        l_x1, l_y1, l_x2, l_y2 = leftline
        r_x1, r_y1, r_x2, r_y2 = rightline
        if abs(l_y1 - r_y1) < abs(l_y1 - r_y2):
            mid_x1 = (l_x1 + r_x1) // 2
            mid_y1 = (l_y1 + r_y1) // 2
        else:
            mid_x1 = (l_x1 + r_x2) // 2
            mid_y1 = (l_y1 + r_y2) // 2

        if abs(l_y2 - r_y2) < abs(l_y2 - r_y1):
            mid_x2 = (l_x2 + r_x2) // 2
            mid_y2 = (l_y2 + r_y2) // 2
        else:
            mid_x2 = (l_x2 + r_x1) // 2
            mid_y2 = (l_y2 + r_y1) // 2
        cv2.line(black, (mid_x1, mid_y1), (mid_x2, mid_y2), (255, 0, 255), 12)
    
    return black

def overlay_arrow(frame, direction):

    arrow = cv2.imread('uparrow.png', cv2.IMREAD_UNCHANGED)

    if direction == 'left':
        arrow = cv2.rotate(arrow, cv2.ROTATE_90_COUNTERCLOCKWISE)
    elif direction == 'right':
        arrow = cv2.rotate(arrow, cv2.ROTATE_90_CLOCKWISE)
    
    height, width, _ = arrow.shape  # takes shape of arrow png

    # resize arrow to 20% of its original size
    height = int(height * 0.2);
    width = int(width * 0.2)
    arrow = cv2.resize(arrow, (height, width))

    arrow_bgr = arrow[:, :, :3]  # extract bgr channels of the arrow
    arrow_alpha = arrow[:, :, 3]  # extract the alpha (transparency) channel

    # create a designated region in the video for the arrow overlay
    # the arrow will be overlayed in the top right corner (850, 10)
    roi = frame[10:10 + height, 850:850 + width]

    # alpha channel is normalized to range from 0.0 to 1.0
    mask = arrow_alpha.astype(float) / 255.0

    # iterates through each color channel of the roi, then blends
    # it with the arrow image
    for x in range(3):
        roi[:, :, x] = (mask * arrow_bgr[:, :, x] + (1 - mask) * roi[:, :, x])
        # multiplies arrow's color channel by the alpha value, then the roi's
        # color channel by 1 - alpha value to correctly overlay the arrow

    # return final video frame with arrow overlay
    return frame

def get_points(time):
    set1 = [[200, 525], [430, 400], [610, 400], [800, 525]]
    set2 = [[200, 525], [430, 400], [630, 400], [820, 525]]
    set3 = [[150, 500], [400, 350], [550, 350], [740, 500]]
    set4 = [[190, 510], [400, 410], [580, 410], [700, 510]]


    if time <= 3.00:
        return set1
    elif 3.00 <= time <= 17.40:
        return set2 
    elif 17.40 <= time <= 45.00:
        return set3   
    else:
        return set4
