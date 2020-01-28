from .road_object import RoadObject

class Destination(RoadObject):

    def __init__(self):
        super().__init__()

    def get_coords(self):
        return ((0,0),(0,0))

    def __str__(self):
        return "D{}".format(self._id)

    def __repr__(self):
        return self.__str__()

