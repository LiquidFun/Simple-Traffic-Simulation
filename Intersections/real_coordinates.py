import math

def transform(key, v,c):
	mx = v[1][0]-v[0][0]
	x = v[0][0] + mx/2
	my = v[1][1]-v[0][1]
	y = v[0][1] + my/2

	x -= c[0]
	y = c[1] - y
	x *= 2.50
	y *= 2.50
	x = round(x,4)
	y = round(y,4)

	l = math.sqrt(mx*mx+my*my)
	#print(l*2.5)
	mx *= 1/l
	my *= 1/l
	if key == 's3l':
		nx = round(x-15*(-my),4)
		ny = round(y-15*(-mx),4)
	else:
		nx = round(x-150*(-my),4)
		ny = round(y-150*(-mx),4)
	return [(nx,ny),(x,y)]

def get_coordinates():
	measurements = {
		'center': (20.8, 13.0),
		# coordinates for the right side and left side of intersection entry
		's1r': [(10.77, 8.63) ,(11.86, 7.57)],
		's1l': [(11.86,7.57), (12.94, 6.51)],
		's1o': [(15.06, 5.00), (16.69, 3.27)],
		's2r': [(23.76, 2.29), (24.88, 3.24)],
		's2l': [(24.88, 3.28), (25.77, 4.04)],
		's2o': [(25.80, 4.07), (26.89, 5.00)],
		's3r': [(28.87, 13.11), (27.95, 14.0)],
		's3m': [(27.95, 14.0),(26.95, 14.97)],
		's3l': [(26.95, 14.99), (26.13, 15.79)], # start(l)':33.48, 21.68 volle breite bei(r)':29.75, 17.83
		's3ol': [(23.26, 17.76), (22.32, 18.67)],
		's3or': [(22.32, 18.67), (21.38, 19.58)],
		's4r': [(15.27, 19.60), (14.34, 18.70)],
		's4l': [(14.34, 18.70), (13.37, 17.76)],
		's4o': [(13.37, 17.74), (12.46, 16.85)],
	}

	coordinates = {}
	c = measurements['center']
	for key, values in measurements.items():
		if key != 'center':
			coordinates[key] = transform(key, values,c)
		#measurements[key][i][j] - c[j])

	return(coordinates)

#print(get_coordinates())
