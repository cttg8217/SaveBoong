from abc import *


class Building(metaclass=ABCMeta):
    def __init__(self, name, map_pos, type_id, level=1, is_upgrading=True, left_time=0):
        self.name = name
        self.map_pos = map_pos
        self.type_id = type_id
        self.level = level
        self.is_upgrading = is_upgrading
        self.left_time = left_time

    def set_upgrade(self):
        self.level += 1
        self.is_upgrading = True
        self.left_time = data[self.name]['upgrade_time'][self.level-1]

    def update_second(self):
        if self.is_upgrading:
            self.upgrade_second()
        else:
            self.action_second()

    def upgrade_second(self):
        self.left_time -= 1
        if self.left_time == 0:
            self.is_upgrading = False

    @abstractmethod
    def action_second(self):
        pass


class Hospital(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('병원', map_pos, 'hospital', level, is_upgrading, left_time)

    def action_second(self):
        pass


class School(Building):
    def __init__(self, map_pos, level=1, is_upgrading=True, left_time=0):
        super().__init__('학교', map_pos, 'school', level, is_upgrading, left_time)
        self.passed_seconds = 0
        self.graduates = 0

    def action_second(self):
        self.passed_seconds += 1
        if self.passed_seconds == 60:
            self.passed_seconds = 0

            new_graduates = data['School']['graduate_per_min'][self.level-1]
            self.graduates += new_graduates


data = {
    'Hospital': {
        'max_level': 4,
        'upgrade_price': [500, 600, 700, 800],
        'upgrade_time': [60, 90, 180, 240],
        'total_happiness': [25, 50, 100, 200],
    },
    'School': {
        'max_level': 2,
        'upgrade_price': [500, 1000],
        'upgrade_time': [90, 180],
        'total_happiness': [200, 400],
        'productivity_increase': [0.1, 0.2],
        'graduate_per_min': [10, 20],
    }
}
