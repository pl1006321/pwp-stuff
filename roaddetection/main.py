import cv2
import numpy as np

leftline = rightline = None

def get_points(time):
    set1 = [[200, 525], [475, 375], [615, 375], [800, 525]]
    set2 = [[250, 525], [500, 375], [650, 375], [850, 525]]
    set3 = [[225, 525], [425, 400], [590, 400], [790, 525]]
    set4 = [[200, 525], [450, 390], [600, 390], [850, 525]]
    set5 = [[200, 525], [450, 360], [600, 360], [850, 525]]
    set6 = [[235, 525], [450, 400], [585, 400], [785, 525]]
    set7 = [[250, 450], [500, 300], [650, 300], [750, 450]]
    set8 = [[200, 480], [400, 330], [500, 330], [750, 480]]

    set9 = [[220, 525], [410, 370], [500, 370], [700, 525]]
    set10 = [[210, 500], [400, 360], [550, 360], [790, 500]]

    if 0.03 <= time <= 1.80:
        return set1
    elif 1.83 <= time <= 6.60:
        return set2
    elif 6.60 <= time <= 9.33:
        return set3
    elif 9.33 <= time <= 14.40:
        return set4
    elif 14.40 <= time <= 15.40:
        return set5
    elif 15.40 <= time <= 24.30:
        return set6
    elif 24.30 <= time <= 24.83:
        return set7
    elif 24.83 <= time <= 32.60:
        return set8
    
    if 32.60 <= time <= 34.00:
        return set9
    elif 34 <= time <= 39:
        return set10
    
    return None

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
    threshold = 0.45

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
            print('yay line!')
            return [x1, y1, x2, y2]
    except Exception as e:
        print(f'error: {str(e)}')
        return None
    
def get_length(x1, y1, x2, y2):
    return np.sqrt((x2-x1)**2 + (y2-y1)**2)

def detect_lines(frame, final, time, templates):
    global leftline, rightline 
    thinned = cv2.ximgproc.thinning(frame)

    h, w, _ = final.shape

    dilated = cv2.dilate(thinned, np.ones((5, 5), np.uint8), iterations=1)

    template_pts = []
    for template in templates:
        p1, p2 = template_match(warped, template)
        if p1 and p2:
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
                # cv2.line(final, (x1, y1), (x2, y2), (255, 0, 255), 6)
    
    cv2.imshow('dilated', dilated)            

    left_pts = np.array(left_pts); right_pts = np.array(right_pts)

    res = polyfit_line(left_pts)
    if res is not None:
        leftline = res

    res = polyfit_line(right_pts)
    if res is not None:
        rightline = res 

    if leftline is not None:
        cv2.line(final, (leftline[0], leftline[1]), (leftline[2], leftline[3]), (0, 255, 0), 12)
    
    if rightline is not None:
        cv2.line(final, (rightline[0], rightline[1]), (rightline[2], rightline[3]), (0, 255, 0), 12)

    return final

def overlay_arrow(frame, arrow):
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

    # read arrows
    up_arrow = cv2.imread('uparrow.png', cv2.IMREAD_UNCHANGED)

    # read templates
    temp1 = cv2.imread('templates/only1_temp.png')
    temp2 = cv2.imread('templates/right1_temp.png')
    temp3 = cv2.imread('templates/only2_temp.png')
    temp4 = cv2.imread('templates/left1_temp.png')

    templates = [temp1, temp2, temp3, temp4]

    print(f'{time:.2f}')

    points = get_points(time)
    if points is not None:
        warped = pers_trans(frame, points)
        filtered = filters(warped.copy())

        lines = detect_lines(filtered, warped.copy(), time, templates)

        unwarped = unwarp(lines, points)
        final = cv2.addWeighted(frame, 0.8, unwarped, 0.8, 0)
        final = overlay_arrow(final, up_arrow)
        cv2.imshow('warp perspective', warped)
        cv2.imshow('lines', lines)
        cv2.imshow('final', final)

    frame = overlay_arrow(frame, up_arrow)
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) != -1:
        break
