import sqlite3
import messages as msg
from tkinter import *
from tkinter.scrolledtext import *
from tkinter.font import Font
from PIL import Image, ImageTk
from threading import Thread
import cv2
import numpy as np
import os
import subprocess
from processing import *
from datetime import *
import socket

"""
set up a class for initializing, accessing, and editing
an sqlite3 database for managing the credentials of 
the login interface of the program.
"""
class database:
    # initializes the database upon creating an instance
    # of the database class 
    def __init__(self):
        self.create_db() 

    # connects to the sqlite3 database, returns the 
    # connection object and the cursor for executing 
    # further queries. this function must be called
    # every time before accessing and modifying the
    # database 
    def connect(self):
        conn = sqlite3.connect('userinfo.db')
        cursor = conn.cursor()
        return conn, cursor

    # commits changes to the database and closes the 
    # connection, ensuring changes are saved and that
    # the connection is safely closed each time 
    def commit_n_close(self, conn):
        conn.commit()
        conn.close() 

    # creates the database if it does not already 
    # exist. called when creating an instance of the 
    # database class 
    def create_db(self):
        conn, cursor = self.connect()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
                )
        ''')
        self.commit_n_close(conn)

    # inserts a new set of user credentials into
    # the users table. takes in the inputs username
    # and password to insert into the database
    def insert_user(self, username, password):
        conn, cursor = self.connect()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        self.commit_n_close(conn)

    # takes in the input username, then checks if 
    # a user in the database with the given username 
    # already exists in the database. if the user 
    # already exists, reutrn True. otherwise, False
    def user_exists(self, username):
        conn, cursor = self.connect()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username, ))
        result = cursor.fetchone()
        self.commit_n_close(conn)
        return result is not None

    # takes in the input username, then returns 
    # the password for the given username. If the 
    # user does not exist, return None. otherwise, 
    # return the password
    def get_password(self, username):
        conn, cursor = self.connect()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username, ))
        password = cursor.fetchone()
        self.commit_n_close(conn)
        return password[0] if password else None
    
"""
set up a class for initializing the graphical user 
interface (gui) elements of the user login and control
panel. 
"""
class guiwindows:
    # upon creating an instance of the guiwindows
    # class, initializes the main gui window, a 
    # database object for managing and accessing
    # credentials, and variables required for 
    # ideo streaming, and the login page is launched. 
    def __init__(self, root):
        self.root = root
        self.root.title('user login')
        self.root.geometry('320x150')
        self.database = database()
 
        self.video_running = False
        self.video_paused = False
        self.cap = None

        self.setup_login_page()

    # creates the text labels and text entry 
    # fields for username and password input, 
    # as well as buttons for login and account 
    # creation. uses the sqlite3 database from 
    # the database object to manage and access creds 
    def setup_login_page(self):
        self.user_entry_text = StringVar()
        self.pw_entry_text = StringVar()

        entries_panel = Frame(self.root)
        entries_panel.grid(row=1, column=1, rowspan=3, padx=10, pady=5, sticky='NWSE')

        username_entry_label = Label(entries_panel, text='username: ')
        username_entry_label.grid(row=1, column=1, padx=5, pady=5)

        username_entry = Entry(entries_panel, textvariable=self.user_entry_text,)
        username_entry.grid(row=1, column=2, padx=5, pady=5)

        password_entry_label = Label(entries_panel, text='password: ')
        password_entry_label.grid(row=2, column=1, padx=5, pady=5)

        password_entry = Entry(entries_panel, textvariable=self.pw_entry_text, show='*')
        password_entry.grid(row=2, column=2, padx=5, pady=5)

        buttons_panel = Frame(self.root)
        buttons_panel.grid(row=5, column=1, rowspan=1, padx=45, pady=5, sticky='NWSE')

        login_button = Button(buttons_panel, text='login', command=self.login)
        login_button.grid(row=1, column=1, ipadx=3, ipady=2, padx=5, pady=5)

        create_acc_button = Button(buttons_panel, text='create account', command=self.create_acc) 
        create_acc_button.grid(row=1, column=2, ipadx=3, ipady=2, padx=5, pady=5)

    # called upon clicking the login button 
    # inside the gui. checks if the entered 
    # username and password match the creds 
    # stored in the database
    def login(self):
        username = self.user_entry_text.get()
        password = self.pw_entry_text.get()

        if not username or not password:
            msg.blank_entry()
            return
        
        if not self.database.user_exists(username):
            msg.invalid_user()
            return
    
        if password != self.database.get_password(username):
            msg.wrong_pw()
            return
        
        msg.login(username)
        self.create_robot_gui(username)

    # insert the entered credentials into the 
    # database if the username does not already 
    # exist. 
    def create_acc(self):
        username = self.user_entry_text.get()
        password = self.pw_entry_text.get()

        if not username or not password:
            msg.blank_entry()
            return
        
        if self.database.user_exists(username):
            msg.user_exists()
            return
        
        self.database.insert_user(username, password)
        msg.create_acc()

    # creates a new tkinter window, and sets up 
    # the frames for video streaming and overlay, 
    # as well as control buttons and log panel. 
    def create_robot_gui(self, user):
        robot_gui = Toplevel()
        robot_gui.title('robot gui')
        robot_gui.geometry('1100x800')

        custom_font = Font(family='Poppins', size=20)
        
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

        log_button = Button(log_panel, text='open log file', command=self.open_log_file, font=custom_font, padx=5, pady=7)
        log_button.grid(row=2, padx=4, pady=5, ipadx=5, ipady=5)

        self.stream_elem = Label(vid_stream_panel, text='video stream')
        self.stream_elem.grid(padx=50, pady=40)

        self.overlay_elem = Label(vid_overlay_panel, text='overlay stream')
        self.overlay_elem.grid(padx=50, pady=10)

        forward = Button(buttons_panel, text='move forward', font=custom_font, padx=5, pady=7,)
        forward.grid(row=1, column=2, padx=5, pady=5, ipadx=5, ipady=5, sticky='we', columnspan=2)
        forward.bind('<ButtonPress-1>', lambda event: self.log_direction('forward', user, text_area))
        forward.bind('<ButtonRelease-1>', lambda event: self.log_direction('stop', user, text_area))

        left = Button(buttons_panel, text='move left', font=custom_font, padx=5, pady=7)
        left.grid(row=2, column=1, padx=2.5, pady=5, ipadx=5, ipady=5)
        left.bind('<ButtonPress-1>', lambda event: self.log_direction('left', user, text_area))
        left.bind('<ButtonRelease-1>', lambda event: self.log_direction('stop', user, text_area))

        play = Button(buttons_panel, text='play', font=custom_font, padx=5, pady=7, command=self.play_video)
        play.grid(row=2, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

        stop = Button(buttons_panel, text='stop', font=custom_font, padx=5, pady=7, command=self.stop_video)
        stop.grid(row=2, column=3, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

        right = Button(buttons_panel, text='move right', font=custom_font, padx=5, pady=7)
        right.grid(row=2, column=4, padx=2.5, pady=5, ipadx=5, ipady=5)
        right.bind('<ButtonPress-1>', lambda event: self.log_direction('right', user, text_area))
        right.bind('<ButtonRelease-1>', lambda event: self.log_direction('stop', user, text_area))

        backward = Button(buttons_panel, text='move backward', font=custom_font, padx=5, pady=7)
        backward.grid(row=3, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we', columnspan=2)
        backward.bind('<ButtonPress-1>', lambda event: self.log_direction('backward', user, text_area))
        backward.bind('<ButtonRelease-1>', lambda event: self.log_direction('stop', user, text_area))

        ip_addr = socket.gethostbyname(socket.gethostname())
        time = datetime.now() 
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')        
        msg = f'{user}@{ip_addr} has logged in at {timestamp}'
        with open('system_log.txt', 'a') as file:
            file.write(msg)
        file.close()
        text_area.config(state='normal')
        text_area.insert(END, msg)
        text_area.see(END)
        text_area.config(state='disabled')

    # runs in a separate thread to continuously 
    # process video frames. applies image overlay 
    # functions from the processing file 
    def update_vid_stream(self):
        global leftline, rightline
        while self.video_running:
            if self.video_paused:
                continue

            if not self.cap.isOpened():
                print('uh oh')
                break

            ret, frame = self.cap.read() 
            if not ret:
                break

            frame = cv2.resize(frame, (960, 540))

            frame_count = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            fps = self.cap.get(cv2.CAP_PROP_FPS)

            key = frame_count / fps 

            only1_temp = cv2.imread('templates/only1_temp.png')
            only2_temp = cv2.imread('templates/only2_temp.png')

            left1_temp = cv2.imread('templates/left1_temp.png')
            right1_temp = cv2.imread('templates/right1_temp.png')

            arrow_temps = {'left':left1_temp, 'right':right1_temp}
            only_temps = [only1_temp, only2_temp]

            points = get_points(key)
            warped = pers_trans(frame, points)
            filtered = filters(warped.copy())

            lines = detect_lines(filtered, warped, arrow_temps, only_temps)

            unwarped = unwarp(lines, points)
            mask = cv2.cvtColor(unwarped, cv2.COLOR_BGR2GRAY) > 0
            final = frame.copy() 
            final[mask] = unwarped[mask]


            if 16.90 <= key <= 16.94 or 46 <= key <= 46.04:
                set_current_dir('forward')
            final = overlay_arrow(final, get_current_dir())

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_rgb = cv2.resize(frame_rgb, (480, 270))

            overlay_rgb = cv2.cvtColor(final, cv2.COLOR_BGR2RGB)
            overlay_rgb = cv2.resize(overlay_rgb, (480, 270))

            stream_img = Image.fromarray(frame_rgb)
            stream_imgtk = ImageTk.PhotoImage(image=stream_img)

            overlay_img = Image.fromarray(overlay_rgb)
            overlay_imgtk = ImageTk.PhotoImage(image=overlay_img)

            self.stream_elem.config(image=stream_imgtk)
            self.stream_elem.image = stream_imgtk

            self.overlay_elem.config(image=overlay_imgtk)
            self.overlay_elem.image = overlay_imgtk

            self.root.update_idletasks() 
        
        self.cap.release()
        self.cap = None
        self.video_running = False

    # logs movement commands issued by
    # the user into the log panel. takes in
    # the direction, username, and the log 
    # panel to add text. 
    def log_direction(self, direction, user, gui):
        ip_addr = socket.gethostbyname(socket.gethostname())
        time = datetime.now() 
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        
        msg = f'{user}@{ip_addr} has sent the command {direction} at {timestamp}\n'
        gui.config(state='normal')
        gui.insert(END, msg)
        gui.see(END)
        gui.config(state='disabled')

    # starts playing video if the camera 
    # connection does not alr exist. otherwise, 
    # resume processing frames
    def play_video(self):
        if self.cap is None:
            self.cap = cv2.VideoCapture('video.mov')
            self.video_running = True
            self.video_paused = False

            self.video_thread = Thread(target=self.update_vid_stream)
            self.video_thread.daemon = True
            self.video_thread.start() 
        else:
            self.video_paused = False

    # pauses video playback from the moment
    # the user clicks the stop button
    def stop_video(self):
        self.video_paused = True

    # linked to the open log file button. 
    # if file does not already exist, create 
    # the file. then, open the log file
    def open_log_file(self):
        file_path = 'system_log.txt'
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        subprocess.call(('open', file_path))

if __name__ == '__main__':
    root = Tk()
    app = guiwindows(root)
    root.mainloop()
