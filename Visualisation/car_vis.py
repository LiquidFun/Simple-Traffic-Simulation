import math, random, arcade, os

dur = 15 # duration of blinking cycle
path = os.path.dirname(os.path.abspath(__file__)) + "/sprites/"
textures = {}

def setup_textures():
	global textures

	map_texture_to_file = [
		("_nor", ""),
		("_nor_left", "_links"),
		("_nor_right", "_rechts"),
		("_brk", "_bremsen"),
		("_brk_left", "_bremsen_links"),
		("_brk_right", "_bremsen_rechts"),
	]
	for car_type, texture_count in [("pkw",4), ("bus",1), ("lkw",1)]:
		for i in range(texture_count):
			n = str(i+1)
			for name, texture in map_texture_to_file:
				key = f"{car_type}{n}{name}"
				textures[key] = arcade.load_texture(f"{path}{car_type}{n}{texture}.png")

def update_scaling(scaling):
	global scaling_factor
	scaling_factor = 0.6*scaling

class Car(arcade.Sprite):
	
	def __init__(self, id):
		super().__init__()
		self.id = id
		self.col = random.randint(1,4) #color of vehicle

		self.count = 0	#counter for blinking textures
		self.blink = False  #Indication if blinking lights are on or off (not if blinking cycle is active!)

	def update(self, x, y, rot, braking, turn_signal, type):
		global textures

		self.center_x = x
		self.center_y = y
		self.radians = rot
		self.tex = type
		
		if type != "pkw":
			self.col = 1

		#Determine car color
		self.tex += str(self.col) + "_"

		#Determine if car is braking
		self.tex += "brk" if braking else "nor"

		#Determine if a car should be blinking
		if turn_signal == "":
			self.count = 0
		else:
			if self.count >= dur:
				self.count = 0
				self.blink = not self.blink
			elif self.blink:
				self.tex += "_" + turn_signal
			self.count += 1

		self.scale = 1
		self.texture = textures[self.tex]
		self.scale = scaling_factor

		#debug function, prints the cars ID next to it
		#arcade.draw_text(f"{self.id}", x, y, arcade.color.WHITE, 20)
