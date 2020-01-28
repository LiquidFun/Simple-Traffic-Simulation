from Simulator.intersection import Intersection

def get_roads(options):
    inter = Intersection(options)

    top_out   = inter.add_road([(3.,7.),   (3.,30.)  ])
    top_in1   = inter.add_road([(-3.,50.),  (-3.,10.) ])
    top_in2   = inter.add_road([(-7.,50.),  (-7.,10.) ])

    bot_out1  = inter.add_road([(-10.,-10.), (-10,-80.)])
    bot_out2  = inter.add_road([(-6.,-10.), (-6,-80.)])
    bot_in1   = inter.add_road([(3.,-80.),  (3.,-10.) ])
    bot_in2   = inter.add_road([(7.,-80.),  (7.,-10.) ])
    bot_in3   = inter.add_road([(11.,-80.),  (11.,-10.) ])

    left_out  = inter.add_road([(-15.,3.),  (-50.,3.) ])
    left_in   = inter.add_road([(-50.,-3.), (-15.,-3.)])

    right_out = inter.add_road([(15.,-3.),   (50.,-3.)  ])
    right_in  = inter.add_road([(50.,3.),  (15.,3.) ])

    inter.adjacent(bot_in1, bot_in2)
    inter.adjacent(bot_in2, bot_in3)
    inter.adjacent(top_in1, top_in2)
    # inter.adjacent(bot_out1, bot_out2)

    red = 30
    green = 20
    inter.add_traffic_light(top_in1,  [('r',red),('g',green)])
    inter.add_traffic_light(top_in2,  [('r',red),('g',green)])
    inter.add_traffic_light(bot_in1,  [('r',red),('g',green)])
    inter.add_traffic_light(bot_in2,  [('r',red),('g',green)])
    inter.add_traffic_light(bot_in3,  [('r',red),('g',green)])
    inter.add_traffic_light(right_in, [('g',green),('r',red)])
    inter.add_traffic_light(left_in,  [('g',green),('r',red)])

    connections = {
        top_in1: [bot_out2, right_out],
        top_in2: [left_out, bot_out1],
        bot_in1: [left_out],
        bot_in2: [top_out],
        bot_in3: [right_out],
        # bot_in2: [top_out],
        # bot_in3: [right_out],
        left_in: [top_out, bot_out1, right_out],
        right_in:[top_out, bot_out2, left_out],
    }
    for key, vals in connections.items():
        for val in vals:
            inter.add_road(start_road=key, end_road=val)

    bot_dest = inter.add_destination([bot_out1, bot_out2])
    top_dest = inter.add_destination(top_out)
    left_dest = inter.add_destination(left_out)
    right_dest = inter.add_destination(right_out)

    inter.add_spawner(bot_in1, [(top_dest, .1), (right_dest, .1), (left_dest, .5)], average_time_for_next_car=31)
    inter.add_spawner(bot_in2, [(top_dest, .6), (right_dest, .1), (left_dest, .1)], average_time_for_next_car=41)
    inter.add_spawner(bot_in3, [(top_dest, .2), (right_dest, .5), (left_dest, .1)], average_time_for_next_car=40)
    inter.add_spawner(top_in1, [(bot_dest, .5), (right_dest, .4), (left_dest, .1)], average_time_for_next_car=26)
    inter.add_spawner(top_in2, [(bot_dest, .5), (right_dest, .4), (left_dest, .1)], average_time_for_next_car=25)
    inter.add_spawner(right_in, [(bot_dest, .5), (top_dest, .4), (left_dest, .1)], average_time_for_next_car=80)
    inter.add_spawner(left_in, [(bot_dest, .5), (right_dest, .2), (top_dest, .3)], average_time_for_next_car=70)

    # Debug
    # for road in inter._roads:
    #     if isinstance(road, Road):
    #         print(road, end=' --> ')
    #         print(len(road.get_connections()))

    inter.calculate_paths()


    # for road in inter._roads:
    #     if isinstance(road, Road):
    #         print(road, end=' --> ')
    #         print(road.path)

    return inter.get_roads()
