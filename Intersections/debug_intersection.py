from Simulator.intersection import Intersection

def get_roads(options):
    inter = Intersection(options)

    top_out   = inter.add_road([(0.,20.),   (0.,40.)  ])
    top_out2   = inter.add_road([(8.,24.),   (40.,40.)  ])

    bot_in3   = inter.add_road([(-4.,-100.),  (-4.,10.) ])
    bot_in    = inter.add_road([(0.,-100.),  (0.,10.) ])
    bot_in2   = inter.add_road([(4.,-100.),  (4.,10.) ])

    inter.adjacent(bot_in, bot_in2)
    inter.adjacent(bot_in, bot_in3)

    red = 30
    green = 20
    # inter.add_traffic_light(bot_in,   [('r',red),('g',green)])

    connections = {
        bot_in : [top_out],
        bot_in2 : [top_out2],
    }
    for key, vals in connections.items():
        for val in vals:
            inter.add_road(start_road=key, end_road=val)

    top_dest = inter.add_destination(top_out)
    top_dest2 = inter.add_destination(top_out2)

    inter.add_spawner(bot_in3, [(top_dest, .8), (top_dest2, .2)], average_time_for_next_car=1)
    inter.add_spawner(bot_in2, [(top_dest, .4), (top_dest2, .6)], average_time_for_next_car=1)

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
