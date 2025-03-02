hii these r step by step instructions on how to get this to work!! and if it doesnt work. erm. 
i may or may not be awake during period 2 if u guys do run into any problems so sorry in advance if im not!

#### **WARNING REGARDING NANO EDITOR:**

you might run into an issue with nano in which if the terminal window isnt maximized, then
some lines of code get cut off by default which may lead to issues. either use terminal in 
full screen or just use vi idk it confuses me too 

===========================================================

### ON THE ACTUAL COMPUTER:
1. make a new directory (mkdir) and cd into it

2. in that directory, use nano/vi to create the following files:
  - message.py
  - functions.py
  - main.py

and paste corresponding contents into each file

3. make sure to go into some of the files and change the api url to the correct one
  - pretty sure it's only in functions.py for these 3 files, but it's in there twice 

4. make sure all external libraries are downloaded prior to running anything
- pillow, thread, opencv-python, tkinter, requests, sqlite3 

===========================================================

### ON THE RASPBERRY PI: 
1. make a new directory and cd into it

2. in that directory, use nano/vi to create the following files:
  - MotorFunctions.py
  - api_attempt.py
  - getvidstream.py 
and paste corresponding contents into each file

3. go into getvidstream.py and change the api url so that it matches up 

4. download raspberry pi's version of opencv if not done so already

these are directly copied and pasted from schoology! run each line individually 

  $ sudo apt-get update
  
  $ sudo apt-get install libatlas-base-dev
  
  $ sudo apt-get install libjasper-dev
  
  $ pip3 install -i https://www.piwheels.org/simple opencv-python
  
  $ pip3 install -i https://www.piwheels.org/simple opencv-contrib-python

===========================================================

### TO RUN THE ACTUAL PROGRAM:

1. open a total of 3 terminal windows; 1 for the actual computer's local directory, 2 that are accessing the pi 

2. run api_attempt.py from the pi

3. run getvidstream.py from the pi

4. run main.py from the pc 

it should work! hopefully.... 
love you guys and goodluck w stern ❤️
