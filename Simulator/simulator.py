import time
import sys

from Intersections import debug_intersection
from Intersections import simple_intersection
from Intersections import complex_intersection
from Intersections import threeway_intersection
from Intersections import real_intersection
from .road import Road
from .spawner import Spawner
from .car import Car
from .traffic_light import TrafficLight
from .helper_functions import verboseprint

class Simulator: 
    def __init__(self, road_objects=None):
        self._time = 0
        self._real_time = time.time()
        self.options = {
            "pkw_max_acc"   : 1.2,
            "pkw_des_vel"   : 13.8888888,
            "pkw_min_dist"  : 2,
            "pkw_time_dist" : 2,
            "pkw_comf_dec"  : 1.7,
            "pkw_length"    : 5,
            "pkw_lane_1"    : 20,
            "pkw_lane_2"    : 50,
            "pkw_lane_3"    : 20,
            "pkw_lane_4"    : 15,
            "lkw_max_acc"   : 0.5,
            "lkw_des_vel"   : 13.8888888,
            "lkw_min_dist"  : 3,
            "lkw_time_dist" : 3,
            "lkw_comf_dec"  : 1.2,
            "lkw_length"    : 10,
            "lkw_lane_1"    : 80,
            "lkw_lane_2"    : 200,
            "lkw_lane_3"    : 80,
            "lkw_lane_4"    : 300,
            "bus_max_acc"   : 0.6,
            "bus_des_vel"   : 13.8888888,
            "bus_min_dist"  : 3,
            "bus_time_dist" : 3,
            "bus_comf_dec"  : 1.3,
            "bus_length"    : 15,
            "bus_lane_1"    : 200,
            "bus_lane_2"    : 300,
            "bus_lane_3"    : 200,
            "bus_lane_4"    : 300,
            "debug_log"     : [],
        }
        self._road_objects = real_intersection.get_roads(options=self.options)
        self._traffic_lights = [tf for ro in self._road_objects for tf in ro.get_entities(TrafficLight)]


    def update(self, step_size=1.0/10.0):
        verboseprint(1, "================== Real Time: {:.1f} Simulation Time: {:.1f} ==================".format(time.time() - self._real_time, self._time))
        # self.options['debug_log'] = []
        self._time += step_size

        for ro in self._road_objects:
            ro.update(step_size)
        for ro in self._road_objects:
            ro.reset_updated_status()

        # Check if all unique IDs
        ids = set()
        for ro in self._road_objects:
            for car in ro.get_entities(Car):
                if car.get_id() in ids:
                    print("Same ID {} on different roads found".format(car.get_id()))
                    sys.exit()
                ids.add(car.get_id())

    def get_sensors(self): 
        return [tf.get_sensor() for tf in self._traffic_lights]


    def get_cars(self):
        cars = []
        for ro in self._road_objects:
            for car in ro.get_entities(Car):
                car_api = car.get_api()
                pos_on_road = min(car_api['position']-car_api['length']/2, ro.get_length())
                curr_coords = ro.pos_to_coord(pos_on_road)

                # If the car is not yet entirely on the new road, i.e. it's position is negative
                # then take the rotation from the previous road and build the average coordinate
                # between the two roads, accounting more fore the new road the fruther ahead you 
                # get. Prevents jumps when switching roads
                if pos_on_road < 0 and car.prev_road is not None:
                    pos_on_prev_road = car.prev_road.get_length() + pos_on_road
                    prev_coords = car.prev_road.pos_to_coord(pos_on_prev_road)
                    m1 = abs(pos_on_road/car_api['length']*2)
                    m2 = 1-m1
                    car_api['coords'] = (curr_coords[0]*m2 + prev_coords[0]*m1, curr_coords[1]*m2 + prev_coords[1]*m1)
                    car_api['rotation'] = car.prev_road.pos_to_rotation(pos_on_prev_road)
                else:
                    car_api['coords'] = curr_coords
                    car_api['rotation'] = ro.pos_to_rotation(pos_on_road)

                cars.append(car_api)
        return cars

    def get_roads(self, dist=0.5):
        roads = []
        for ro in self._road_objects:
            roads.append(ro.trace_coords(dist=dist))
        return roads


    def get_traffic_lights(self):
        traffic_lights = []
        for tf in self._traffic_lights:
            tf_api = tf.get_api()
            tf_api['coords'] = tf.road.pos_to_coord(tf_api['position'])
            tf_api['rotation'] = tf.road.pos_to_rotation(tf_api['position'])
            traffic_lights.append(tf_api)
        return traffic_lights


    def get_debug_log(self):
        """Returns a list of ((x,y), string) tuples which can be displayed in the visualiser

        (x,y) is a tuple of coordinates representing where the message should be displayed,
        string is the message to be displayed
        """
        # return []
        # return [((0,0), "test"), ((1,1), "test2")]
        return self.options['debug_log']



    def get_options(self):
        opt = self.options.copy()
        opt.pop('debug_log')
        return opt


    def set_options(self, new_options):
        for opt, val in new_options.items():
            self.options[opt] = val

            # Update spawner rates
            for car_type in ['pkw', 'bus', 'lkw']:
                if (car_type + "_lane") in opt:
                    for ro in self._road_objects:
                        if isinstance(ro, Spawner):
                            ro.update_next_car_times([car_type])


    def get_time(self):
        return self._time


    def show(self):
        """Prints the current board including cars to the console

        '.' is a road
        '#' is a car
        """

        min_x = 1e9
        min_y = 1e9
        max_x = -1e9
        max_y = -1e9
        for ro in self._road_objects:
            c = ro.get_coords()
            min_x = min(min_x, c[0][0])
            min_y = min(min_y, c[0][1])
            max_x = max(max_x, c[1][0])
            max_y = max(max_y, c[1][1])

        field = [[" "] * (int(round(max_x-min_x))) for i in range(int(round(max_y-min_y)))]
        for ro in self._road_objects:
            for coords in ro.trace_coords():
                y, x = int(round(coords[1]+min_y)), int(round(coords[0])+min_x)
                if field[y][x] == ' ':
                    field[y][x] = '.'

            for car in ro.get_entities(Car):
                coords = ro.pos_to_coord(car.get_pos())
                y, x = int(round(coords[1]+min_y)), int(round(coords[0])+min_x)
                try:
                    field[y][x] = '\033[033m#\033[037m'
                except:
                    pass

        for line in field:
            print(''.join(line))
        print()

