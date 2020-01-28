from .entity import Entity

class TrafficLight(Entity):
    def __init__(self, pos=0, cycle=[("r",20),("g",20)], start_time=0, ry_phase_length=3, y_phase_length=5, road=None):
        super().__init__()

        self._cycle = [("",0)]
        for phase in cycle:
            curr_phase_time = phase[1]+self._cycle[-1][1]
            self._cycle.append((phase[0], curr_phase_time))
        #     if phase[0] == 'r':
        #         self._cycle.append(("ry", curr_phase_time+y_phase_length))
        #     if phase[0] == 'g':
        #         self._cycle.append(("y", curr_phase_time+ry_phase_length))

        self._pos = pos
        self._time = start_time
        self._phase = cycle[0][0]
        self._cycle_length = self._cycle[-1][1]
        self.road = road

        # print(self._time)
        # print(self._cycle_length)
        # print(self._cycle)
        # print()


    def __str__(self):
        return "TF@{}:id:{}!{}".format(round(self._pos,2), self._id, self._phase)


    def __repr__(self):
        return self.__str__()


    def get_sensor(self):
        return True if self.road.get_entities(after_length=self.road.get_length()-5, before_length=self.road.get_length()-1) else False


    def advance(self, step_size, a1=None, a2=None):
        self._time += step_size
        # print("time: {}\t--> phase: {}".format(round(self._time, 2), self._phase))
        for i in range(1,len(self._cycle)):
            if self._cycle[i-1][1] <= (self._time%self._cycle_length) < self._cycle[i][1]:
                self._phase = self._cycle[i][0]
                return

    def can_go(self):
        return self._phase == 'g'


    def get_api(self):
        return {
            'position':self._pos,
            'phase':self._phase,
            'id':self._id,
        }

    
    def get_phase(self):
        return self._phase


