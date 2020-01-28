from Simulator.intersection import Intersection

def get_roads(options):
    inter = Intersection(options)

    top_out   = inter.add_road([(3.,7.),   (3.,30.)  ])
    top_in    = inter.add_road([(-3.,30.),  (-3.,7.) ])

    bot_out   = inter.add_road([(-3.,-7.), (-3.,-30.)])
    bot_in    = inter.add_road([(3.,-30.),  (3.,-7.) ])

    left_out  = inter.add_road([(-7.,3.),  (-30.,3.) ])
    left_in   = inter.add_road([(-30.,-3.), (-7.,-3.)])

    right_out = inter.add_road([(7.,-3.),   (30.,-3.)  ])
    right_in  = inter.add_road([(30.,3.),  (7.,3.) ])

    red = 30
    green = 20
    inter.add_traffic_light(top_in,   [('r',red),('g',green)])
    inter.add_traffic_light(bot_in,   [('r',red),('g',green)])
    inter.add_traffic_light(right_in, [('g',green),('r',red)])
    inter.add_traffic_light(left_in,  [('g',green),('r',red)])

    for i, road_in in enumerate([top_in, bot_in, left_in, right_in]):
        for j, road_out in enumerate([top_out, bot_out, left_out, right_out]):
            if i != j:
                inter.add_road(start_road=road_in, end_road=road_out)

    bot_dest = inter.add_destination(bot_out)
    top_dest = inter.add_destination(top_out)
    left_dest = inter.add_destination(left_out)
    right_dest = inter.add_destination(right_out)

    inter.add_spawner(bot_in, [(top_dest, .8), (right_dest, .1), (left_dest, .1)], average_time_for_next_car=20)
    inter.add_spawner(top_in, [(bot_dest, .5), (right_dest, .4), (left_dest, .1)], average_time_for_next_car=25)
    inter.add_spawner(right_in, [(bot_dest, .5), (top_dest, .4), (left_dest, .1)], average_time_for_next_car=80)
    inter.add_spawner(left_in, [(bot_dest, .5), (right_dest, .2), (top_dest, .3)], average_time_for_next_car=70)

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
