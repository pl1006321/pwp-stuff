import sqlite3
import messages as msg
from tkinter import *
from tkinter.scrolledtext import *
from tkinter.font import Font
import requests
from PIL import Image, ImageTk
from threading import Thread
import cv2
import base64
import numpy as np
import os
import subprocess

url = "http://192.168.240.25:5000/"

def launch_gui(root):  # launches the tkinter window using mainloop
    root.mainloop()


def connect_to_db():  # establishes connection to database + creates the cursor object
    conn = sqlite3.connect('userinfo.db')
    cursor = conn.cursor()
    return conn, cursor


def commit_n_close(conn):  # saves changes and connects to database
    conn.commit()
    conn.close()


def create_db():  # creates database if not existing already
    conn, cursor = connect_to_db()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # primary key makes it so that the id auto increments, ensuring a unique id for every user
    commit_n_close(conn)


def print_db():  # prints info in database (mainly for debugging)
    conn, cursor = connect_to_db()

    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()

    for x in rows:
        print(x)

    commit_n_close(conn)


def insert_db(the_user, the_pw):  # inserts username and password into database
    conn, cursor = connect_to_db()

    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (the_user, the_pw))

    commit_n_close(conn)


def existing_user(the_user):  # checks if the username already exists in database
    conn, cursor = connect_to_db()

    cursor.execute('SELECT id FROM users WHERE username = ?', (the_user,))

    result = cursor.fetchone()

    commit_n_close(conn)

    return result is not None  # false if user doesn't exist already, true if it does


def get_password(the_user):
    conn, cursor = connect_to_db()

    cursor.execute('SELECT id FROM users WHERE username = ?', (the_user,))  # gets id corresponding to username
    id_number = cursor.fetchone()[0]
    cursor.execute('SELECT password FROM users WHERE id = ?', (id_number,))  # gets password corresponding to id
    password = cursor.fetchone()[0]

    commit_n_close(conn)
    return password


def login_button_func(user, pw):
    if not user or not pw:  # makes sure entry fields are not blank
        msg.blank_entry()
        return
    exists = existing_user(user)  # checks if user exists in database
    if not exists:
        msg.invalid_user()
        return
    password = get_password(user)  # checks if password is correct
    if pw != password:
        msg.wrong_pw()
        return
    else:
        msg.login(user)  # successful login!
        create_robot_gui(user)  # launches robot remote control window


def create_acc_button_func(user, pw):
    if not user or not pw:  # makes sure entries are not empty
        msg.blank_entry()
        return
    exists = existing_user(user)  # check if user alr exists
    if exists:
        msg.user_exists()  # if user alr exists, login instead of create acc
        return
    insert_db(user, pw)  # insert user and pw into database
    msg.create_acc()


def post_direction(direction, user, gui):
    try:
        temp_url = url + 'moving'
        data = {'direction': direction}
        req = requests.post(temp_url, json=data)
        print('command sent successfully')
        logging(direction, user, gui)
    except:
        print('something happened; error')


def logging(direction, user, gui):
    try:
        temp_url = url + 'logging'
        log = requests.get(temp_url)
        log = log.json()
        log_str = f"{log['Timestamp']} - {user}@{log['IP Address']} sent the command: {direction}\n"
        with open("system_log.txt", 'a') as file:
            file.write(log_str)
        gui.config(state='normal')
        gui.insert(END, log_str)
        gui.see(END)
        gui.config(state='disabled')
    except:
        print('an error occured sorry!')

def open_log_file():
    file_path = "system_log.txt"
    if not os.path.exists(file_path):
        open(file_path, 'w').close()
    subprocess.call(('open', file_path))

def calc_angle(x1, y1, x2, y2):
    angle = np.degrees(np.arctan2(y2-y1, x2-x1))
    return angle 

def calc_midpoint(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return (int((x1+x2)/2), int((y1+y2)/2))

def calc_distance(p1, p2):
    x1, y1 = p1[0], p1[1]
    x2, y2 = p2[0], p2[1]
    return np.sqrt(np.square(y2-y1) + np.square(x2-x1))

def apply_overlay(frame): 
    image = cv2.resize(frame, (1280, 960))
    cropped = image[360:960, 0:1280]
    final = image.copy()

    hsv = cv2.cvtColor(cropped, cv2.COLOR_BGR2HSV)

    lower = np.array([0, 80, 0])
    upper = np.array([140, 255, 200])

    mask = cv2.inRange(hsv, lower, upper)
    dilated = cv2.dilate(mask, np.ones((3, 3), np.uint8), iterations=2)
    final_mask = cv2.morphologyEx(dilated, cv2.MORPH_CLOSE, np.ones((21, 21), np.uint8))

    masked = cv2.bitwise_and(cropped, cropped, mask=final_mask)

    gray = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    gaussian = cv2.GaussianBlur(gray, (7, 7), 0)
    edges = cv2.Canny(gaussian, 50, 150, apertureSize=3)
    dilated = cv2.dilate(edges, np.ones((5, 5), np.uint8), iterations=2)
    eroded = cv2.erode(dilated, np.ones((3, 3), np.uint8))

    lines = cv2.HoughLinesP(eroded, rho=1, theta=np.pi/180, threshold=10, minLineLength=30)
    points1 = []
    points2 = []
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = calc_angle(x1, y1, x2, y2)

            if abs(angle) < 20:
                continue

            if angle > 0:
                points1.append([x1, y1, x2, y2])
            else:
                points2.append([x1, y1, x2, y2])

    points1 = np.array(points1)
    points2 = np.array(points2)

    p1 = p2 = p3 = p4 = None

    try:
        slope, intercept = np.polyfit(points1[:, 0], points1[:, 1], 1)
        x1, x2 = min(points1[:, 0]), max(points1[:, 0])
        y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.line(cropped, p1, p2, (0, 255, 0), 5)
    except:
        print('error with line of best fits with points1')

    try:
        slope, intercept = np.polyfit(points2[:, 0], points2[:, 1], 1)
        x1, x2 = min(points2[:, 0]), max(points2[:, 0])
        y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

        p3, p4 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.line(cropped, p3, p4, (0, 255, 0), 5)
    except:
        print('error with line of best fit with points2')

    if p1 and p2 and p3 and p4:
        midpoint1 = calc_midpoint(p1, p2)
        midpoint2 = calc_midpoint(p3, p4)

        p1_p3 = calc_distance(p1, p3)
        p1_p4 = calc_distance(p1, p4)
        shorter1 = p3 if p1_p3 < p1_p4 else p4
        center1 = calc_midpoint(p1, shorter1)

        shorter2 = p4 if shorter1 == p3 else p3 
        center2 = calc_midpoint(p2, shorter2)

        # center3 = calc_intersection(shorter1, midpoint1, p1, shorter2)
        # center4 = calc_intersection(midpoint1, shorter2, midpoint2, p2)

        # cv2.circle(cropped, center1, 10, (0, 0, 255), -1)
        # cv2.circle(cropped, center2, 10, (0, 0, 255), -1)
        # cv2.circle(cropped, center3, 10, (0, 0, 255), -1)
        # cv2.circle(cropped, center4, 10, (0, 0, 255), -1)
        # print(f'center: {center1, center2, center3, center4}')
        
        # centerline = np.array([center1, center2, center3, center4])
        # slope, intercept = np.polyfit(centerline[:, 0], centerline[:, 1], 1)
        # x1, x2 = min(centerline[:, 0]), max(centerline[:, 0])
        # y1, y2 = (slope * x1 + intercept), (slope * x2 + intercept)

        # c1, c2 = (int(x1), int(y1)), (int(x2), int(y2))
        # cv2.line(cropped, c1, c2, (255, 0, 255), 2)
        cv2.line(cropped, center1, center2, (255, 0, 255), 5)


    final[360:960, 0:1280] = cropped

    return final


def update_vid_stream(element1, element2): 
    while True:
        b64_image = requests.get(url + 'vidstream').json()['frame'] # extract video stream from api
        decoded_img = base64.b64decode(b64_image) # decode the b64 string that is returned

        np_image = np.frombuffer(decoded_img, dtype=np.uint8) # convert string to numpy array
        stream = cv2.imdecode(np_image, cv2.IMREAD_COLOR) # convert numpy array to image

        overlay = apply_overlay(stream) # apply the overlay onto the frame 

        stream = cv2.resize(stream, (400, 300))
        overlay = cv2.resize(overlay, (400, 300))

        # cv2 uses bgr, tkinter uses rgb 
        stream = cv2.cvtColor(stream, cv2.COLOR_BGR2RGB)
        overlay = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)

        # create an imagetk of both images 
        stream = ImageTk.PhotoImage(Image.fromarray(stream))
        overlay = ImageTk.PhotoImage(Image.fromarray(overlay))

        # checks to see if both elements still exist, in case the gui is closed 
        if element1.winfo_exists() and element2.winfo_exists():
            # sets respective elements to the image frames 
            element1.imgtk = stream
            element2.imgtk = overlay
            element1.configure(image=stream)
            element2.configure(image=overlay) 
        else:
            break

def create_login_page():  # sets up the tkinter window for logging in
    login_page = Tk()
    login_page.title('user login')
    login_page.geometry('320x150')

    user_entry_text = StringVar()
    pw_entry_text = StringVar()

    entries_panel = Frame(login_page)
    entries_panel.grid(row=1, column=1, rowspan=3, padx=10, pady=5, sticky='NWSE')

    username_entry_label = Label(entries_panel, text='username: ')
    username_entry_label.grid(row=1, column=1, padx=5, pady=5)

    username_entry = Entry(entries_panel, textvariable=user_entry_text)
    username_entry.grid(row=1, column=2, padx=5, pady=5)

    password_entry_label = Label(entries_panel, text='password: ')
    password_entry_label.grid(row=2, column=1, padx=5, pady=5)

    password_entry = Entry(entries_panel, textvariable=pw_entry_text)
    password_entry.grid(row=2, column=2, padx=5, pady=5)

    buttons_panel = Frame(login_page)
    buttons_panel.grid(row=5, column=1, rowspan=1, padx=45, pady=5, sticky='NWSE')

    login_button = Button(buttons_panel, text='login', command=lambda: login_button_func(user_entry_text.get(), pw_entry_text.get()))
    login_button.grid(row=1, column=1, ipadx=3, ipady=2, padx=5, pady=5)

    create_acc_button = Button(buttons_panel, text='create account', command=lambda: create_acc_button_func(user_entry_text.get(), pw_entry_text.get()))
    create_acc_button.grid(row=1, column=2, ipadx=3, ipady=2, padx=5, pady=5)

    return login_page


def create_robot_gui(user):  # sets up tkinter window for controlling robot if login is successful
    robot_gui = Toplevel()
    robot_gui.title('robot gui')
    robot_gui.geometry('1100x800')

    custom = Font(family='Poppins', size=20)

    vid_stream_panel = Frame(robot_gui)
    vid_stream_panel.grid(row=5, column=1, rowspan=1, padx=5, pady=5, sticky='NWSE')

    buttons_panel = Frame(robot_gui)
    buttons_panel.grid(row=5, column=2, rowspan=1, padx=20, pady=95, sticky='NWSE')

    vid_overlay_panel = Frame(robot_gui)
    vid_overlay_panel.grid(row=6, column=1, rowspan=1, padx=5, pady=5, sticky='NWSE')

    log_panel = Frame(robot_gui)
    log_panel.grid(row=6, column=2, rowspan=1, padx=10, pady=50, sticky='NS')

    text_area = ScrolledText(log_panel, width=55, height=5)
    text_area.grid(row=1, padx=5, pady=5, ipadx=20, ipady=20)

    text_area.config(state='disabled')

    open_file_button = Button(log_panel, text='open log file', command=open_log_file, font=custom, padx=5, pady=7)
    open_file_button.grid(row=2, padx=4, pady=5, ipadx=5, ipady=5,)

    stream_elem = Label(vid_stream_panel, text='vid stream')
    stream_elem.grid(padx=50, pady=40)

    overlay_elem = Label(vid_overlay_panel, text='vid overlay')
    overlay_elem.grid(padx=50, pady=10)

    video_thread = Thread(target=update_vid_stream, args=(stream_elem,overlay_elem))
    video_thread.daemon = True 
    video_thread.start()

    forward = Button(buttons_panel, text='move forward', font=custom, padx=5, pady=7)
    forward.grid(row=1, column=2, padx=5, pady=5, ipadx=5, ipady=5, sticky='we', columnspan=2)
    forward.bind('<ButtonPress-1>', lambda event: post_direction('forward', user, text_area))
    forward.bind('<ButtonRelease-1>', lambda event: post_direction('stop', user, text_area))

    left = Button(buttons_panel, text='move left', font=custom, padx=5, pady=7)
    left.grid(row=2, column=1, padx=2.5, pady=5, ipadx=5, ipady=5)
    left.bind('<ButtonPress-1>', lambda event: post_direction('left', user, text_area))
    left.bind('<ButtonRelease-1>', lambda event: post_direction('stop', user, text_area))

    play = Button(buttons_panel, text='play', font=custom, padx=5, pady=7)
    play.grid(row=2, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

    stop = Button(buttons_panel, text='stop', command=lambda: post_direction('stop', user, text_area), font=custom, padx=5, pady=7)
    stop.grid(row=2, column=3, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

    right = Button(buttons_panel, text='move right', font=custom, padx=5, pady=7)
    right.grid(row=2, column=4, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')
    right.bind('<ButtonPress-1>', lambda event: post_direction('right', user, text_area))
    right.bind('<ButtonRelease-1>', lambda event: post_direction('stop', user, text_area))

    backward = Button(buttons_panel, text='move backward', font=custom, padx=5, pady=7)
    backward.grid(row=3, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we', columnspan=2)
    backward.bind('<ButtonPress-1>', lambda event: post_direction('backward', user, text_area))
    backward.bind('<ButtonRelease-1>', lambda event: post_direction('stop', user, text_area))
