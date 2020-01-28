import arcade, os

SCALE = 1 # scaling of light textures
path = os.path.dirname(os.path.abspath(__file__)) + "/sprites/"

textures = {}

def update_textures(WIDTH, HEIGHT, zoom):
	global textures
	if WIDTH < HEIGHT:
		res = WIDTH*zoom*SCALE
	else:
		res = HEIGHT*zoom*SCALE

	textures["red"] = arcade.load_texture(f"{path}"+"ampel_rot.png", scale=res)
	textures["yellow"] = arcade.load_texture(f"{path}"+"ampel_gelb.png", scale=res)
	textures["green"] = arcade.load_texture(f"{path}"+"ampel_gruen.png", scale=res)
	textures["redyellow"] = arcade.load_texture(f"{path}"+"ampel_rotgelb.png", scale=res)

class Traffic_light(arcade.Sprite):
	
	def __init__(self, id, x, y, rot):
		super().__init__()
		
		self.id = id
		self.pos_x = x
		self.pos_y = y
		self.radians = rot
		self.texture = arcade.load_texture(f"{path}"+"ampel_rot.png")

	def update(self, col):
		global textures
			
		if col == 'r':
			self.texture = textures['red']
		elif col == 'g':
			self.texture = textures['green'] 
		elif col =='y': 
			self.texture = textures['yellow']  
		elif col == 'ry':
			self.texture = textures['redyellow']
