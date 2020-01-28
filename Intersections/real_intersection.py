import sys

from Simulator.intersection import Intersection
from Simulator.helper_functions import verboseprint
from Simulator.road import Road
from Simulator.destination import Destination
from. import real_coordinates

def get_roads(options):

    car_types  = ['pkw', 'bus', 'lkw'] #same as spawner.py
    type_index = [0, 3, 1]
    lanes = [1,2,3,4]
    spawn_values = {
        #   pkw      lkw      -        bus      -
        1: [0.26166, 0.00361, 0.00138, 0.00194, 0.00166], 
        2: [0.02472, 0.00027, 0.0    , 0.0    , 0.0]    , 
        3: [0.19638, 0.00444, 0.00166, 0.00083, 0.00166], 
        4: [0.00666, 0.0    , 0.0    , 0.00138, 0.0]
    }
    #from Datenauswertung/read_data.py
    for lane in lanes:
        for index, car_type in enumerate(car_types):
            key = car_type + "_lane_" + str(lane)
            value = 4000
            if spawn_values[lane][type_index[index]] != 0:
                value = max(1, min(4000, 1 / spawn_values[lane][type_index[index]]))
            if key not in options:
                sys.exit("key {} not in options".format(key))
            # print(key, value)
            options[key] = value

    inter = Intersection(options)

    c = real_coordinates.get_coordinates()
    s1r = inter.add_road(c['s1r'])
    s1l = inter.add_road(c['s1l'])
    s1o = inter.add_road(c['s1o'][::-1])

    s2r = inter.add_road(c['s2r'])
    s2l = inter.add_road(c['s2l'])
    s2o = inter.add_road(c['s2o'][::-1])

    s3r = inter.add_road(c['s3r'])
    s3m = inter.add_road(c['s3m'])
    s3l = inter.add_road(c['s3l'])
    s3ol = inter.add_road(c['s3ol'][::-1])
    s3or = inter.add_road(c['s3or'][::-1])

    s4r = inter.add_road(c['s4r'])
    s4l = inter.add_road(c['s4l'])
    s4o = inter.add_road(c['s4o'][::-1])

    # inter.add_road(start_road=s3m, end_road=s3l, at_length=20)
    switch_at_length = 110
    switch_lane = Road([s3m.pos_to_coord(switch_at_length), s3m.pos_to_coord(switch_at_length+5), s3l.pos_to_coord(-5), s3l.pos_to_coord(0)], options=options, turn_signal='left')
    s3m.add_connection(switch_lane, switch_at_length)
    switch_lane.add_connection(s3l)
    inter._roads.append(switch_lane)

    # inter.adjacent(s1r, s1l)
    # inter.adjacent(s2r, s2l)
    # inter.adjacent(s3r, s3m)
    # # inter.adjacent(s3m, s3l)
    # inter.adjacent(s3ol, s3or)
    # inter.adjacent(s4r, s4l)

    #Schwachlastprogramm
    #c1 = [('r',34),('ry',1),('g',36),('y',3),('r',16)]
    #c2 = [('g',6),('y',3),('r',77),('ry',1),('g',3)]
    #c3 = [('r',14),('ry',1),('g',54),('y',3),('r',18)]
    #c4 = [('r',13),('ry',1),('g',11),('y',3),('r',62)]
    #c_bus = [('r',80),('g',5),('r',5)]

    #Früh-/Spätspitze
    c1 = [('r',39),('ry',1),('g',61),('y',3),('r',16)]
    c2 = [('g',11),('y',3),('r',103),('ry',1),('g',2)]
    c3 = [('r',19),('ry',1),('g',79),('y',3),('r',18)]
    c4 = [('r',13),('ry',1),('g',11),('y',3),('r',92)]
    c_bus = [('r',110),('g',5),('r',5)]

    #Grün
    # c1 = c2 = c3 = c4 = c_bus = [('g',1)]

    inter.add_traffic_light(s1r, c1)
    inter.add_traffic_light(s1l, c1)
    inter.add_traffic_light(s2r, c2)
    inter.add_traffic_light(s2l, c2)
    inter.add_traffic_light(s3r, c3)
    inter.add_traffic_light(s3m, c3)
    inter.add_traffic_light(s3l, c4)
    inter.add_traffic_light(s4r, c_bus)
    inter.add_traffic_light(s4l, c2)

    connections = {
                s1r: [s3or, s4o],
                s1l: [s2o, s3ol],
                s2r: [s1o],
                s2l: [s3ol,s4o],
                s3r: [s2o],
                s3m: [s1o],
                s3l: [s4o],
                s4r: [s2o, s3or, s1o],
                s4l: [s1o, s2o, s3or],
    }
    for key, vals in connections.items():
        for val in vals:
            inter.add_road(start_road=key, end_road=val)

    s1d = inter.add_destination(s1o)
    s2d = inter.add_destination(s2o)
    s3d = inter.add_destination([s3or, s3ol])
    s4d = inter.add_destination(s4o)

    # Print destinations
    for dest in [s1d, s2d, s3d, s4d]:
        verboseprint(1, "Destination added: {}".format(dest))
    
    #distribution (from K_0915.pdf)
    #Frühspitze
    ds1r = [(s4d, 5), (s3d, 882)]
    ds1l = [(s3d, 882), (s2d,86)]
    ds2r = [(s1d,63)]
    ds2l = [(s4d, 1), (s3d, 26)]
    ds3m = [(s4d, 3), (s1d,680)]
    ds3r = [(s2d, 55)]
    ds4 = [(s1d,12), (s2d, 5), (s3d, 12)]
    '''#Spätspitze
    ds1 = [(s2d,49), (s3d, 863), (s4d, 13)]
    ds2 = [(s1d,126), (s3d, 54), (s4d, 4)]
    ds3 = [(s1d,766), (s2d, 136), (s4d, 100)] # original 36, 10
    ds4 = [(s1d,16), (s2d, 6), (s3d, 7)]
    '''

    inter.add_spawner(s1r, ds1r, name='lane_1')
    inter.add_spawner(s1l, ds1l, name='lane_1')

    inter.add_spawner(s2r, ds2r, name='lane_2')
    inter.add_spawner(s2l, ds2l, name='lane_2')

    inter.add_spawner(s3r, ds3r, name='lane_3')
    inter.add_spawner(s3m, ds3m, name='lane_3')

    inter.add_spawner(s4l, ds4, name='lane_4', allowed=['pkw', 'lkw'])
    inter.add_spawner(s4r, ds4, name='lane_4', allowed=['bus'])

    # Debug
    # for road in inter._roads:
    #     if isinstance(road, Road):
    #         print(road, end=' --> ')
    #         print(len(road.get_connections()))

    inter.calculate_paths()

    inter.traffic_rules()

    # Debug (shows road IDS in the gui on the roads
    # log = []
    # for index, road in enumerate(inter.get_roads()):
    #     if isinstance(road, Road):
    #         x, y = road._curve.evaluate(0.9)
    #         log.append(((x[0],y[0]), str(index)))
    #     if isinstance(road, Destination):
    #         x, y = road.get_coords()[0]
    #         log.append(((x,y), str(index)))
    # options['debug_log'] = log

    # for road in inter._roads:
    #     if isinstance(road, Road):
    #         print(road, end=' --> ')
    #         print(road.path)

    return inter.get_roads()
