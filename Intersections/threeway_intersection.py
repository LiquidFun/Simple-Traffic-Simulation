from Simulator.intersection import Intersection

def get_roads(options):
    inter = Intersection(options)

    bot_out   = inter.add_road([(-2.,-15.), (-3.,-60.)])
    bot_in    = inter.add_road([(3.,-60.),  (2.,-15.) ])

    left_out  = inter.add_road([(-7.,3.),  (-60.,50.) ])
    left_in   = inter.add_road([(-60.,46.), (-7.,-3.)])

    right_out = inter.add_road([(7.,-3.),   (60.,46.)])
    right_in  = inter.add_road([(60.,50.),  (7.,3.) ])

    red = 30
    ry=3
    y=3
    green = 20
    inter.add_traffic_light(bot_in,   [('r',red),('r',red),('g',green),])
    inter.add_traffic_light(right_in, [('r',red),('g',green),('r',red)])
    inter.add_traffic_light(left_in,  [('g',green),('r',red),('r',red),])

    connections = {
        bot_in : [right_out, left_out],
        right_in : [left_out, bot_out],
        left_in : [bot_out, right_out],
    }
    for key, vals in connections.items():
        for val in vals:
            inter.add_road(start_road=key, end_road=val)

    bot_dest = inter.add_destination(bot_out)
    left_dest = inter.add_destination(left_out)
    right_dest = inter.add_destination(right_out)

    inter.add_spawner(bot_in, [(right_dest, .1), (left_dest, .1)], average_time_for_next_car=20)
    inter.add_spawner(right_in, [(bot_dest, .5), (left_dest, .1)], average_time_for_next_car=80)
    inter.add_spawner(left_in, [(bot_dest, .5), (right_dest, .2),], average_time_for_next_car=70)

    inter.calculate_paths()

    # Debug
    # for road in inter._roads:
    #     if isinstance(road, Road):
    #         print(road, end=' --> ')
    #         print(len(road.get_connections()))

    # for road in inter._roads:
    #     if isinstance(road, Road):
    #         print(road, end=' --> ')
    #         print(road.path)

    return inter.get_roads()
