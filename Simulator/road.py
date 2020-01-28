import sys
import math
import random
import heapq

import cmath
import bezier
import numpy as np

from .car import Car
from .traffic_light import TrafficLight
from .road_object import RoadObject
from .helper_functions import verboseprint

class Road(RoadObject):
    """A road which is a single lane in the traffic simulation

    entities is a list of Entity objects, sorted by the distance they are from the start point
    Assuming there never will be a lot of entities on a single road it is justified to use
    a list instead of a priority queue

    connections is a list of tuples of (road_object: RoadObject, at_length : int) at this road 
    leads into

    path is a dictionary of paths, where destinations are keys and an index of the
    connection was the value
    
    wait_for is a list of (at_length, Road) tuples. Cars will wait at_length if road has any 
    cars on it

    start_siblings is a list of roads which originate from the same road as this one (exluding
    this one)
    
    end_siblings is a list of roads which end in the same road as this one (excluding this one)

    intersections is a list of (at_length, other_road, other_at_length) tuples where this road
    and other_road meet, at_length in relation to this road and other_at_length in relation
    to the other road
    """


    def __init__(self, coords, options={}, turn_signal=''):
        super().__init__()
        self._entities = []
        self._connections = []
        self._coords = coords
        self._curve = bezier.curve.Curve(np.array(list(zip(*coords))), 2)
        self._length = self._curve.length
        self._turn_signal = turn_signal
        self._options = options

        self.wait_for = []
        
        # Roads which begin and end together with this road
        self.start_siblings = []
        self.end_siblings = []
        self.intersections = []

        self.path = {}


    def __str__(self):
        return "RoadID:{}|len:{:.2f}|entities:{}".format(self._id, self._length, len(self._entities))


    def __repr__(self):
        return self.__str__()


    def update(self, step_size):
        """Updates all entities on current road

        Calls entity.advance() for each entity. 
        Then checks whether the entity has moved past the edge of road,
        if so it adds the entity to the next road and removes it from the current road.
        """
        # verboseprint(1, "id: {}\t".format(self._id), end=' -> ')
        # verboseprint(1, self._entities)
        cars_to_be_removed = set()
        for entity in self._entities:
            # verboseprint(2, "\t{}:".format(entity))
            ae_dist = 100
            ae_vel = 100
            ahead_entity = None
            take_con = None
            if isinstance(entity, Car):
                take_con = self.path[entity.destination]
                if take_con is None:
                    print("ERROR: Can't take expected connection here for {} to destination: {}".format(entity, entity.destination))
                    sys.exit()
                curr_con, curr_at_length, curr_to_length = self._connections[take_con]
                # verboseprint(2, '\t\tExit on id: {} at {} to {}'.format(curr_con.get_id(), curr_at_length, curr_to_length))
                ahead_entities_on_curr_road = self.get_entities(after_length=entity.get_pos()+.01, before_length=curr_at_length+.01)

                # verboseprint(2, "\t\tEntities between {} and {}: {}".format(entity.get_pos(), curr_at_length, ahead_entities_on_curr_road))
                # Check if there is a car on the same road as this car until your needed exit
                # verboseprint(2, '\t\t' + str(ahead_entities_on_curr_road))
                if ahead_entities_on_curr_road:
                    ahead_entity = ahead_entities_on_curr_road[-1]
                    ae_dist = ahead_entity.get_pos()-entity.get_pos()-ahead_entity.get_length()
                    # print("    -> normal: ae_dist: {}".format(ae_dist))
                    ae_vel = ahead_entity.get_vel()

                # Check if there is a car on the next road you need to take, adjust accordingly
                if isinstance(ahead_entity, TrafficLight):
                    if ahead_entity.can_go():
                        ae_dist = 100
                        ae_vel = 100

                ahead_entities_on_next_road = curr_con.get_entities(after_length=curr_to_length-entity.get_length()*2)
                # verboseprint(2,"\t\tEntities between {} and {}: {}".format(curr_to_length-entity.get_length(), curr_con.get_length(), ahead_entities_on_next_road))
                if ahead_entities_on_next_road:
                    for ahead_entity in ahead_entities_on_next_road:
                        # ahead_entity = ahead_entities_on_next_road[-1]
                        # verboseprint(2,"\t\tAHEAD_ENTITY %s" % ahead_entity)
                        # ae_dist = (curr_to_length-entity.get_pos())+ahead_entity.get_pos()-ahead_entity.get_length()
                        possible_ae_dist = ahead_entity.get_pos() - curr_to_length - ahead_entity.get_length() + (curr_at_length - entity.get_pos())
                        if possible_ae_dist < ae_dist:
                            ae_dist = possible_ae_dist
                            # print(curr_con, curr_at_length, curr_to_length)
                            # verboseprint(3, "\t\t\_> ae_dist: {}".format(ae_dist))
                            ae_vel = ahead_entity.get_vel()

                # Check the start of the sibling roads
                if entity.get_pos() < 10:
                    for sibling_road in self.start_siblings:
                        ahead_entities_on_next_road = sibling_road.get_entities(before_length=25)
                        for ahead_entity in ahead_entities_on_next_road:
                            if ahead_entity.get_pos() > entity.get_pos():
                                possible_ae_dist = ahead_entity.get_pos() - ahead_entity.get_length() - entity.get_pos()
                                if possible_ae_dist < ae_dist and possible_ae_dist < 10:
                                    ae_dist = possible_ae_dist
                                    ae_vel = ahead_entity.get_vel()

                # Check all connecting roads whether they have a car, even all the ones you are not taking
                if entity.get_pos() + 20 > self.get_length():
                    for con,at,to in self._connections:
                        if at >= entity.get_pos():
                            ahead_entities_on_next_road = con.get_entities(before_length=25)
                            for ahead_entity in ahead_entities_on_next_road:
                                possible_ae_dist = ahead_entity.get_pos() - ahead_entity.get_length() + (self.get_length() - entity.get_pos())
                                if possible_ae_dist < ae_dist:
                                    ae_dist = possible_ae_dist
                                    ae_vel = ahead_entity.get_vel()

                # Check all end siblings roads whether there is a car
                if entity.get_pos() + 15 > self.get_length():
                    for sibling_road in self.end_siblings:
                        ahead_entities_on_sibling_road = sibling_road.get_entities(after_length=sibling_road.get_length() - 15)
                        for ahead_entity in ahead_entities_on_sibling_road:
                            possible_ae_dist = (self.get_length() - entity.get_pos()) - (sibling_road.get_length() - ahead_entity.get_pos())
                            if possible_ae_dist < ae_dist and possible_ae_dist >= 0:
                                ae_dist = possible_ae_dist
                                ae_vel = ahead_entity.get_vel()

                # Check if next entity is perhaps blocked by another road
                for at_length, road in self.wait_for:
                    possible_ae_dist = at_length - entity.get_pos() - entity.get_min_dist()
                    if possible_ae_dist > 1:
                        if not road.is_empty():
                            if possible_ae_dist < ae_dist:
                                ae_dist = possible_ae_dist
                                ae_vel = 0
                            break

                # Check if next entity is perhaps blocked by another road
                for at_length, other_road, other_at_length in self.intersections:
                    if entity.get_pos() < at_length:
                        ahead_entities_on_parallel_road = other_road.get_entities(after_length=other_at_length-1, before_length=other_at_length+15)
                        if ahead_entities_on_parallel_road:
                            ahead_entity = ahead_entities_on_parallel_road[0]
                            if ahead_entity.get_pos() - ahead_entity.get_length() < other_at_length+1:
                                possible_ae_dist = at_length - entity.get_pos() - entity.get_min_dist()
                                if 0 < possible_ae_dist < ae_dist:
                                    ae_dist = possible_ae_dist
                                    ae_vel = 0


            # print("\t\tae_dist: {}, ae_vel:{}".format(ae_dist, ae_vel))
            entity.advance(step_size, ae_dist, ae_vel)

            # Move to next road if the car has gone too far
            if isinstance(entity, Car):
                curr_con, curr_at_length, curr_to_length = self._connections[take_con]
                # verboseprint(3, "\t\tcurr_con: {}".format(curr_con))
                # verboseprint(3, "\t\tcurr_at_length: {}".format(curr_at_length))
                # verboseprint(3, "\t\tcurr_to_length: {}".format(curr_to_length))
                if curr_at_length - entity.get_pos() < 10:
                    entity.set_turn_signal(curr_con.get_turn_signal())
                drove_ahead = entity.get_pos() - curr_at_length
                if drove_ahead > 0:
                    # entity.set_pos(drove_ahead+curr_to_length)
                    # verboseprint(1, "\t\t\033[32mMoving car {} from road ({}) at {:.2f} to road ({}) to {:.2f} \033[37m".format(entity, self, curr_at_length, curr_con, curr_to_length))
                    entity.prev_road = self
                    curr_con.add_entity(entity, at_length=curr_to_length)
                    cars_to_be_removed.add(entity.get_id())

        # Remove elements in place
        # Note that the [:] is important to not create copies of the elements
        self._entities[:] = [entity for entity in self._entities if entity.get_id() not in cars_to_be_removed]


    def add_connection(self, road, at_length=None, to_length=None):
        if at_length is None:
            at_length = self._length
        if to_length is None:
            to_length = 0
        self._connections.append((road, at_length, to_length))



    def reset_updated_status(self):
        for entity in self._entities:
            entity.reset_updated()


    def add_entity(self, entity, at_length=None):
        """Adds an entity at the position at_length

        If at_length is None then the entity will be inserted behind all other entities, or at 0
        whichever is smaller.
        In case the road is full this means that negative coordinates are possible, but this
        prevents the entities being in the list in the wrong order compared to their coordinates.
        Note that the entity position will be overriden.
        """

        if at_length is None:
            entity.set_pos(0)
            if self._entities:
                entity.set_pos(min(0, self._entities[-1].get_pos()-self._entities[-1].get_length()-entity.get_min_dist()))
            self._entities.append(entity)
        else:
            entity.set_pos(at_length)
            insert_at = len(self._entities)
            for i in range(len(self._entities)):
                if self._entities[i].get_pos() <= at_length:
                    insert_at = i
                    break
            # print(insert_at)
            self._entities.insert(insert_at, entity)


    def remove_entity(self, entity):
        self._entities.remove(entity)


    def trace_coords(self, dist=0.5):
        coords = self._curve.evaluate_multi(np.array([i/self._length for i in np.arange(0, self._length, dist)]))
        return list(zip(*coords))


    def get_coords(self):
        """Returns list of coordinates of the road as tuples
        """
        return self._coords.copy()


    def pos_to_coord(self, pos):
        rel = pos/self._length
        return tuple(self._curve.evaluate(rel).flatten())

    def coord_to_pos(self, coord):
        return self._curve.locate(np.array([coord]).T)*self._length

    def pos_to_rotation(self, pos):
        rel = pos/self._length
        rel2 = (pos-1)/self._length
        front = tuple(self._curve.evaluate(rel).flatten())
        behind = tuple(self._curve.evaluate(rel2).flatten())
        return cmath.polar(complex((front[0]-behind[0]), (front[1]-behind[1])))[1]


    def is_empty(self):
        return not self._entities


    def is_full(self):
        if self.get_entities(entity_class=Car, before_length=10):
            return True
        return False



    def get_entities(self, entity_class=None, after_length=None, before_length=None):
        if before_length is None:
            before_length = 1e9
        if after_length is None:
            after_length = -1e9
        entities_of_type = []
        for entity in self._entities:
            if after_length <= entity.get_pos() <= before_length:
                if entity_class is not None:
                    if isinstance(entity, entity_class):
                        entities_of_type.append(entity)
                else:
                    entities_of_type.append(entity)
        return entities_of_type


    def get_connections(self):
        return self._connections


    def get_cars(self):
        return self.get_entities(Car)


    def get_traffic_lights(self):
        return self.get_entities(TrafficLight)


    def get_length(self):
        return self._length


    def get_turn_signal(self):
        return self._turn_signal


    def _dist(self, coord1, coord2):
        return math.sqrt((coord1[0]-coord2[0])**2 + (coord1[1]-coord2[1])**2)


    def _len(self, coord):
        return math.sqrt(coord[0]**2 + coord[1]**2)


