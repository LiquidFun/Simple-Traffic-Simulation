from arcade.gui import Theme
from Visualisation import buttons, vis, graphs
from Simulator.simulator import Simulator
import math, arcade

SCREEN_TITLE = "Verkehrssimulation"
SLIDER_RANGE = [ #Wertebereiche für die Slider (min, max)
		[0.1, 3], #Maximalbeschleunigung
		[10, 150], #Wunschgeschwindigkeit 	 #150m/s = 540km/h
		[1.5, 5], #Zeitabstand
		[1, 10], #Minimalabstand
		[0.1, 10], #komfortable Verzögerung
		[1, 12], #Spur 1
		[1, 12], #Spur 2
		[1, 12], #Spur 3
		[1, 12]] #Spur 4
TAB_LIST = ["pkw", "lkw", "bus"]

class MainGUI(arcade.Window):

	step_size = 16/60
	update_rate = 1/60
	
	def __init__(self, width, height, title):
		global s
		self.step_size = 16/60
		update_rate = 1/60
		
		super().__init__(width, height, title, resizable=True)
		self.set_update_rate(self.update_rate)
		arcade.set_background_color(arcade.color.WHITE)
		s = Simulator()
		vis.setup(s)
		buttons.setup(s)
		graphs.setup(s)

	def set_gui_elements(self):
		global s, SLIDER_RANGE

		self.slider_list = []
		active = True
		dic = s.get_options()
		for i in TAB_LIST:
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*639, dic[i + "_max_acc"],
				SLIDER_RANGE[0][0], SLIDER_RANGE[0][1],	i + "_max_acc", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*579, dic[i + "_des_vel"]*3.6, #multiplied by 3.6 to convert m/s into km/h
				SLIDER_RANGE[1][0], SLIDER_RANGE[1][1],	i + "_des_vel", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*519, dic[i + "_min_dist"],
				SLIDER_RANGE[2][0], SLIDER_RANGE[2][1],	i + "_min_dist", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*459, dic[i + "_time_dist"],
				SLIDER_RANGE[3][0], SLIDER_RANGE[3][1],	i + "_time_dist", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*399, dic[i + "_comf_dec"],
				SLIDER_RANGE[4][0], SLIDER_RANGE[4][1],	i + "_comf_dec", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*315,
				SLIDER_RANGE[5][1] + SLIDER_RANGE[5][0] - math.log2(dic[i + "_lane_1"]),
				SLIDER_RANGE[5][0],	SLIDER_RANGE[5][1],	i + "_lane_1", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*255,
				SLIDER_RANGE[6][1] + SLIDER_RANGE[6][0] - math.log2(dic[i + "_lane_2"]),
				SLIDER_RANGE[6][0], SLIDER_RANGE[6][1], i + "_lane_2", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*195,
				SLIDER_RANGE[7][1] + SLIDER_RANGE[7][0] - math.log2(dic[i + "_lane_3"]),
				SLIDER_RANGE[7][0], SLIDER_RANGE[7][1],	i + "_lane_3", active))
			self.slider_list.append(buttons.Slider(HEIGHT*150, HEIGHT*135,
				SLIDER_RANGE[8][1] + SLIDER_RANGE[8][0] - math.log2(dic[i + "_lane_4"]),
				SLIDER_RANGE[8][0], SLIDER_RANGE[8][1],	i + "_lane_4", active))
			active = False

	def increase_speed(self):
		if self.step_size <= 32*self.update_rate and self.step_size >= 1*self.update_rate: 
			self.step_size = self.step_size*2
		elif self.step_size < 1*self.update_rate:
			self.step_size = 1*self.update_rate
	
	def decrease_speed(self):
				
		if self.step_size >= 2*self.update_rate:
			self.step_size = self.step_size/2
		elif self.step_size < 2*self.update_rate:
			self.step_size = 0
	
	def on_mouse_press(self, x, y, button, key_modifiers):
		buttons.check_mouse_click(x, y)
	

	def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
		if x > HEIGHT*300:
			vis.update_zoom(scroll_y)

	def on_mouse_release(self, x, y, button, key_modifiers):
		buttons.check_mouse_release()

	def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
		buttons.check_mouse_drag(x, y, dx, dy)

	def on_resize(self, screen_width, screen_height):
		global WIDTH, HEIGHT
		
		super().on_resize(screen_width, screen_height)
		WIDTH = screen_width/1280
		HEIGHT = screen_height/720
		self.set_gui_elements()
		buttons.update_resolution(WIDTH, HEIGHT, self.slider_list)
		vis.update_resolution(WIDTH, HEIGHT)
		
	def on_update(self, delta_time):
				
		vis.on_update(self.step_size)
		graphs.on_update()
		
	def on_draw(self):
		arcade.start_render()
		super().on_draw()
		vis.draw_loop()
		buttons.draw()
		
		#shows the simulation time and speed on screen
		time = s.get_time()
		clock_string = "{:0>2}:{:0>2}".format(math.floor((time/3600)%24), math.floor((time/60)%60))
		speed = (self.step_size/self.update_rate)
		
		arcade.draw_text("Simulationszeit:", start_x=HEIGHT*210, start_y=HEIGHT*85, 
				color=arcade.color.BLACK, font_size=HEIGHT*13, width = int(HEIGHT*150), align="center", anchor_x="center", anchor_y="baseline")
		arcade.draw_text(clock_string, start_x=HEIGHT*210, start_y=HEIGHT*65, 
				color=arcade.color.BLACK, font_size=HEIGHT*13, width = int(HEIGHT*150), align="center", anchor_x="center", anchor_y="baseline")
		arcade.draw_text("Geschwindigkeit:", start_x=HEIGHT*210, start_y=HEIGHT*40, 
				color=arcade.color.BLACK, font_size=HEIGHT*13, width = int(HEIGHT*150), align="center", anchor_x="center", anchor_y="baseline")
		arcade.draw_text(f"{speed:2.0f}x", start_x=HEIGHT*210, start_y=HEIGHT*15, 
				color=arcade.color.BLACK, font_size=HEIGHT*13,width = int(HEIGHT*150), align="center", anchor_x="center", anchor_y="baseline")

def main():
	gui = MainGUI(1280, 720, SCREEN_TITLE)
	arcade.run()

if __name__ == "__main__":
	main()
