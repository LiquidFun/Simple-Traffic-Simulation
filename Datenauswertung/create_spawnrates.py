import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, date, time

def manualcount():
    data = readData("../../data-master/Z_0915.XLS")
    selection = range(3,9) #select which rows of data 
                           #(corresponing mostly to vehicle types) to save
    s = 0
    x = 0
    for l in range(x,len(data[s])):
        if data[s][l] == "Intervall in min":
            intervall = int(data[s][l+1])
            x = l
            break
    #print("Intervall:",intervall,"(m)")

    for l in range(x,len(data[s])):
        if data[s][l] == "Datum":
            x = l
            break
    datainfo = []
    for r in range(0,len(data)):
        string = str(data[r][x])
        if string == ("" or "nan"):
            break
        datainfo.append(s)
    #print("datainfo:",datainfo)

    sr = 1 #search row (for "von:" and "bis:")
    counts = {}
    values = {}
    scrape = False
    for l in range(x,len(data[sr])):
        if data[sr][l] == "von:":
            von = int(data[sr+1][l])
            continue
        if data[sr][l] == "nach:":
            nach = int(data[sr+1][l])
            scrape = True
            #print("scrape begin")
            continue
        string = str(data[0][l])
        if(scrape == True and string == ("" or "nan")):
            counts[(von,nach)] = values
            values = {}
            scrape = False
        if(scrape == True):
            dt = datetime.fromisoformat(string)
            timestamp = dt.hour*60 + dt.minute
            #print(timestamp)
            values[timestamp] = []
            for r in selection:
                values[timestamp].append(data[r][l])
    counts[(von,nach)] = values
  
    #graph drawing/ test if result equals K_0915.pdf (yes, for typeSelection = range(0,5))
    begin = 7*60 + 0  #must match creation of timestamp
    end = 8*60 + 0
    for direction in counts:
        forGraph = counts[direction]
        #print(forGraph.items())
        bins = []
        x = []
        for key, value in forGraph.items():
            if(begin <= key and key < end):
                bins.append(key)
                s = 0
                for i in range(0,len(value)):
                    s += value[i]
                x.append(s)
        #print(x)
        #print("Verbindung:",direction, "Summe:",sum(x))
        if direction[0] in [2,4]:
            plt.plot(bins,x,label=direction)
    plt.legend()
    #plt.show()

    INTERVAL = 60
    typeSelection = range(0,5) #type of vehicle
    # 0 = Pkw 1 = Lkw 3 = Bus(/KOM)
    lanes = [1,2,3,4]
    interval_data = {}
    for begin in range(0,24*60,INTERVAL):
        end = begin+INTERVAL
        value_written = False
        spawnerValues = {}
        for l in lanes:
            spawnerValues[l] = [0]*len(typeSelection)
            #print(spawnerValues)
            destinations = [1,2,3,4]
            destinations.remove(l)
            #print(destinations)
            for dest in destinations:
                x = counts[(l,dest)]
                for key, value in x.items():
                    if(begin <= key and key < end):
                        value_written = True
                        for t in typeSelection:
                            spawnerValues[l][t] += value[t]
            #change counts in an hour to cars/second:
            #for i in range(0,len(spawnerValues[l])):
            #    spawnerValues[l][i] /= (60*60)
        if value_written:
            interval_data[begin] = spawnerValues
    '''
    #fill missing hours:
    factor = 0.9
    for time in range(6*60,0,-INTERVAL):
        spawnerValues = interval_data[6*60]
        print(spawnerValues)
        for key, values in spawnerValues:
            for t in range(0,len(values)):
                spawnerValues[key][t] *= factor
        interval_data[time] = spawnerValues
        if factor > 0.1:
            factor -= 0.1
    '''
    return interval_data

def readData(loc):
    file = loc
    df = pd.read_excel(file)

    data = []
    for i in range(0,len(df.columns)):
	    data.append(df[df.columns[i]])
    return data

x = manualcount()
print(x)

