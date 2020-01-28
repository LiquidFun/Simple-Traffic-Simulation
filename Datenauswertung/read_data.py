import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date, time

def normal(mu,sigma,x):
    return 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (x - mu)**2 / (2 * sigma**2) )

def muFitting(median):
    LIMIT = 0
    WEIGHT = 0.8
    maxima = []
    cleanmax = []
    valid = range(0,len(median))
    for i in valid:
        diff = 0
        diff2 = 0
        if i+1 in valid and i-1 in valid and median[i] > median[i-1] and median[i] > median[i+1]:
            if i+1 in valid and i+2 in valid:
                if median[i+1]-median[i+2] > 0 and median[i]-median[i+1] < WEIGHT*(median[i+1]-median[i+2]):
                    diff = (median[i+1]-median[i+2]) - (median[i]-median[i+1])
            if i-1 in valid and i-2 in valid:
                if median[i-1]-median[i-2] > 0 and median[i]-median[i-1] < WEIGHT*(median[i-1]-median[i-2]):
                    diff2 = (median[i-1]-median[i-2]) - (median[i]-median[i-1])
            if diff > diff2:
                maxima.append(i + 0.5)
            elif diff < diff2:
                maxima.append(i - 0.5)
            else:
                maxima.append(i)
            cleanmax.append(i)
    #print(maxima)
    if LIMIT <= 0:
        return maxima

    limited = []
    for i in range(0,LIMIT):
         currmax = 0
         currj = 0
         for j in range(0,len(cleanmax)):
             x = median[cleanmax[j]]
             if x > currmax:
                 currmax = x
                 currj = j
         limited.append(maxima[currj])
         cleanmax[currj] = 0
    #print(limited)
    return limited

def sigmaFitting(mu, median):
    MINSTEP = 0.01
    DISTANCE = 1
    sigma = [1] * len(mu)
    ncars = ncarsFitting(mu, sigma, median)
    
    l = r = 0
    valid = range(0,24)
    for i in range(0,len(mu)):
        '''
        if mu[i] == int(mu[i]):
            maxv = median[mu[i]]
        else:
            maxv = (median[int(mu[i])]+median[int(mu[i])+1])/2
        '''
        if mu[i] == int(mu[i]):
            l = int(mu[i]) - DISTANCE
            r = int(mu[i]) + DISTANCE
        else:
            l = int(mu[i]) - DISTANCE
            r = int(mu[i]) + DISTANCE + 1
        while not l in valid:
            l += 1
        while not r in valid:
            r -= 1
        
        #v = 0
        lv = rv = 0
        step = 0.5
        while step >= MINSTEP:
            #v = 0
            lv = rv = 0
            for j in range(0,len(mu)):
                #v += ncars[j]*normal(mu[j],sigma[j],mu[i])
                lv += ncars[j]*normal(mu[j],sigma[j],l)
                rv += ncars[j]*normal(mu[j],sigma[j],r)
            if lv < median[l] and rv < median[r]:# and v < 1.002* maxv:
                sigma[i] += step
            else:
                sigma[i] -= step
                step /= 2.0
            #print(step)
            ncars = ncarsFitting(mu, sigma, median)
    return sigma

def ncarsFitting(mu, sigma, median):
    ncars = [0] * len(mu)
    
    for i in range(0,len(mu)):
        if mu[i] == int(mu[i]):
            maxv = median[mu[i]]
        else:
            maxv = (median[int(mu[i])]+median[int(mu[i])+1])/2

        v = 0
        while v <= maxv:
            v = 0
            for j in range(0,i+1):
                v += ncars[j]*normal(mu[j],sigma[j],mu[i])
            ncars[i] += 1
            #print(v, maxv)
    return ncars

def getDistribution(mu, sigma, ncars, bins):
    #add values together for final distribution:
    values = []
    for x in bins:
        v = 0
        for i in range(0,len(mu)):
            v += ncars[i]*normal(mu[i],sigma[i],x)
        values.append(v)
    return values


#für DZ943_SuedringWest_Hauptfahrstreifen_RichtungOsten_201904xx.xls und ähnliche
def showGraph(data):
    row = 2
    i = 0
    while data[0][ofs+i].date() == data[0][ofs+i+1].date():
        #print(data[0][3+i])
        i+=1
    i+=1
    
    dayn = 30
    days = [*range(0,dayn)]
    #print(days)
    r = 5 #Datum vom ersten Samstag -1 (da start von 0)
    while r <= dayn:
        days.remove(r)   #Samstag
        days.remove(r+1) #Sonntag
        r += 7
    days.remove(18) #Karfreitag
    days.remove(21) #Ostermontag
    #print(days)
    #days = [5,6,12,13,18,19,20,21,26,27]
    daygraphs = []
    combine = 1
    for x in days:
        temp = (data[row][ofs+x*i:ofs+(x+1)*i]).tolist()
        graphd = []
        j = 0
        #print(temp)
        for e in range(0,len(temp)):
            if e % combine == 0:
                graphd.append(temp[e])
                for c in range(0, combine-1):
                    graphd[j] += temp[e-c]
                j+=1
        daygraphs.append(graphd)
    median = [0] * len(daygraphs[0])
    for graph in daygraphs:
        i = 0
        for value in graph:
            median[i] += value
            i+=1
    for i in range(0,len(median)):
        median[i] /= len(daygraphs)
            
    graphd = daygraphs[0]
    #print(graphd)
    plt.xlabel('Zeit')
    plt.ylabel(data[row][ofs-1])
    step = float(len(graphd))/24
    steps = np.arange(0, len(graphd), step)
    x = []
    for j in range(0,24):
        x.append(time(j).strftime("%H:%M"))
    plt.xticks(steps, x, rotation=90)

    for g in daygraphs:
        plt.plot(g, color='b')
    plt.plot(median, color='r')


    #handfitted for "Hauptfahrstreifen Richtung Osten"
    mu = [None] * 3
    sigma = [None] * 3
    ncars = [None] * 3

    mu[0], sigma[0] = 15.5, 3
    mu[1], sigma[1] = 7.25, 1.7
    mu[2], sigma[2] = 10.5, 1.4
    ncars[0], ncars[1], ncars[2] = 3600, 1500, 650

    bins = [*np.arange(0,24,0.1)] #adjust draw points for a smooth graph

    #show handfitted distribution:
    #plt.plot(bins, getDistribution(mu,sigma,ncars,bins), linewidth=2, color='g')
    
    #automatic fitting (determining approx. car number for each normal distribution):
    mu = muFitting(median)
    print("mu:",mu)
    sigma = sigmaFitting(mu, median)
    print("sigma:", sigma)
    ncars = ncarsFitting(mu, sigma, median)
    print("ncars:", ncars)

    #show automatically fitted distribution:
    plt.plot(bins, getDistribution(mu,sigma,ncars,bins), linewidth=2, color='y')

    #use distribution to determine spawn times:
    spawnt = []    #final car spawn times
    for i in range(0,len(mu)):
        spawnt.append(np.random.normal(mu[i], sigma[i], ncars[i]))
    bins = [*np.arange(0,24,1)]
    plt.hist(spawnt, bins, histtype='barstacked') #shows cars spawned per hour
    # (the colors show which normal distribution was responsible)
    
    plt.title(str(data[row][ofs-1]) + " für 1-"+str(dayn)+".4.2019")
    plt.show()

#für Stundenwerte
def vehicleDistribuition(data):
	d = {}
	q_all = 0.0
	selection = [2,5,6]

	for i in selection:
		s = sum(data[i][ofs:])
		d[data[i][ofs-1]] = s
		q_all += s
	for key in d:
		d[key] = (d[key],round(d[key]/q_all,4))
	return d

def readData(loc):
    file = loc
    df = pd.read_excel(file)

    data = []
    for i in range(0,len(df.columns)):
	    data.append(df[df.columns[i]])
    return data

loc = "../../data-master/StudentenprojektMensaLSA/DZ943_SuedringWest_Hauptfahrstreifen_RichtungOsten_Stundenwerte_201904xx.xls"
ofs = 3 #offset

data = readData(loc)
#d = vehicleDistribuition(data)
#print(d)
showGraph(data)
