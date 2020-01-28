from .road_object import RoadObject

class Abyss(RoadObject):

    def __init__(self):
        super().__init__()

    def update(self, step_size):
        pass

    def get_coords(self):
        return ((0,0),(0,0))

