import math

from .entity import Entity

class Car(Entity):
    """ car class for use in the simulator

    An options dictionary is required to set the cars attributes. It must contain these values:
        car_type + '_max_acc' (m/s^2) - maximum acceleration
        car_type + '_comf_dec' (m/s^2) - comfortable deceleration for braking
        car_type + '_time_dist' (s) - comfortable time distance to next car
        car_type + '_min_dist' (m) - minimum distance between cars
        car_type + '_des_vel' (m/s) - desired velocity to achieve for the car

    Note that this dictionary can be passed to every car and then by changing it once
    you change it for each car. If this is not expected behaviour then consider passing a 
    copy of that dictionary to each car (may need to be implemented yet).

    Each Car is described by a dictionary, i.e. this is the Car API:
        'velocity'   : double
        'position'   : double
        'coords'     : (double, double)
        'rotation'   : double (radians)
        'length'     : double
        'turn_signal': '' or 'left' or 'right'
        'braking'    : boolean
        'id'         : integer
    """

    def __init__(
            self, 
            pos=0, 
            options={},
            car_type="pkw",
            acc_exp=4,
            destination=None,
            random_factor=1
        ):
        super().__init__()

        self._vel = 0                   # m/s        : current velocity
        self._pos = pos                 # m          : current position

        self._ran_fac = random_factor

        self.destination = destination

        self._options = options
        self._car_type = car_type

        self._length = self._options[self._car_type+"_length"]

        self._acc_exp = acc_exp         #            : acceleration exponent

        self._next_car_vel = 0          # m/s        : velocity of next car (relative to ground)
        self._next_car_dist = 0         # m          : distance to next car (relative to current car)
        self._last_vel = 0              # m/s        : last velocity. Used for calculating if car is breaking

        self._last_step_size = 1

        self._turn_signal = ''

        self.prev_road = None


    def __str__(self):
        return "Car@{:.2f}|id:{}|type:{}|vel:{:.2f}km/h".format(self._pos, self._id, self._car_type, 3.6*self._vel)


    def __repr__(self):
        return self.__str__()


    def advance(self, step_size, next_car_dist, next_car_vel):
        if self._updated:
            return
        self._updated = True
        if next_car_dist < 0:
            return
        self._options[self._car_type+'_des_vel'] = max(1, self._options[self._car_type+'_des_vel'])
        self._next_car_dist = max(next_car_dist,1)
        self._next_car_vel = next_car_vel

        self._last_step_size = step_size

        self._last_vel = self._vel

        old_vel = self._vel
        self._vel = self._runge_kutta(self._idm_function, self._vel, step_size)
        self._pos += (old_vel+self._vel)/2 * step_size


    def _idm_s(self, v, deltaV):
        o = self._options
        t = self._car_type
        r = self._ran_fac
        end_part = ((v*deltaV) / (2*math.sqrt(r * o[t+'_max_acc'] * o[t+'_comf_dec'])))
        return o[t+'_min_dist']/r + max(0, v*o[t+'_time_dist'] + end_part)


    def _idm_function(self, vel):
        o = self._options
        t = self._car_type
        r = self._ran_fac
        app_rate = vel - self._next_car_vel   # m/s      : approach rate
        part1 = min(1000, (vel/(o[t+'_des_vel']*r)))**self._acc_exp
        part2 = (self._idm_s(vel, app_rate)/self._next_car_dist)**2
        v_dot = r * o[t+'_max_acc'] * (1 - part1 - part2)
        return v_dot


    def get_min_dist(self):
        o = self._options
        t = self._car_type
        r = self._ran_fac
        return o[t+'_min_dist']/r


    def get_api(self):
        # signal = {0 : 'right', 1 : '', 2 : 'left'}
        braking = True if self._last_vel - self._vel > 0*self._last_step_size else False
        return {
            'velocity'   : self._vel,
            'position'   : self._pos,
            'length'     : self._length,
            'type'       : self._car_type,
            'turn_signal': self._turn_signal,
            'braking'    : braking,
            'id'         : self._id,
        }

    def get_acc_max(self):
        o = self._options
        t = self._car_type
        r = self._ran_fac
        return r * o[t+'_acc_max']


    def set_turn_signal(self, turn_signal):
        self._turn_signal = turn_signal

    def _runge_kutta(self, function, var, step_size):
        k1 = step_size * (function(var))
        k2 = step_size * (function(var + k1/2))
        k3 = step_size * (function(var + k2/2))
        k4 = step_size * (function(var + k3))
        var_next = var + (1/6) * (k1 + 2*k2 + 2*k3 + k4)
        return max(0, var_next)

