import sys
import math

import numpy as np

from .road import Road
from .traffic_light import TrafficLight
from .destination import Destination
from .spawner import Spawner

class Intersection:
    """ intersections is a list of lists where each sublist describes the roads in the intersection
    """
    def __init__(self, options={}):
        self._roads = []
        self._destinations = []
        self._options = options


    def add_road(self, coords=[], start_road=None, end_road=None, turn_signal=None):
        """Adds a road with the specified coords

        Coords has to be at least of size 2, can be any length. It is a list of tuples (x,y).
        A bezier curve will be drawn out of these points, the first point being the starting point.

        If instead given both start and end, a middle point will be interpolated where the line between
        (start_road) and (end_end) meets for the bezier curve. Useful to avoid
        calculating the middle curve point.
        """

        # line_intersection function by Paul Draper from stackoverflow.com:
        # https://stackoverflow.com/a/20677983
        def line_intersection(line1, line2):
            xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
            ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                return None

            d = (det(*line1), det(*line2))
            x = det(d, xdiff) / div
            y = det(d, ydiff) / div
            return x, y


        # get_angle function by Eric from stackoverflow.com:
        # https://stackoverflow.com/a/35178910
        def get_angle(p0, p1, p2):
            """ compute angle (in degrees) for p0p1p2 corner
            Inputs:
                p0,p1,p2 - points in the form of [x,y]
            """
            v0 = np.array(p0) - np.array(p1)
            v1 = np.array(p2) - np.array(p1)

            angle = np.math.atan2(np.linalg.det([v0,v1]),np.dot(v0,v1))
            return np.degrees(angle)


        if len(coords) >= 2:
            self._roads.append(Road(coords, options=self._options))
            return self._roads[-1]
        elif start_road is not None and end_road is not None:
            if isinstance(start_road, Road) and isinstance(end_road, Road):
                sr_coords = start_road.get_coords()
                er_coords = end_road.get_coords()

                # Calculate intersection point
                intersection_point = line_intersection((sr_coords[-2], sr_coords[-1]), (er_coords[0], er_coords[1]))

                if intersection_point is not None:
                    angle = get_angle(sr_coords[-1], intersection_point, er_coords[0])
                    if abs(angle) < 30:
                        intersection_point = ((sr_coords[-1][0]+er_coords[0][0])/1.9, (sr_coords[-1][1]+er_coords[0][1])/2.1)
                        angle = get_angle(sr_coords[-1], intersection_point, er_coords[0])
                    if turn_signal is None:
                        turn_signal = ''
                        if 30 < angle < 120:
                            turn_signal = "right"
                        elif -120 < angle < -30: 
                            turn_signal = "left"
                    curr = Road([sr_coords[-1], intersection_point, er_coords[0]], turn_signal=turn_signal, options=self._options)
                else:
                    if turn_signal is None:
                        turn_signal = ''
                    curr = Road([sr_coords[-1], er_coords[0]], turn_signal=turn_signal, options=self._options)
                start_road.add_connection(curr)
                curr.add_connection(end_road)
                self._roads.append(curr)
                return self._roads[-1]

            else:
                print("ERROR: Not of class Road")
        return None


    def traffic_rules(self):
        """Determines that cars should wait for another road

        If there are any cars on `road_b` then cars on `road_a` will wait
        for road_b to clear.
        """
        # Go over each road pair, checking each pair only once
        for ra in range(len(self._roads)):
            for rb in range(ra+1, len(self._roads)):
                road_a = self._roads[ra] 
                road_b = self._roads[rb] 

                # Check if both are Road objects
                if isinstance(road_a, Road) and isinstance(road_b, Road):

                    # Calculate intersection point and check whether it exitst
                    intersection_points = road_a._curve.intersect(road_b._curve)
                    if len(intersection_points[0]) != 0:
                        first = intersection_points[0][0]
                        second = intersection_points[1][0]

                        # Check whether the intersection point should accounted for
                        if 0.1 < first < 0.9 and 0.1 < second < 0.9:
                            pos_f = first * road_a.get_length()
                            pos_s = second * road_b.get_length()
                            road_a.intersections.append((pos_f, road_b, pos_s))
                            road_b.intersections.append((pos_s, road_a, pos_f))
                            if road_a.get_turn_signal() == 'left' and road_b.get_turn_signal() != 'left':
                                road_a.wait_for.append((pos_f, road_b))
                            elif road_b.get_turn_signal() == 'left':
                                road_b.wait_for.append((pos_s, road_a))
        # Sort roads by distance 
        for ra in self._roads:
            if isinstance(ra, Road):
                ra.wait_for.sort()

        # Matches all successors to their predecessors since this isn't easily readable from the data
        # used to build end_siblings
        successor_to_predecessors = {}

        # Go over each road and add it's siblings
        for road in self._roads:
            if isinstance(road, Road):
                cons = [con for con,at,to in road._connections if isinstance(con, Road) and at+1 > road.get_length()]
                for i in range(len(cons)):
                    # Configure successor to predecessor stuff
                    if cons[i] not in successor_to_predecessors:
                        successor_to_predecessors[cons[i]] = []
                    successor_to_predecessors[cons[i]].append(road)
                    # Configure start_siblings
                    for j in range(i+1, len(cons)):
                        cons[i].start_siblings.append(cons[j])
                        cons[j].start_siblings.append(cons[i])

        for successor, predecessors in successor_to_predecessors.items():
            for predecessor in predecessors:
                predecessor.end_siblings = [sibling for sibling in predecessors if sibling is not predecessor]
        


    def adjacent(self, road_a, road_b, con_dist=10):
        """Adds a number of connections between 2 roads

        con_dist is the distance between each connection, this therefore determines how many
        connections there will be
        """
        if road_a is road_b:
            print("ERROR: Same road supplied to adjacent")
            sys.exit()

        def dist(a, b):
            (x1,y1), (x2,y2) = a,b
            return math.sqrt((x1-x2)**2 + (y1-y2)**2)

        def bin_search(coord, road):
            """Returns a length on the road `road` closest to `coord`

            This is a naive implementation of binary search with a fixed iteration count.
            """
            curr = road.get_length() / 2
            step = curr / 1.3
            for i in range(30):
                minor_dist = road.get_length() / 1000.0
                a = road.pos_to_coord(curr)
                b = road.pos_to_coord(curr+minor_dist)
                if dist(coord, a) < dist(coord, b):
                    curr -= step
                else:
                    curr += step
                step /= 1.3
            return curr

        start_at = 10
        l = [(start_at, bin_search(road_a.pos_to_coord(start_at), road_b)), (bin_search(road_b.pos_to_coord(start_at), road_a), start_at)]
        start = max(l)
        a_len = road_a.get_length()
        b_len = road_b.get_length()
        p1 = a_len, bin_search(road_a.pos_to_coord(a_len), road_b)
        p2 = bin_search(road_b.pos_to_coord(b_len), road_a), b_len
        end = min([p1, p2])

        def connect(from_pos, to_pos, from_road, to_road):
            from_coords = from_road.pos_to_coord(from_pos)
            to_coords = to_road.pos_to_coord(to_pos)

            # These points will be inserted to smooth out the adjacent road
            # mid = [from_road.pos_to_coord(from_pos+2), to_road.pos_to_coord(to_pos-2)]
            mid = []
            adjacent_road = self.add_road([from_coords] + mid + [to_coords])
            # print("Adding road from ({}) at {:.2f} to ({}) at {:.2f} with id {}".format(from_road, from_pos, to_road, to_pos, adjacent_road.get_id()))

            # Add the connections to the road
            from_road.add_connection(adjacent_road, at_length=from_pos)
            adjacent_road.add_connection(to_road, to_length=to_pos)

        i = 0
        while start[0]+con_dist < end[0] and start[1]+con_dist < end[1]:
            if i % 2 == 0:
                connect(start[0], start[1]+con_dist, from_road=road_a, to_road=road_b)
            else:
                connect(start[1], start[0]+con_dist, from_road=road_b, to_road=road_a)
                break
            i += 1
            start = (start[0]+con_dist+20, start[1]+con_dist+20)



    def get_roads(self):
        return self._roads


    def add_traffic_light(self, road, cycle, start_time=0, ry_phase_length=5, y_phase_length=3):
        """Adds a traffic light to the given road with a given cycle. Then returns it
        """
        tl = TrafficLight(cycle=cycle, start_time=start_time, ry_phase_length=ry_phase_length, y_phase_length=y_phase_length, road=road)
        road.add_entity(tl, at_length=road.get_length())
        return tl


    def add_destination(self, roads):
        """Adds a destination road_object to the given road and returns the destination

        Upon adding a destination it calculates the best possible path to each destination. 
        Therefore it is best not to change the intersection after adding destinations.

        Make sure to add destinations before you add spawners
        """
        if not isinstance(roads, list):
            roads = [roads]
        dest = Destination()
        for road in roads:
            road.add_connection(dest)
        self._roads.append(dest)
        self._destinations.append(dest)
        return dest


    def calculate_paths(self):
        """Calculates any possible path to go for each road_object
        """

        def rec_calc_curr_path(destination, curr_road, at_length, ignore_adjacent=False):
            if isinstance(curr_road, Destination):
                if destination is curr_road:
                    return True
                else:
                    return False
            elif isinstance(curr_road, Road):
                if destination in curr_road.path.keys() and curr_road.path[destination] is not None:
                    return True
                else:
                    if not curr_road.get_connections():
                        curr_road.path[destination] = None
                        return False
                    con_tuple = list(zip(*curr_road.get_connections()))
                    con_roads = con_tuple[0]
                    con_at_length = con_tuple[1]
                    con_to_length = con_tuple[2]
                    for index, con in enumerate(con_roads):
                        if ignore_adjacent and abs(con_at_length[index] - curr_road.get_length()) > 0.1:
                            continue
                        if con_at_length[index] >= at_length:
                            if rec_calc_curr_path(destination, con, con_to_length[index], ignore_adjacent=ignore_adjacent):
                                curr_road.path[destination] = index
                                return True
                    curr_road.path[destination] = None
                    return False

        for destination in self._destinations:
            # print(destination)
            for road in self._roads:
                # print("=======================")
                # print(road)
                rec_calc_curr_path(destination, road, 0, ignore_adjacent=True)
                rec_calc_curr_path(destination, road, 0)




    def add_spawner(self, road, distribution=None, average_time_for_next_car=40, name="lane_1", allowed=['pkw', 'lkw', 'bus']):
        """Adds a spawner before the given road with the given distribution.

        Distribution is a list of tuples of (Destination, chance) where Destination is a 
        Destination object and chance is a float. The chances will be normalized to add up to 100%.
        If left as None it will take the list of known Destinations with an uniform distribution. 
        Therefore make sure to add the spawners after adding the destinations if you want to use 
        that feature.
        """
        if distribution is None:
            distribution = [(dest, 1.0/len(self._destinations)) for dest in self._destinations]
        else:
            dest, nums = np.array(list(zip(*distribution)))
            nums = nums / nums.sum()
            distribution = list(zip(dest, nums))
        spawner = Spawner(road, distribution, options=self._options, average_time_for_next_car=average_time_for_next_car, name=name, allowed=allowed)
        self._roads.append(spawner)


    def add_road_object(self, road_object):
        """General function to add a road object to the intersection. Returns the same object
        """
        self._roads.append(road_object)
        return road_object

