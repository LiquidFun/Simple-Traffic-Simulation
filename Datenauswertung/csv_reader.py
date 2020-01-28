import csv
from datetime import datetime, timedelta

def readSignaldaten():
	with open('signaldaten.csv2', 'r') as csvfile:
		dialect = csv.Sniffer().sniff(csvfile.read(1024))
		csvfile.seek(0)
		reader = csv.reader(csvfile, dialect)

		bc = 0
		s = {}
		name = ""
		for row in reader:
			if row[0] == 'type':
				bc = 0
			if bc == 1:
				if row[0] == 'SGR':     #equals: type = SGR
					name = row[2]
					s[name] = []
					print(name)
				#else:
					#TODO
			if bc >= 3:
				s[name].append([datetime.fromisoformat(row[0][:23]),row[1]])
			bc+=1
		return s

def readDetektordaten():
	with open('detektordaten.csv', 'r') as csvfile:
		dialect = csv.Sniffer().sniff(csvfile.read(1024))
		csvfile.seek(0)
		reader = csv.reader(csvfile, dialect)

		bc = 0
		s = {}
		name = ""
		for row in reader:
			if row[0] == 'type':
				bc = 0
			if bc == 1:
				if row[0] == 'DET':     #equals: type = DET
					name = row[2]
					s[name] = []
					#print(name)
				#else:
					#TODO
			if bc >= 3:
				s[name].append([datetime.fromisoformat(row[0][:23]),row[1]])
			bc+=1
		return s

daten = readDetektordaten();
for det in daten:
	i = 1
	gt = timedelta() #Gesamtzeit, für die der Detetor aktiv ist, d.h. die Spur am warten ist
	before = daten[det][0][0]
	after = daten[det][0][0]
	for entry in daten[det]:
		if(i%2 == 0):
			before = entry[0]
		if(i%2 == 1):
			after = entry[0]
			gt += after-before
		i+=1
	#print(gt)
	seconds = gt.total_seconds()
	print(str(det)+":\t"+str(seconds)+"s")
	#break
