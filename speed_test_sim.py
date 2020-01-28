import time

from Simulator.simulator import Simulator

# Change these variables for testing
step_size = 10/10
simulate_seconds = 24*3600
alert_step_size = 1




# Testing of simulator object creation
start_time = time.process_time()
s = Simulator()
print("creating simulator object took {} seconds".format(round(time.process_time()-start_time, 3)))

# Testing the simulation itself
simulation_time = 0
start_time = time.process_time()
next_alert = alert_step_size
while(True):
    s.update(step_size)
    #s.get_cars()
    simulation_time += step_size
    if time.process_time() > next_alert:
        print("simulation time: {}/{} seconds".format(round(simulation_time,3), simulate_seconds))
        next_alert += alert_step_size
    if simulation_time > simulate_seconds:
        print("{} seconds of simulation with a step size of {} took {} real time seconds".format(
            simulate_seconds,
            round(step_size, 3),
            round(time.process_time()-start_time, 3)
        ))
        break
    # s.show()
