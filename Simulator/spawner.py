import random

import numpy as np

from .car import Car
from .road import Road
from .road_object import RoadObject

class Spawner(RoadObject):
    """Spawns cars at the beginning of a road with a certain probability.
    
    The time the next car spawns depends on the Poisson distribution
    """

    def __init__(self, connection, distribution, options, start_time=0, average_time_for_next_car=40, name="lane_1", allowed=['pkw', 'lkw', 'bus']):
        super().__init__()
        self._connection = connection
        self._coords = connection.get_coords()[-1]
        self._time = start_time
        self._poisson_lambda = average_time_for_next_car
        self._options = options
        self._distribution = distribution
        self._name = name
        self._allowed = allowed

        self._next_car_times = {}
        self.update_next_car_times(['pkw', 'bus', 'lkw'])

        # Add some random time to current spawner
        self._time += random.randint(0, 100)


    def update(self, step_size):
        self._time += step_size
        next_car_times = list(self._next_car_times.items())
        random.shuffle(next_car_times)
        for car_type, next_car_time in next_car_times:
            car = self.get_car(car_type)
            if car is not None:
                if self._connection is not None:
                    self._connection.add_entity(car)

    def update_next_car_times(self, car_types):

        for car_type in car_types:
            self._next_car_times[car_type] = self._get_next_car_time(car_type)


    def get_car(self, car_type):
        if car_type in self._allowed:
            if not self._connection.is_full():
                if self._time > self._next_car_times[car_type]:
                    self._next_car_times[car_type] = self._get_next_car_time(car_type)
                    chance = random.uniform(0,1)
                    i = 0
                    while chance > self._distribution[i][1]:
                        chance -= self._distribution[i][1]
                        i += 1
                    return Car(destination=self._distribution[i][0], car_type=car_type, options=self._options, random_factor=np.random.normal(1, 0.2))
        return None


    def get_coords(self):
        return (self._coords, self._coords)


    def _get_next_car_time(self, car_type='pkw'):
        return self._time + np.random.poisson(self._options[car_type+"_"+self._name]) * np.random.normal(1, 0.2)



