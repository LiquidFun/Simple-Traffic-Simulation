class Entity:

    entity_id = 0

    def __init__(self):
        self._pos = 0
        self._vel = 0
        self._length = 0
        self._vel = 0
        self._updated = False
        Entity.entity_id += 1
        self._id = Entity.entity_id


    def set_pos(self, pos):
        self._pos = pos


    def reset_updated(self):
        self._updated = False


    def get_pos(self):
        return self._pos


    def get_length(self):
        return self._length


    def get_vel(self):
        return self._vel


    def get_id(self):
        return self._id
