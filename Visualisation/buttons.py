import sys, math, arcade, os
from . import graphs, vis
from gui_sim import MainGUI

pressed = None
path = os.path.dirname(os.path.abspath(__file__)) + "/sprites/"

def update_resolution(width_scaling, height_scaling, slider):
	global WIDTH, HEIGHT, slider_list
	global tabSprite, sliderSprite, buttonSprite
	WIDTH = width_scaling
	HEIGHT = height_scaling
	slider_list = slider
	
	tabSprite.scale = HEIGHT/2
	sliderSprite.scale = HEIGHT/2
	buttonSprite.scale = HEIGHT/2
	tabSprite.left = 0
	tabSprite.bottom = HEIGHT*690
	sliderSprite.left = 0
	sliderSprite.bottom = HEIGHT*109
	buttonSprite.left = 0
	buttonSprite.bottom = 0

def setup(simulator):
	global slider_nor, slider_press, s, tabSprite, sliderSprite, buttonSprite
	slider_nor = arcade.load_texture(f"{path}"+"slider_normal.png")
	slider_press = arcade.load_texture(f"{path}"+"slider_pressed.png")
    
	tabSprite = arcade.Sprite(f"{path}"+"gui_tabs_pkw.png")
	sliderSprite = arcade.Sprite(f"{path}"+"gui_slider.png")
	buttonSprite = arcade.Sprite(f"{path}"+"gui_buttons_none.png")
	s = simulator

def draw():
	tabSprite.draw()
	sliderSprite.draw()
	buttonSprite.draw()
	for slider in slider_list:
		if slider.visible:
			slider.draw()
	#arcade.draw_line(0, 6, 400, 6, arcade.color.RED, 1)


class Slider():
	def __init__(self, santa_x, santa_y, val, min_val, max_val, id, visible):
		self.center_x = santa_x
		self.center_y = santa_y
		self.val = float(val)
		self.min = min_val
		self.max = max_val
		self.id = id
		self.visible = visible
		
		if self.min >= self.max or self.val < self.min or self.val > self.max:
			print("Error: Falsche Werte für min_val, max_val oder val Parameter von Slider '"
					+ id + "'")
			print("min: " + str(self.min) + ", max: " + str(self.max) + ", val: " + str(self.val))
			sys.exit()

	def draw(self):

		self.pos = (self.val - self.min) * HEIGHT*240 / (self.max - self.min) + (self.center_x-HEIGHT*120)
		if pressed == self:
			arcade.draw_texture_rectangle(self.pos, self.center_y, HEIGHT*29, HEIGHT*14, slider_press)
		else:
			arcade.draw_texture_rectangle(self.pos, self.center_y, HEIGHT*29, HEIGHT*14, slider_nor)
		arcade.draw_text(format(self.val, '.1f'), self.center_x + HEIGHT*117,
							self.center_y + HEIGHT*19, arcade.color.BLACK, HEIGHT*13, width = 0,
							align="right", anchor_x="right", anchor_y="bottom")


def check_mouse_click(x, y):
	global pressed, tabSprite, tab
	
	#check mouse click for tabs
	if (x >= 0 and x <= HEIGHT*100 and y >= HEIGHT*690 and y <= HEIGHT*715):
		tab = 1
		for slider in slider_list:
			if slider.id[:3] == "pkw":
				slider.visible = True
			else:
				slider.visible = False
		tabSprite.texture = arcade.load_texture(f"{path}"+"gui_tabs_pkw.png", scale=HEIGHT/2)
	elif (x >= HEIGHT*101 and x <= HEIGHT*200 and y >= HEIGHT*690 and y <= HEIGHT*715):
		tab = 2
		for slider in slider_list:
			if slider.id[:3] == "lkw":
				slider.visible = True
			else:
				slider.visible = False
		tabSprite.texture = arcade.load_texture(f"{path}"+"gui_tabs_lkw.png", scale=HEIGHT/2)
	elif (x >= HEIGHT*201 and x <= HEIGHT*300 and y >= HEIGHT*690 and y <= HEIGHT*715):
		tab = 3
		for slider in slider_list:
			if slider.id[:3] == "bus":
				slider.visible = True
			else:
				slider.visible = False
		tabSprite.texture = arcade.load_texture(f"{path}"+"gui_tabs_bus.png", scale=HEIGHT/2)

	#check mouse click for buttons
	elif (x >= HEIGHT*30 and x <= HEIGHT*130 and y >= HEIGHT*74 and y <= HEIGHT*103):
		graphs.draw_graph1()
		buttonSprite.texture = arcade.load_texture(f"{path}"+"gui_buttons_1.png", scale=HEIGHT/2)
	elif (x >= HEIGHT*30 and x <= HEIGHT*130 and y >= HEIGHT*40 and y <= HEIGHT*69):
		graphs.draw_graph2()
		buttonSprite.texture = arcade.load_texture(f"{path}"+"gui_buttons_2.png", scale=HEIGHT/2)
	elif (x >= HEIGHT*30 and x <= HEIGHT*130 and y >= HEIGHT*6 and y <= HEIGHT*35):
		graphs.draw_graph3()
		buttonSprite.texture = arcade.load_texture(f"{path}"+"gui_buttons_3.png", scale=HEIGHT/2)
		
	elif (x >= HEIGHT*150 and x <= HEIGHT*177 and y >= HEIGHT*6 and y <= HEIGHT*35):
		MainGUI.decrease_speed(arcade.get_window())
		buttonSprite.texture = arcade.load_texture(f"{path}"+"gui_buttons_minus.png", scale=HEIGHT/2)
	elif (x >= HEIGHT*242 and x <= HEIGHT*269 and y >= HEIGHT*6 and y <= HEIGHT*35):
		MainGUI.increase_speed(arcade.get_window())
		buttonSprite.texture = arcade.load_texture(f"{path}"+"gui_buttons_plus.png", scale=HEIGHT/2)
	elif x > HEIGHT*300:
		pressed = "vis"

	#check mouse click for sliders
	else:
		for slider in slider_list:
			if (slider.visible and y <= slider.center_y + HEIGHT*7
				and y >= slider.center_y - HEIGHT*7):
				if (x <= slider.center_x + HEIGHT*120 and x >= slider.center_x - HEIGHT*120):
					pressed = slider
					pressed.val = (x-pressed.center_x+HEIGHT*120) * (pressed.max - pressed.min) / (HEIGHT*240) + pressed.min

					if(pressed.id[4:] == "des_vel"):
						s.set_options({pressed.id: pressed.val/3.6})
					elif pressed.id[4:8] == "lane":
						s.set_options({pressed.id: 2 ** (pressed.max + pressed.min - pressed.val)})
					else:
						s.set_options({pressed.id: pressed.val})
					break
				elif (x <= slider.pos + HEIGHT*15 and x >= slider.pos - HEIGHT*15):
					pressed = slider
					break

def check_mouse_release():
	global pressed
	pressed = None
	buttonSprite.texture = arcade.load_texture(f"{path}"+"gui_buttons_none.png", scale=HEIGHT/2)

def check_mouse_drag(x, y, dx, dy):
	global pressed
	if isinstance(pressed, Slider):
		val = pressed.val + dx * (pressed.max - pressed.min) / (HEIGHT*240)

		if(val >= pressed.min and val <= pressed.max and x >= HEIGHT*30 and x <= HEIGHT*270):
			pressed.val = val
		elif x > HEIGHT*270 or val > pressed.max:
			pressed.val = pressed.max
		elif x < HEIGHT*30 or val < pressed.min:
			pressed.val = pressed.min
		if(pressed.id[4:] == "des_vel"):
			s.set_options({pressed.id: pressed.val/3.6})
		elif pressed.id[4:8] == "lane":
			s.set_options({pressed.id: 2 ** (pressed.max + pressed.min - pressed.val)})
		else:
			s.set_options({pressed.id: pressed.val})
	elif pressed == "vis":
		vis.update_offset(dx ,dy)
