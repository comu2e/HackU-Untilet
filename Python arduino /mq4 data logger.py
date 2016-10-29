import matplotlib.pyplot as plt  
import matplotlib.animation as anim  
from collections import deque  
import random
import serial

MAX_X = 100   #width of graph  
MAX_Y = 5  #height of graph

# intialize line to horizontal line on 0
line = deque([0.0]*MAX_X, maxlen=MAX_X)
ser = serial.Serial("/dev/tty.usbmodemFD122", 9600)


def update(fn, l2d):
    #simulate data from serial within +-5 of last datapoint
    # dy = random.randint(-5, 5)
    ser = serial.Serial("/dev/tty.usbmodemFD122",9600)
    dy = float(ser.readline().decode('utf-8'))
    volt = 5*dy/1024
    #add new point to deque
    line.append(line[MAX_X-1]+volt)
    # set the l2d to the new line coords
    # args are ([x-coords], [y-coords])
    l2d.set_data(range(-MAX_X//2, MAX_X//2), line)

fig = plt.figure()
# make the axes revolve around [0,0] at the center
# instead of the x-axis being 0 - +100, make it -50 - +50
# ditto for y-axis -512 - +512
a = plt.axes(xlim=(-(MAX_X//2),MAX_X//2), ylim=(-0.1,MAX_Y+0.1))
# plot an empty line and keep a reference to the line2d instance
l1, = a.plot([], [])  
ani = anim.FuncAnimation(fig, update, fargs=(l1,), interval=50)

plt.grid()
plt.show()  