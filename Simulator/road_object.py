from abc import ABC, abstractmethod

class RoadObject:
    """RoadObject is used to implement a parent class for road, spawner, abyss and other types of roads.

    """

    ro_id = 0

    def __init__(self):
        self._id = RoadObject.ro_id
        RoadObject.ro_id += 1

    
    @abstractmethod
    def update(self, step_size):
        """Updates the respective object
        """
        pass


    @abstractmethod
    def get_coords(self):
        """Returns a tuple of 2 x,y coordinate tuples

        The first tuple is the start point, the second is the end point
        For example: ((0,10), (0,50))
        For RoadObjects which do not have a length this will return the same coordinate for both
        """
        pass


    @abstractmethod
    def trace_coords(self, dist=0.5):
        """Returns a list of coordinates along the road with a dist as distance between them

        Example:
        Returns [(-3.0, 10.0), (-3.0, 9.5), (-3.0, 9.0), (-3.0, 8.5), (-3.0, 8.0)]
        for a road from (-3, 10) to (-3, 8)
        """
        return []


    @abstractmethod
    def add_entity(self, entity, at_length=None):
        """Adds an entity to the current entity list

        """
        pass

    def reset_updated_status(self):
        pass

    def get_length(self):
        return 0

    def get_turn_signal(self):
        return ''


    def get_id(self):
        return self._id


    def get_entities(self, entity_class=None, after_length=0, before_length=None):
        return []
