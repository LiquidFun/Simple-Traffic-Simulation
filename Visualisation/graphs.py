import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import math
import multiprocessing, os
from Simulator.simulator import Simulator

INTERVALL = 1 #in seconds
car_types  = ['pkw', 'lkw', 'bus'] #same as spawner.py
directory = os.path.dirname(os.path.abspath(__file__)) + "/../Data/"
fileString = str(directory)

def setup(simulator):
    global s, last_update, last_time, sensor_times
    last_update = 0
    last_time = 0.0
    s = simulator
    sensor_times = [0.0] * len(s.get_sensors())
    #creating Data folder, if it does not Exits
    if not os.path.exists(directory):
        os.makedirs(directory)
    #resetting Data
    for i in range(0,len(car_types)):
        with open(fileString+car_types[i]+'.txt', 'w') as f:
            f.write("")
    with open(fileString+"sensors.txt", 'w') as f:
            f.write("")

def on_update():
    global last_update, last_time, sensor_times
    time = int(s.get_time())
    if time >= last_update + INTERVALL:
        last_update = time
        create_data(time, sensor_times)
    #update sensor_times
    time = s.get_time() #use finer time (not rounded)
    sensors = s.get_sensors()
    for i in range(0,len(sensors)):
        if sensors[i]:
            sensor_times[i] += time - last_time
    last_time = time
    

def create_data(time, sensor_times):
    cars = s.get_cars()
    #print(sensor_times)
    #print(cars)
    data = []
    for i in range(0,len(car_types)):
        data.append([0,0])
    #counts, velocities

    for c in cars:
        #get car type and check which index it has in car_types
        typeIndex = car_types.index(c['type'])
        #then use that index for counts and add 1
        data[typeIndex][0] += 1
        data[typeIndex][1] += c['velocity']

    #save to file (from which thread_graph reads to draw the graphs)
    for i in range(0,len(car_types)):
        if data[i][0] > 0:
            data[i][1] /= data[i][0]
            data[i][1] *= 3.6 #from m/s to km/h
        with open(fileString+car_types[i]+'.txt', 'a') as f:
            item = str(time)+": "+str(data[i])
            f.write("%s\n" % item)
    #save sensor data
    with open(fileString+"sensors.txt", 'a') as f:
            item = str(time)+": "+str(sensor_times)
            f.write("%s\n" % item)

def convertTime(time):
    return "{:0>2}:{:0>2}".format(math.floor((time/3600)%60), math.floor((time/60)%60))

def set_xticks_time(timestamps):
    MAXTICKS = 8    
    ticks = [[],[]]
    n = len(timestamps) // MAXTICKS
    for time in timestamps:
        if time % n == 0:
            ticks[0].append(time)
            if timestamps[-1] >= 60*MAXTICKS: 
                ticks[1].append(convertTime(time))
            else:
                ticks[1].append(str(time)+"s")
    plt.xticks(ticks[0],ticks[1])

def thread_graph(target, windowTitle="", graphTitle=""):
    if graphTitle == "":
        graphTitle = windowTitle
    fig = plt.gcf()
    fig.canvas.set_window_title(windowTitle)
    legendData = []
    def animate(frame):
        fig.clear()
        plt.title(graphTitle)
        plt.xlabel("time")
        if(target==1):
            plt.ylabel("n")
        if(target==2):
            plt.ylabel("km/h")
        for i in range(0,len(car_types)):
            values = []
            timestamps = []
            file_data = open(fileString+car_types[i]+'.txt','r').read()
            lines = file_data.split('\n')
            prev = 0.0
            j = 1
            for line in lines:
                if len(line) >= 1:
                    time, rest = line.split(": ")
                    data = rest[1:-1].split(',')
                    timestamps.append(int(time))
                    count = int(data[0])
                    velocity = float(data[1])
                    if(target==1):
                        #print(car_types[i],"count:",count)
                        values.append(count)
                    if(target==2):
                        prev += velocity
                        values.append(prev/j)
                        if(count != 0):
                            j+=1
            if i == 1: plot = plt.plot(timestamps,values,color ='green')#lkw
            elif i == 2: plot = plt.plot(timestamps,values,color ='orange')#bus
            else: plot = plt.plot(timestamps,values)
            legendData.append(plot[0])
            set_xticks_time(timestamps)
        plt.legend(legendData, car_types)
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()

def thread_performance(windowTitle="", graphTitle=""):
    if graphTitle == "":
        graphTitle = windowTitle
    fig = plt.gcf()
    fig.canvas.set_window_title(windowTitle)
    legendData = []
    def animate(frame):
        fig.clear()
        plt.title(graphTitle)
        plt.xlabel("time")
        plt.ylabel("%")

        values = []
        timestamps = []
        file_data = open(fileString+"sensors.txt",'r').read()
        lines = file_data.split('\n')
        prev = 0.0
        j = 1
        for line in lines:
            if len(line) >= 1:
                time, rest = line.split(": ")
                data = rest[1:-1].split(',')
                timestamps.append(int(time))
                p = 0                
                for i in range(0,len(data)):
                    p += float(data[i])
                p /= len(data)*int(time)
                values.append(1-p)
        plot = plt.plot(timestamps,values)
        set_xticks_time(timestamps)
        #plt.legend(legendData, car_types)
    ani = animation.FuncAnimation(fig, animate, interval=1000)
    plt.show()
    
def draw_graph1():
    a = (1,"Fahrzeuganzahl", "Anzahl der Fahrzeuge")
    x = multiprocessing.Process(target=thread_graph, args=a)
    x.start()

def draw_graph2():
    a = (2,"Geschwindigkeit", "Durchschnittliche Geschwindigkeit")
    x = multiprocessing.Process(target=thread_graph, args=a)
    x.start()

def draw_graph3():
    a = ("Performance","")
    x = multiprocessing.Process(target=thread_performance, args=a)
    x.start()
