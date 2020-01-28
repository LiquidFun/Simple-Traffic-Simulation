from PIL import Image, ImageDraw, ImageFilter
import math, os

def create_cross_png(road_list):
	im = Image.new("RGB", (6800,6800), (255,255,255))
	draw = ImageDraw.Draw(im)

	for road in road_list:
		if not road == []:
			for i in range(len(road)):
				if i < len(road)-1:
					x1 = road[i][0]*24+im.size[0]/2 #x position des aktuellen straßenblocks
					y1 = im.size[1]/2-road[i][1]*24 #y
					x2 = road[i+1][0]*24+im.size[0]/2 #x position des nächsten straßenblocks
					y2 = im.size[1]/2-road[i+1][1]*24 #y
					vec_x = 2*(x2-x1) #x vektor aktueller straßenblock -> nächster straßenblock
					vec_y = 2*(y2-y1) #y mit 2 multipliziert für längere, dadurch überlappende Blöcke

					orth_x = (-vec_y/vec_x) #x-wert des orthogonalen vektors mit y-wert=1
					nor_x = 48*orth_x/math.sqrt(orth_x ** 2 + 1) #x orthogonaler vektor
					nor_y = 48/math.sqrt(orth_x ** 2 + 1) #y auf länge 48 (2*straßenbreite) normiert

					draw.polygon([(x1+nor_x, y1+nor_y), (x1+nor_x+vec_x, y1+nor_y+vec_y),
					(x1-nor_x+vec_x, y1-nor_y+vec_y), (x1-nor_x, y1-nor_y)], fill=(53,53,53))

	im = im.resize((3400,3400),resample=Image.LANCZOS)
	im.save(os.path.dirname(os.path.abspath(__file__)) + "/sprites/cross.png", "PNG")
