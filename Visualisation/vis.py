import math, os, arcade
from . import car_vis
from . import traffic_light_vis
from . import cross
from Simulator.simulator import Simulator

car_list = arcade.SpriteList(use_spatial_hash=False)
boundary_x, boundary_y = 1400, 1600

def setup(simulator):
	global s, light_list, offset_x, offset_y, zoom, cross_tex
	offset_x, offset_y, zoom = 0, 0, 1
	s = simulator
	light_list = arcade.SpriteList(use_spatial_hash=False)
	for dic in s.get_traffic_lights():
		light = traffic_light_vis.Traffic_light(dic['id'], (dic['coords'][0]*12),
					(dic['coords'][1]*12), dic['rotation'])
		light_list.append(light)
	cross.create_cross_png(s.get_roads())
	cross_tex = arcade.load_texture(os.path.dirname(os.path.abspath(__file__)) + "/sprites/cross.png")
	car_vis.setup_textures()

def update_resolution(width_scaling, height_scaling):
	global WIDTH, HEIGHT, offset_x, offset_y
	global light_list
	WIDTH = width_scaling
	HEIGHT = height_scaling
	
	car_vis.update_scaling(round(min(WIDTH,HEIGHT)*zoom, 2))
	traffic_light_vis.update_textures(WIDTH, HEIGHT, zoom)
	update_offset(0, 0)
	
	for light in light_list:
		light.center_x = WIDTH*(light.pos_x*zoom+790+offset_x)
		light.center_y = HEIGHT*(light.pos_y*zoom+360+offset_y)

def update_offset(dx, dy):
	global offset_x, offset_y
	offset_x += dx/WIDTH
	offset_y += dy/HEIGHT

	if offset_x > boundary_x*zoom:
		offset_x = boundary_x*zoom
	elif offset_x < -boundary_x*zoom:
		offset_x = -boundary_x*zoom
	if offset_y > boundary_y*zoom:
		offset_y = boundary_y*zoom
	elif offset_y < -boundary_y*zoom:
		offset_y = -boundary_y*zoom

	for light in light_list:
		light.center_x = WIDTH*(light.pos_x*zoom+790+offset_x)
		light.center_y = HEIGHT*(light.pos_y*zoom+360+offset_y)

def update_zoom(scroll_y):
	global zoom
	zoom += scroll_y/10
	zoom = max(0.1, min(zoom, 2))
	car_vis.update_scaling(round(min(WIDTH,HEIGHT)*zoom, 2))
	
	traffic_light_vis.update_textures(WIDTH, HEIGHT, zoom)
	for light in light_list:
		light.center_x = WIDTH*(light.pos_x*zoom+790+offset_x)
		light.center_y = HEIGHT*(light.pos_y*zoom+360+offset_y)

def draw_loop():
	try:
		cross_tex.draw(WIDTH*(790+offset_x), HEIGHT*(360+offset_y), WIDTH*zoom*3400, HEIGHT*zoom*3400)
		car_list.draw()
		light_list.draw()
	except:
		print("Texture too large")
	
	#debug function: displays debug messages at specified coordinates
	logs = s.get_debug_log()
	for log in logs:
		x = log[0][0]
		y = log[0][1]
		message = log[1]
		arcade.draw_text(f"{message}", WIDTH*(x*12+790+offset_x), HEIGHT*(y*12+360+offset_y), arcade.color.RED, 20)

def on_update(step_size):
	s.update(step_size)

	cars = s.get_cars()
	
	# Get IDs for each car from simulator
	dic_id = set(curr["id"] for curr in cars)
	
	# Remove cars no longer in the intersection
	for car in car_list:
		if car.id not in dic_id:
			car.kill()

	# Get IDs for each from visualiser
	car_id = set(car.id for car in car_list)

	# for dic in cars:
	# 	if dic["id"] not in car_id:
	# 		car_list.append(car_vis.Car(dic["id"]))

	id_to_car_vis = {car.id:car for car in car_list}

	# Update each car in car list, add new ones if they don't exist yet
	for dic in cars:

		# Add car if it has not been added
		dic_id = dic['id']
		if dic_id not in id_to_car_vis:
			new_car = car_vis.Car(dic_id)
			car_list.append(new_car)
			id_to_car_vis[dic_id] = new_car 

		# Update cars
		id_to_car_vis[dic_id].update(
			WIDTH*(dic["coords"][0]*zoom*12+790+offset_x),
			HEIGHT*(dic["coords"][1]*zoom*12+360+offset_y),
			dic["rotation"],
			dic["braking"],		
			dic["turn_signal"], 
			dic["type"]
		)
	
	for dic in s.get_traffic_lights():
		for light in light_list:
			if light.id == dic['id']:
				light.update(dic['phase'])
	
