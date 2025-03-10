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

class database:
    def __init__(self):
        self.create_db() 

    def connect(self):
        conn = sqlite3.connect('userinfo.db')
        cursor = conn.cursor()
        return conn, cursor
    
    def commit_n_close(self, conn):
        conn.commit()
        conn.close() 

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

    def insert_user(self, username, password):
        conn, cursor = self.connect()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        self.commit_n_close(conn)

    def user_exists(self, username):
        conn, cursor = self.connect()
        cursor.execute('SELECT id FROM users WHERE username = ?', (username, ))
        result = cursor.fetchone()
        self.commit_n_close(conn)
        return result is not None
    
    def get_password(self, username):
        conn, cursor = self.connect()
        cursor.execute('SELECT password FROM users WHERE username = ?', (username, ))
        password = cursor.fetchone()
        self.commit_n_close(conn)
        return password[0] if password else None
    

class guiwindows:
    def __init__(self, root):
        self.root = root
        self.root.title('user login')
        self.root.geometry('320x150')
        self.database = database()

        self.setup_login_page()

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

        stream_elem = Label(vid_stream_panel, text='video stream')
        stream_elem.grid(padx=50, pady=40)

        overlay_elem = Label(vid_overlay_panel, text='overlay stream')
        overlay_elem.grid(padx=50, pady=10)

        video_thread = Thread(target=self.update_vid_stream, args=(stream_elem, overlay_elem))
        video_thread.daemon = True
        video_thread.start()

        forward = Button(buttons_panel, text='move forward', font=custom_font, padx=5, pady=7,)
        forward.grid(row=1, column=2, padx=5, pady=5, ipadx=5, ipady=5, sticky='we', columnspan=2)
        # forward.bind('<ButtonPress-1>', lambda event: self.log_direction('forward', user))
        # forward.bind('<ButtonRelease-1', lambda event: self.log_direction('stop', user))

        left = Button(buttons_panel, text='move left', font=custom_font, padx=5, pady=7)
        left.grid(row=2, column=1, padx=2.5, pady=5, ipadx=5, ipady=5)
        # left.bind('<ButtonPress-1>', lambda event: self.log_direction('left', user))
        # left.bind('<ButtonRelease-1', lambda event: self.log_direction('stop', user))

        play = Button(buttons_panel, text='play', font=custom_font, padx=5, pady=7, command=self.play_video)
        play.grid(row=2, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

        stop = Button(buttons_panel, text='stop', font=custom_font, padx=5, pady=7, command=self.stop_video)
        stop.grid(row=2, column=3, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we')

        right = Button(buttons_panel, text='move right', font=custom_font, padx=5, pady=7)
        right.grid(row=2, column=4, padx=2.5, pady=5, ipadx=5, ipady=5)
        # right.bind('<ButtonPress-1>', lambda event: self.log_direction('right', user))
        # right.bind('<ButtonRelease-1', lambda event: self.log_direction('stop', user))

        backward = Button(buttons_panel, text='move backward', font=custom_font, padx=5, pady=7)
        backward.grid(row=3, column=2, padx=2.5, pady=5, ipadx=5, ipady=5, sticky='we', columnspan=2)
        # backward.bind('<ButtonPress-1>', lambda event: self.log_direction('backward', user))
        # backward.bind('<ButtonRelease-1', lambda event: self.log_direction('stop', user))
    
    def update_vid_stream(self, element1, element2):
        pass
    
    def log_direction(self, direction, user):
        pass

    def play_video(self):
        pass

    def stop_video(self):
        pass

    def open_log_file(self):
        file_path = 'system_log.txt'
        if not os.path.exists(file_path):
            open(file_path, 'w').close()
        subprocess.call(('open', file_path))

if __name__ == '__main__':
    root = Tk()
    app = guiwindows(root)
    root.mainloop()
