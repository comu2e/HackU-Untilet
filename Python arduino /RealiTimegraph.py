import matplotlib.pyplot as plt  
import matplotlib.animation as anim  
from collections import deque  
import random
import serial

MAX_X = 100   #width of graph
MAX_Y = 10  #height of graph

# intialize line to horizontal line on 0
linemq4 = deque([0.0]*MAX_X, maxlen=MAX_X)
# ser = serial.Serial("/dev/tty.usbmodemFD122", 9600)
diff = deque([0.0]*MAX_X, maxlen=MAX_X)


def update(fn, l2d):
    #simulate data from serial within +-5 of last datapoint
    mq4 = serial.Serial("/dev/tty.usbmodemFD122",9600)
    mq4_data = float(mq4.readline().decode('utf-8'))
    #add new point to deque
    linemq4.append(mq4_data)
    # set the l2d to the new line coords
    # args are ([x-coords], [y-coords])
    l2d.set_data(range(-MAX_X//2, MAX_X//2), linemq4)


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
