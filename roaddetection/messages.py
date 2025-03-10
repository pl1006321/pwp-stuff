from tkinter import *
from tkinter import messagebox

# simplifies message boxes by creating a separate file 
# with them, then calling the message function

def login(username): 
    messagebox.showinfo(message=f'login successful! welcome {username}')

def create_acc():
    messagebox.showinfo(message=f'account creation successful!')

def wrong_pw():
    messagebox.showinfo(message='invalid password. please try again')

def invalid_user():
    messagebox.showinfo(message='invalid username. please try again')

def user_exists():
    messagebox.showinfo(message='account with this username already exists.')

def blank_entry():
    messagebox.showinfo(message='one or more entries were left blank. please try again')
