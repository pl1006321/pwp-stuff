from tkinter import *
from sqlite3 import *
from messages import *
from functions import *

login_page = create_login_page() # calls function to create login window 
create_db() # creates db if not existing, nothing happens if db already exists 
launch_gui(login_page) # launches login window 
